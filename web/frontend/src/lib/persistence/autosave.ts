import { get, writable, type Readable, type Writable } from 'svelte/store';
import type { CvDocuments } from '$lib/stores/documents';
import type { ActiveCvMeta } from '$lib/stores/cvSession';
import { updateCv as updateCvApi, type UpdateCvResult } from '$lib/api/cvs';

export type AutosaveStatus = 'saved' | 'saving' | 'retrying' | 'error' | 'conflict';

export interface AutosaveState {
	status: AutosaveStatus;
	/** Set only while `status === 'conflict'`: the server's current state, for the reconciliation bar. */
	conflict: { updatedAt: string; documents: CvDocuments } | null;
	/**
	 * Set only while `status === 'error'` for a failure that retrying cannot
	 * fix (the document is too large, or the CV no longer exists), so the UI
	 * can say what went wrong instead of offering a Retry that must fail.
	 */
	permanentError?: string;
}

export interface AutosaveBaseline {
	id: number;
	name: string;
	documents: CvDocuments;
	updatedAt: string;
}

export interface AutosaveControllerOptions {
	/** Idle time after the last documents/name change before a save is attempted. */
	debounceMs?: number;
	/** Delay before the single automatic retry after a failed (non-conflict) save. */
	retryDelayMs?: number;
	updateCv?: typeof updateCvApi;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
}

export interface AutosaveController {
	state: Writable<AutosaveState>;
	/**
	 * Establishes a new baseline (the CV just loaded into the `documents` /
	 * `activeCv` stores) without treating it as a dirty edit. Call this
	 * before or as part of switching to a different CV -- see
	 * `documentsEqual`'s note on subscription ordering.
	 */
	setBaseline: (baseline: AutosaveBaseline) => void;
	/** Awaits any in-flight save, then saves again if the stores are still dirty relative to the baseline. Used before switching CVs. */
	flush: () => Promise<void>;
	/** Best-effort, non-blocking save for `beforeunload` (uses `fetch(..., {keepalive: true})`; never awaited by the caller). */
	flushBeforeUnload: () => void;
	/** Resolves a `'conflict'` state: `'reload'` replaces the local documents with the server's current state; `'overwrite'` re-submits the local edit against the server's current `updatedAt`. */
	resolveConflict: (action: 'reload' | 'overwrite') => void;
	/** Manually retries after a surfaced `'error'`. */
	retryNow: () => void;
	destroy: () => void;
}

function initialState(): AutosaveState {
	return { status: 'saved', conflict: null };
}

function documentsEqual(a: CvDocuments, b: CvDocuments): boolean {
	return a.cv === b.cv && a.design === b.design && a.locale === b.locale && a.settings === b.settings;
}

/**
 * Wires the shared `documents` store and the active CV's name to
 * `PUT /api/cvs/{id}`: debounced (1500ms), serialized (never two in-flight;
 * a trailing edit during a save re-queues itself), with 409-conflict
 * reconciliation and a single automatic retry on failure before surfacing
 * an error (docs/plans/completed/cv-editor-web-app.md, Phase 4c).
 *
 * Why a standalone controller (same pattern as `renderController` /
 * `validateController` / `formSync`): every side effect (network, timers)
 * is injected, so this logic is unit-testable without mounting a component
 * or a real backend -- see `autosave.test.ts`.
 */
export function createAutosaveController(
	documentsSource: Readable<CvDocuments>,
	activeCvSource: Readable<ActiveCvMeta | null>,
	options: AutosaveControllerOptions = {}
): AutosaveController {
	const {
		debounceMs = 1500,
		retryDelayMs = 3000,
		updateCv = updateCvApi,
		setTimeoutFn = setTimeout,
		clearTimeoutFn = clearTimeout
	} = options;

	const state = writable<AutosaveState>(initialState());

	let baseline: AutosaveBaseline | null = null;
	let currentDocuments: CvDocuments | null = null;
	let currentMeta: ActiveCvMeta | null = null;

	let debounceTimer: ReturnType<typeof setTimeout> | null = null;
	let retryTimer: ReturnType<typeof setTimeout> | null = null;
	let retriedOnce = false;
	let inFlight = false;
	let queued = false;
	let currentSavePromise: Promise<void> | null = null;

	function isDirty(): boolean {
		if (!baseline || !currentMeta || !currentDocuments) return false;
		if (currentMeta.id !== baseline.id) return false; // a stale tick for a CV we've since switched away from
		return currentMeta.name !== baseline.name || !documentsEqual(currentDocuments, baseline.documents);
	}

	function scheduleSave(): void {
		if (get(state).status === 'conflict') return; // frozen until the user reconciles
		if (retryTimer) {
			clearTimeoutFn(retryTimer);
			retryTimer = null;
		}
		retriedOnce = false;
		if (debounceTimer) clearTimeoutFn(debounceTimer);
		debounceTimer = setTimeoutFn(() => {
			debounceTimer = null;
			trigger();
		}, debounceMs);
	}

	/** Runs `performSave`, tracking it on `currentSavePromise` so `flush()` can always await whichever save is currently on the wire. */
	function runSave(forceSeenUpdatedAt?: string, keepalive = false): Promise<void> {
		const p = performSave(forceSeenUpdatedAt, keepalive).finally(() => {
			if (currentSavePromise === p) currentSavePromise = null;
		});
		currentSavePromise = p;
		return p;
	}

	function trigger(): void {
		if (inFlight) {
			queued = true;
			return;
		}
		void runSave();
	}

	async function performSave(forceSeenUpdatedAt?: string, keepalive = false): Promise<void> {
		if (!baseline || !currentMeta || !currentDocuments) return;

		inFlight = true;
		state.set({ status: 'saving', conflict: null });

		const nameSnapshot = currentMeta.name;
		const docsSnapshot = currentDocuments;
		const cvId = baseline.id;
		const seenAt = forceSeenUpdatedAt ?? baseline.updatedAt;

		let result: UpdateCvResult;
		try {
			result = await updateCv(
				cvId,
				{ name: nameSnapshot, documents: docsSnapshot, seenUpdatedAt: seenAt },
				undefined,
				keepalive ? { keepalive: true } : {}
			);
		} catch {
			result = { ok: false, kind: 'error', message: 'Network error.' };
		}

		inFlight = false;

		// The active CV may have changed while this save was on the wire (switch,
		// delete, restore). This result belongs to the previous CV: reinstalling
		// its snapshot would clobber the new baseline -- permanently wedging
		// `isDirty()`'s id check, so every later edit looks clean and is never
		// saved -- and a conflict/error would be surfaced against a CV the user
		// has already left.
		if (baseline?.id !== cvId) {
			// A trailing edit queued while this stale save was on the wire belongs
			// to the CV that is open *now*, so run it rather than dropping it --
			// the queue is the only thing keeping that edit scheduled.
			if (queued) {
				queued = false;
				if (isDirty()) void runSave();
			}
			return;
		}

		if (result.ok) {
			baseline = { id: cvId, name: nameSnapshot, documents: docsSnapshot, updatedAt: result.updatedAt };
			retriedOnce = false;
			state.set({ status: 'saved', conflict: null });
			if (queued) {
				queued = false;
				if (isDirty()) void runSave();
			}
			return;
		}

		if (result.kind === 'conflict') {
			state.set({ status: 'conflict', conflict: result.current });
			return;
		}

		// 413 and 404 are deterministic: the identical payload will fail the same
		// way forever, so retrying only hides the cause behind a generic banner.
		if (result.kind === 'too-large' || result.kind === 'not-found') {
			state.set({
				status: 'error',
				conflict: null,
				permanentError:
					result.kind === 'too-large'
						? 'This CV is too large to save. Shorten it and your changes will save again.'
						: 'This CV no longer exists — it may have been deleted in another tab.'
			});
			return;
		}

		if (!retriedOnce) {
			retriedOnce = true;
			state.set({ status: 'retrying', conflict: null });
			retryTimer = setTimeoutFn(() => {
				retryTimer = null;
				void runSave();
			}, retryDelayMs);
		} else {
			state.set({ status: 'error', conflict: null });
		}
	}

	function setBaseline(next: AutosaveBaseline): void {
		if (debounceTimer) {
			clearTimeoutFn(debounceTimer);
			debounceTimer = null;
		}
		if (retryTimer) {
			clearTimeoutFn(retryTimer);
			retryTimer = null;
		}
		retriedOnce = false;
		queued = false;
		baseline = next;
		state.set({ status: 'saved', conflict: null });
	}

	async function flush(): Promise<void> {
		if (debounceTimer) {
			clearTimeoutFn(debounceTimer);
			debounceTimer = null;
		}
		if (retryTimer) {
			clearTimeoutFn(retryTimer);
			retryTimer = null;
		}
		// Awaiting a single save is not enough: its success handler starts the
		// queued follow-up save before this resumes, so wait until nothing is on
		// the wire. Starting one while `inFlight` would put two writes carrying
		// the same `seenUpdatedAt` in flight, and the loser would 409 -- showing
		// the user a conflict bar against their own save.
		while (currentSavePromise) await currentSavePromise;
		if (!inFlight && isDirty()) {
			await runSave();
		}
	}

	function flushBeforeUnload(): void {
		if (debounceTimer) {
			clearTimeoutFn(debounceTimer);
			debounceTimer = null;
		}
		if (inFlight) return; // a save is already on the wire; nothing more we can reliably do
		if (isDirty()) {
			void runSave(undefined, true);
		}
	}

	function resolveConflict(action: 'reload' | 'overwrite'): void {
		const conflictState = get(state);
		if (conflictState.status !== 'conflict' || !conflictState.conflict || !baseline) return;
		const current = conflictState.conflict;

		if (action === 'reload') {
			baseline = { id: baseline.id, name: baseline.name, documents: current.documents, updatedAt: current.updatedAt };
			// The caller is responsible for writing `current.documents` into the
			// shared `documents` store; once it does, the next subscription tick
			// will see the store matching the new baseline and stay clean.
			state.set({ status: 'saved', conflict: null });
			return;
		}

		// 'overwrite': keep the local edit, retry against the server's current updatedAt.
		void runSave(current.updatedAt);
	}

	function retryNow(): void {
		if (retryTimer) {
			clearTimeoutFn(retryTimer);
			retryTimer = null;
		}
		retriedOnce = false;
		void runSave();
	}

	const unsubscribeDocuments = documentsSource.subscribe((docs) => {
		currentDocuments = docs;
		if (isDirty()) scheduleSave();
	});
	const unsubscribeMeta = activeCvSource.subscribe((meta) => {
		currentMeta = meta;
		if (isDirty()) scheduleSave();
	});

	function destroy(): void {
		if (debounceTimer) clearTimeoutFn(debounceTimer);
		if (retryTimer) clearTimeoutFn(retryTimer);
		unsubscribeDocuments();
		unsubscribeMeta();
	}

	return { state, setBaseline, flush, flushBeforeUnload, resolveConflict, retryNow, destroy };
}

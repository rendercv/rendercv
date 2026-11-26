import { get, writable, type Writable } from 'svelte/store';
import type { CvDocuments, DocumentKey } from '$lib/stores/documents';
import {
	parseCvDocument,
	patchCvDocument,
	type ParseResult,
	type PatchResult
} from '$lib/api/documents';
import type { ValidationError } from '$lib/api/validate';
import { applyOp, collapseOps, type PatchOp } from './patchOps';

export type FormSyncStatus = 'idle' | 'loading' | 'ready' | 'error';

export interface FormSyncState {
	status: FormSyncStatus;
	/** The parsed `cv` document tree (`{cv: {...}}`, the full mapping incl. the top-level key). */
	data: Record<string, unknown> | null;
	/** Errors from the most recent (re)parse — a document that fails to parse has no usable form model. */
	errors: ValidationError[];
	/** The message from the most recent failed patch, for a toast; cleared on the next successful op. */
	toast: string | null;
}

export interface FormSyncOptions {
	/** Which of the four documents this controller tracks. Defaults to `'cv'` (the only tab Phase 2 wired up). */
	documentKey?: DocumentKey;
	/** Idle time after the last queued op before a patch request is sent. */
	debounceMs?: number;
	parse?: (yaml: string) => Promise<ParseResult>;
	patch?: (yaml: string, ops: PatchOp[]) => Promise<PatchResult>;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
}

export interface FormSyncController {
	state: Writable<FormSyncState>;
	/** Parses the store's current `cv` text into the form model and starts tracking it. Call when the YAML toggle turns OFF. */
	activate: () => Promise<void>;
	/** Stops re-parsing on external store changes (but keeps the last model cached). Call when the YAML toggle turns ON. */
	deactivate: () => void;
	/** Applies one op optimistically to the local form model, then queues it for the debounced patch request. */
	submitOp: (op: PatchOp) => void;
	/** Clears the current toast message (e.g. once the user has seen it). */
	dismissToast: () => void;
	/** Releases the store subscription and any pending timer. */
	destroy: () => void;
}

function initialState(): FormSyncState {
	return { status: 'idle', data: null, errors: [], toast: null };
}

/**
 * Wires the shared `documents` store to the form editor: parses `cv` into a
 * tree on activation, applies form edits as optimistic local updates plus
 * debounced, serialized `/api/documents/patch` calls, and recovers by
 * re-parsing whenever a patch is rejected or the YAML changes out from under
 * the form (e.g. an undo while in form mode) — see the ui-implementation
 * skill's "one store, two views" rule and the phase task's sync-engine spec.
 *
 * Why a standalone controller (same pattern as `renderController` /
 * `validateController`): every side effect (network, timers) is injected,
 * so the debounce/serialize/optimistic-update/recovery logic is unit
 * testable without mounting a component or a real backend.
 */
export function createFormSync(
	documents: Writable<CvDocuments>,
	options: FormSyncOptions = {}
): FormSyncController {
	const {
		documentKey = 'cv',
		debounceMs = 300,
		parse = parseCvDocument,
		patch = patchCvDocument,
		setTimeoutFn = setTimeout,
		clearTimeoutFn = clearTimeout
	} = options;

	const state = writable<FormSyncState>(initialState());

	let active = false;
	let pendingOps: PatchOp[] = [];
	let inFlight = false;
	let timer: ReturnType<typeof setTimeout> | null = null;
	/**
	 * The `cv` text we last parsed from or wrote to the store. Used to tell
	 * "the store changed because of our own write" (equal -> ignore) apart
	 * from "the store changed for some other reason, e.g. an undo" (not
	 * equal -> re-parse), without needing a transaction-tagging mechanism
	 * across the store boundary.
	 */
	let lastKnownCvYaml: string | null = null;

	function currentCvYaml(): string {
		return get(documents)[documentKey];
	}

	async function reparse(): Promise<void> {
		const yaml = currentCvYaml();
		state.update((s) => ({ ...s, status: 'loading' }));

		// A blank document (design/locale start this way — see the "minimal
		// YAML" approved semantics) is a valid empty state, not a parse
		// error: skip the network round trip and hand back an empty tree.
		if (yaml.trim() === '') {
			lastKnownCvYaml = yaml;
			state.set({ status: 'ready', data: {}, errors: [], toast: null });
			return;
		}


		const result: ParseResult = await parse(yaml);

		// The document may have been replaced while this parse was in
		// flight -- importing a CV writes twice in quick succession, the
		// empty CV the server just made and then the imported text. The
		// subscription below cannot pick the second one up while
		// `lastKnownCvYaml` is still null, so without this the change was
		// dropped and the form went on showing the document that is no
		// longer open. That is how an imported `engineeringresumes` design
		// was displayed as `classic`.
		if (currentCvYaml() !== yaml) {
			void reparse();
			return;
		}

		lastKnownCvYaml = yaml;
		if (result.ok) {
			state.set({ status: 'ready', data: result.data, errors: [], toast: null });
		} else {
			state.set({ status: 'error', data: null, errors: result.errors, toast: null });
		}
	}

	async function activate(): Promise<void> {
		active = true;
		await reparse();
	}

	function deactivate(): void {
		active = false;
	}

	function applyOptimistic(op: PatchOp): void {
		state.update((s) => (s.data ? { ...s, data: applyOp(s.data, op) as Record<string, unknown> } : s));
	}

	function submitOp(op: PatchOp): void {
		applyOptimistic(op);
		pendingOps.push(op);
		scheduleFlush();
	}

	function scheduleFlush(): void {
		if (timer) clearTimeoutFn(timer);
		timer = setTimeoutFn(() => {
			timer = null;
			void flush();
		}, debounceMs);
	}

	async function flush(): Promise<void> {
		// Never two in-flight: if a patch is already running, do nothing here
		// -- its own completion (below) re-checks pendingOps and flushes again.
		if (inFlight || pendingOps.length === 0) return;

		const ops = collapseOps(pendingOps);
		pendingOps = [];
		inFlight = true;

		const yamlSnapshot = currentCvYaml();
		// The patch endpoint's YAML parser treats a genuinely empty document as
		// an error (there's nothing to round-trip), but a blank document is a
		// valid starting point here (design/locale start this way -- the
		// "minimal YAML" approved semantics) and the very first write on one
		// needs somewhere to land: `{}` is a valid empty mapping the backend
		// can parse and then populate via the ops, same as any other document.
		const patchableYaml = yamlSnapshot.trim() === '' ? '{}' : yamlSnapshot;
		const result = await patch(patchableYaml, ops);
		inFlight = false;

		if (result.ok) {
			lastKnownCvYaml = result.yaml;
			documents.update((docs) => ({ ...docs, [documentKey]: result.yaml }));
			state.update((s) => ({ ...s, toast: null }));
		} else {
			const message =
				result.kind === 'op-error'
					? result.error.message
					: (result.errors[0]?.message ?? 'Could not save that change.');
			await reparse(); // recover from the authoritative YAML; never diverge silently
			state.update((s) => ({ ...s, toast: message })); // reparse() clears toast, so set it after
		}

		if (pendingOps.length > 0) void flush();
	}

	function dismissToast(): void {
		state.update((s) => ({ ...s, toast: null }));
	}

	// External changes to the cv document (YAML-mode edits, undo/redo, a
	// freshly loaded CV) must re-render the form. We only react while
	// active, and only when the change isn't just our own write landing
	// (lastKnownCvYaml) or a write we're already mid-flight/queued for
	// (which will update lastKnownCvYaml itself once it lands).
	const unsubscribe = documents.subscribe((docs) => {
		if (!active) return;
		if (lastKnownCvYaml === null) return;
		if (docs[documentKey] === lastKnownCvYaml) return;
		if (inFlight || pendingOps.length > 0) return;
		void reparse();
	});

	function destroy(): void {
		unsubscribe();
		if (timer) {
			// Flush any queued-but-not-yet-sent edits immediately instead of
			// silently dropping them. Why this matters: the YAML toggle
			// unmounts the form the instant a user switches back to YAML mode,
			// which can easily happen inside the 300ms debounce window right
			// after an edit -- without this, that edit would vanish instead of
			// ever reaching `/api/documents/patch`. The resulting write lands
			// on the shared `documents` store (not on this controller's own
			// `state`), so it's safe to let it finish after this call returns.
			clearTimeoutFn(timer);
			timer = null;
			void flush();
		}
	}

	return { state, activate, deactivate, submitOp, dismissToast, destroy };
}

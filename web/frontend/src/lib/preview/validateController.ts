import { writable, type Readable, type Writable } from 'svelte/store';
import type { CvDocuments } from '$lib/stores/documents';
import { validateDocuments, type ValidateResult, type ValidationError } from '$lib/api/validate';

export interface ValidationState {
	/** True once at least one validation round-trip has completed. */
	checked: boolean;
	errors: ValidationError[];
}

export interface DocumentSource {
	subscribe: Readable<CvDocuments>['subscribe'];
}

export interface ValidateControllerOptions {
	/** Idle time after the last document change before validation is triggered. */
	debounceMs?: number;
	validate?: (docs: CvDocuments) => Promise<ValidateResult>;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
	/** If true, the controller does not subscribe to `source` until `activate()` is called -- see `RenderControllerOptions.startPaused` for why. Defaults to `false`. */
	startPaused?: boolean;
}

export interface ValidateController {
	state: Writable<ValidationState>;
	/** Starts reacting to `source` (scheduling a validation for its current value). No-op if already active; only relevant when created with `startPaused: true`. */
	activate: () => void;
	destroy: () => void;
}

function initialState(): ValidationState {
	return { checked: false, errors: [] };
}

/**
 * Wires a CV-documents store to `/api/validate`: debounced on every change,
 * on the same ~800ms cadence as the preview render (see
 * `createRenderController`), so inline error placement (line/tab) has an
 * authoritative source independent of whether a PDF could also be rendered.
 *
 * Why a standalone controller: same reasoning as `renderController` — the
 * plan requires this sync/debounce logic be unit-testable without mounting
 * Svelte components or a real backend.
 */
export function createValidateController(
	source: DocumentSource,
	options: ValidateControllerOptions = {}
): ValidateController {
	const {
		debounceMs = 800,
		validate = validateDocuments,
		setTimeoutFn = setTimeout,
		clearTimeoutFn = clearTimeout,
		startPaused = false
	} = options;

	const state = writable<ValidationState>(initialState());

	let timer: ReturnType<typeof setTimeout> | null = null;
	let token = 0;

	async function runValidate(docs: CvDocuments): Promise<void> {
		const current = ++token;
		const result = await validate(docs);
		if (current !== token) return; // a newer validation started; drop this one

		state.set({ checked: true, errors: result.ok ? [] : result.errors });
	}

	function scheduleValidate(docs: CvDocuments): void {
		if (timer) clearTimeoutFn(timer);
		timer = setTimeoutFn(() => {
			timer = null;
			void runValidate(docs);
		}, debounceMs);
	}

	let unsubscribe: (() => void) | null = null;

	function activate(): void {
		if (unsubscribe) return; // already active
		unsubscribe = source.subscribe((docs) => {
			scheduleValidate(docs);
		});
	}

	if (!startPaused) activate();

	function destroy(): void {
		if (timer) clearTimeoutFn(timer);
		unsubscribe?.();
	}

	return { state, activate, destroy };
}

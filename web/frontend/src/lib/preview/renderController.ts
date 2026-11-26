import { writable, type Readable, type Writable } from 'svelte/store';
import type { CvDocuments } from '$lib/stores/documents';
import { renderPreview, type RenderResult, type ValidationError } from '$lib/api/render';
import { isWasmPreviewEnabled } from '$lib/wasm/featureFlag';

export type PreviewStatus = 'idle' | 'pending' | 'success' | 'error';

export interface PreviewState {
	status: PreviewStatus;
	/** The last successfully rendered blob: URL, kept visible while a newer render is invalid. */
	url: string | null;
	errors: ValidationError[];
	hasRenderedOnce: boolean;
	/** Which path produced the currently-showing (or currently pending) render. */
	renderedBy: 'server' | 'client';
}

export interface DocumentSource {
	subscribe: Readable<CvDocuments>['subscribe'];
}

/**
 * The in-browser (Pyodide + typst.ts) render path, injected into the
 * controller so it stays unit-testable with a fake instead of real wasm.
 *
 * Why `isReady()` is synchronous and polled rather than a single startup
 * Promise: the engine's readiness can change over the page's lifetime (it
 * starts loading in the background and becomes ready some seconds later,
 * independent of when any particular render is requested), so the
 * controller needs to check it fresh on every render, not just once at
 * construction.
 */
export interface ClientRenderEngine {
	/** True once the engine has finished loading (wheel installed, compiler initialized) and can accept `render()` calls. */
	isReady(): boolean;
	/**
	 * Compiles the four documents to a PDF entirely client-side.
	 *
	 * Must reject (not resolve an error result) on any failure -- the
	 * controller treats a rejection as "fall back to the server for this
	 * render", matching the plan's "server render stays canonical" rule.
	 * Client-side validation errors are intentionally not surfaced; the
	 * server render (or the parallel `/api/validate` debounce) remains the
	 * source of truth for error content.
	 */
	render(docs: CvDocuments): Promise<Blob>;
}

export interface RenderControllerOptions {
	/** Idle time after the last document change before a render is triggered. */
	debounceMs?: number;
	render?: (docs: CvDocuments) => Promise<RenderResult>;
	createObjectURL?: (blob: Blob) => string;
	revokeObjectURL?: (url: string) => void;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
	/**
	 * If true, the controller does not subscribe to `source` (and so cannot
	 * fire a render) until `activate()` is called.
	 *
	 * Why: a caller that seeds `source` asynchronously (e.g. an app bootstrap
	 * that replaces a placeholder document with a freshly loaded one) would
	 * otherwise have this controller react to the placeholder the instant
	 * it's created, firing a real network render for content nobody will
	 * ever see -- and, worse, letting that stale render's blob URL satisfy
	 * an "a preview is showing" check before the real content has rendered
	 * at all. Defaults to `false` (subscribes immediately, matching every
	 * caller before this option existed).
	 */
	startPaused?: boolean;
	/**
	 * The optional client-side (wasm) render engine. When provided, and
	 * `clientRenderEnabled()` reports true, and the engine reports ready,
	 * debounced renders are attempted client-side first; any failure or
	 * timeout for that render falls back to `render()` (the server path).
	 */
	clientRenderEngine?: ClientRenderEngine;
	/**
	 * Reads the feature flag. Defaults to `isWasmPreviewEnabled()`
	 * (localStorage, off by default). Injectable so tests don't need to
	 * touch real browser storage.
	 */
	clientRenderEnabled?: () => boolean;
	/** How long a client render is given before it's treated as a failure and the server path is used instead. */
	clientRenderTimeoutMs?: number;
	/** Consecutive client-render failures (errors or timeouts) after which the engine is flagged unhealthy and skipped for the rest of this controller's lifetime. */
	clientRenderMaxConsecutiveFailures?: number;
}

export interface RenderController {
	state: Writable<PreviewState>;
	/** Renders immediately, bypassing the debounce (used by an explicit "Render" button). */
	renderNow: (docs: CvDocuments) => void;
	/** Starts reacting to `source` (scheduling a render for its current value). No-op if already active; only relevant when created with `startPaused: true`. */
	activate: () => void;
	/** Stops listening to the document source and revokes any outstanding blob URL. */
	destroy: () => void;
}

function initialState(): PreviewState {
	return { status: 'idle', url: null, errors: [], hasRenderedOnce: false, renderedBy: 'server' };
}

/** Rejects with a timeout error if `promise` doesn't settle within `ms`. */
function withTimeout<T>(
	promise: Promise<T>,
	ms: number,
	setTimeoutFn: typeof setTimeout,
	clearTimeoutFn: typeof clearTimeout
): Promise<T> {
	return new Promise<T>((resolve, reject) => {
		const timer = setTimeoutFn(() => reject(new Error('client render timed out')), ms);
		promise.then(
			(value) => {
				clearTimeoutFn(timer);
				resolve(value);
			},
			(err) => {
				clearTimeoutFn(timer);
				reject(err);
			}
		);
	});
}

/**
 * Wires a CV-documents store to `/api/render`: debounced auto-render on every
 * change, with the last good PDF kept visible while newer input is invalid.
 *
 * Why a standalone controller instead of component-local logic: this is the
 * "sync logic" the plan requires be unit-tested without mounting Svelte
 * components or a real backend -- every side effect (fetch, timers, blob URL
 * creation) is injected.
 */
export function createRenderController(
	source: DocumentSource,
	options: RenderControllerOptions = {}
): RenderController {
	const {
		debounceMs = 800,
		render = renderPreview,
		createObjectURL = (blob: Blob) => URL.createObjectURL(blob),
		revokeObjectURL = (url: string) => URL.revokeObjectURL(url),
		setTimeoutFn = setTimeout,
		clearTimeoutFn = clearTimeout,
		startPaused = false,
		clientRenderEngine,
		clientRenderEnabled = isWasmPreviewEnabled,
		clientRenderTimeoutMs = 4000,
		clientRenderMaxConsecutiveFailures = 3
	} = options;

	const state = writable<PreviewState>(initialState());

	let timer: ReturnType<typeof setTimeout> | null = null;
	let currentUrl: string | null = null;
	let renderToken = 0;

	let clientConsecutiveFailures = 0;
	let clientEngineUnhealthy = false;

	function clientEngineUsable(): boolean {
		return (
			!!clientRenderEngine &&
			!clientEngineUnhealthy &&
			clientRenderEnabled() &&
			clientRenderEngine.isReady()
		);
	}

	async function runRender(docs: CvDocuments): Promise<void> {
		const token = ++renderToken;
		state.update((s) => ({ ...s, status: 'pending' }));

		// Why an `if/else` rather than an always-`await`ed helper: when there is
		// no usable client engine, `clientEngineUsable()` is a synchronous
		// boolean check, so the server `render(docs)` call below happens in the
		// same microtask as the debounce firing -- exactly like before this
		// engine option existed. Routing every render through an intermediate
		// `async` helper (even one that resolves instantly) would insert an
		// extra microtask tick before `render(docs)` is invoked, which is
		// invisible in production but changes the synchronous-call assumption
		// the "pending status" test above relies on.
		let usedClient = false;
		let result: RenderResult;
		if (clientEngineUsable()) {
			try {
				const blob = await withTimeout(
					clientRenderEngine!.render(docs),
					clientRenderTimeoutMs,
					setTimeoutFn,
					clearTimeoutFn
				);
				clientConsecutiveFailures = 0;
				usedClient = true;
				result = { ok: true, blob };
			} catch {
				clientConsecutiveFailures += 1;
				if (clientConsecutiveFailures >= clientRenderMaxConsecutiveFailures) {
					clientEngineUnhealthy = true;
				}
				result = await render(docs);
			}
		} else {
			result = await render(docs);
		}
		if (token !== renderToken) return; // a newer render started while this one was in flight

		if (result.ok) {
			const nextUrl = createObjectURL(result.blob);
			const staleUrl = currentUrl;
			currentUrl = nextUrl;
			state.set({
				status: 'success',
				url: nextUrl,
				errors: [],
				hasRenderedOnce: true,
				renderedBy: usedClient ? 'client' : 'server'
			});
			if (staleUrl) revokeObjectURL(staleUrl);
		} else {
			state.update((s) => ({
				status: 'error',
				url: s.url,
				errors: result.errors,
				hasRenderedOnce: s.hasRenderedOnce,
				renderedBy: s.renderedBy
			}));
		}
	}

	function scheduleRender(docs: CvDocuments): void {
		if (timer) clearTimeoutFn(timer);
		timer = setTimeoutFn(() => {
			timer = null;
			void runRender(docs);
		}, debounceMs);
	}

	let unsubscribe: (() => void) | null = null;

	function activate(): void {
		if (unsubscribe) return; // already active
		unsubscribe = source.subscribe((docs) => {
			scheduleRender(docs);
		});
	}

	if (!startPaused) activate();

	function renderNow(docs: CvDocuments): void {
		if (timer) {
			clearTimeoutFn(timer);
			timer = null;
		}
		void runRender(docs);
	}

	function destroy(): void {
		if (timer) clearTimeoutFn(timer);
		unsubscribe?.();
		if (currentUrl) revokeObjectURL(currentUrl);
	}

	return { state, renderNow, activate, destroy };
}

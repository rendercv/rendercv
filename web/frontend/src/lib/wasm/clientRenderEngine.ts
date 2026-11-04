import type { ClientRenderEngine } from '$lib/preview/renderController';
import type { CvDocuments } from '$lib/stores/documents';
import type { WasmEngineRequest, WasmEngineResponse } from './protocol';

interface PendingRender {
	resolve: (blob: Blob) => void;
	reject: (err: Error) => void;
}

/**
 * Main-thread handle to the client-side (Pyodide + typst.ts) preview
 * engine: spawns `engine.worker.ts`, starts it loading immediately, and
 * implements the `ClientRenderEngine` interface `renderController` expects
 * (see that file for the selection/fallback logic that lives on the other
 * side of this interface).
 *
 * Why a class instead of exposing the worker directly: `renderController`
 * needs a synchronous `isReady()` it can poll on every debounced render
 * (the worker's own loading is asynchronous and can take several seconds),
 * plus request/response correlation for `render()` -- both are bookkeeping
 * a raw `postMessage` API doesn't give you.
 */
export class WasmRenderEngine implements ClientRenderEngine {
	private readonly worker: Worker;
	private ready = false;
	private nextRequestId = 1;
	private readonly pending = new Map<number, PendingRender>();

	constructor(workerFactory: () => Worker = WasmRenderEngine.defaultWorkerFactory) {
		this.worker = workerFactory();
		this.worker.onmessage = (event: MessageEvent<WasmEngineResponse>) => {
			this.handleMessage(event.data);
		};
		this.postToWorker({ type: 'init' });
	}

	private static defaultWorkerFactory(): Worker {
		return new Worker(new URL('./engine.worker.ts', import.meta.url), { type: 'module' });
	}

	private postToWorker(message: WasmEngineRequest): void {
		this.worker.postMessage(message);
	}

	private handleMessage(message: WasmEngineResponse): void {
		if (message.type === 'ready') {
			this.ready = true;
			return;
		}
		if (message.type === 'init-error') {
			// The engine never becomes ready; `isReady()` stays false forever,
			// so `renderController` simply never selects the client path --
			// no separate "failed" state to track here.
			return;
		}
		if (message.type === 'render-result') {
			const pending = this.pending.get(message.requestId);
			if (!pending) return; // no one is awaiting this (e.g. after dispose())
			this.pending.delete(message.requestId);
			if (message.ok) {
				// `.slice()` copies into a fresh `ArrayBuffer` (never a
				// `SharedArrayBuffer`), which is what `BlobPart` requires --
				// the postMessage-transferred `Uint8Array`'s buffer type is too
				// loose (`ArrayBufferLike`) for TS to accept directly here.
				pending.resolve(new Blob([message.pdf.slice()], { type: 'application/pdf' }));
			} else {
				pending.reject(new Error(message.message));
			}
		}
	}

	isReady(): boolean {
		return this.ready;
	}

	render(docs: CvDocuments): Promise<Blob> {
		if (!this.ready) {
			return Promise.reject(new Error('wasm render engine is not ready'));
		}
		const requestId = this.nextRequestId++;
		return new Promise<Blob>((resolve, reject) => {
			this.pending.set(requestId, { resolve, reject });
			this.postToWorker({ type: 'render', requestId, docs });
		});
	}

	/** Terminates the worker and rejects any renders still in flight. */
	dispose(): void {
		for (const pending of this.pending.values()) {
			pending.reject(new Error('wasm render engine disposed'));
		}
		this.pending.clear();
		this.worker.terminate();
	}
}

/**
 * Creates the engine if this is a browser environment capable of running
 * it (a `Worker` global is available), otherwise returns `null`.
 *
 * Why: the render controller and this module are imported from
 * `+page.svelte`, which SvelteKit also runs during SSR/prerendering, where
 * `Worker` doesn't exist. Callers should only wire this into
 * `createRenderController`'s `clientRenderEngine` option when this returns
 * non-null.
 */
export function createWasmRenderEngineIfSupported(): WasmRenderEngine | null {
	if (typeof Worker === 'undefined') return null;
	return new WasmRenderEngine();
}

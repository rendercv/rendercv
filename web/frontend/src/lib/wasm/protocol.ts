import type { CvDocuments } from '$lib/stores/documents';

/** Messages the main thread sends to the engine worker. */
export type WasmEngineRequest =
	| { type: 'init' }
	| { type: 'render'; requestId: number; docs: CvDocuments };

/** Messages the engine worker sends back to the main thread. */
export type WasmEngineResponse =
	| { type: 'ready' }
	| { type: 'init-error'; message: string }
	| { type: 'render-result'; requestId: number; ok: true; pdf: Uint8Array }
	| { type: 'render-result'; requestId: number; ok: false; message: string };

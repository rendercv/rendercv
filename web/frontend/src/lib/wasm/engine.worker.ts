/// <reference lib="webworker" />

// The client-side (Pyodide + typst.ts) preview engine, running entirely in
// this dedicated worker so a multi-second Pyodide/typst.ts cold start and
// CPU-bound compiles never block the main thread or the form/YAML editors.
//
// Protocol: see `./protocol.ts`. One `init` message starts loading (fetching
// the manifest, then Pyodide + the rendercv wheel and the typst.ts compiler
// + bundled packages/fonts, in parallel); the worker then replies `ready` or
// `init-error` exactly once. Each `render` message is answered by exactly
// one `render-result` (ok or not), correlated by `requestId` so the main
// thread can safely have more than one in flight (though the render
// controller only ever sends one at a time in practice).

import { loadWasmManifest } from './manifest';
import { createPyodideEngine, type PyodideEngineHandle } from './pyodideEngine';
import { createBrowserTypstCompiler, type TypstCompilerHandle } from './typstCompiler';
import type { WasmEngineRequest, WasmEngineResponse } from './protocol';

const ctx = self as unknown as DedicatedWorkerGlobalScope;

let pyodideEngine: PyodideEngineHandle | null = null;
let typstCompiler: TypstCompilerHandle | null = null;
let initPromise: Promise<void> | null = null;

function post(message: WasmEngineResponse, transfer: Transferable[] = []): void {
	ctx.postMessage(message, transfer);
}

async function init(): Promise<void> {
	const baseUrl = ctx.location.origin;
	const manifest = await loadWasmManifest(baseUrl);

	const [pyodide, typst] = await Promise.all([
		createPyodideEngine(`${baseUrl}/wasm/${manifest.wheel}`),
		createBrowserTypstCompiler(manifest, baseUrl)
	]);
	pyodideEngine = pyodide;
	typstCompiler = typst;
}

ctx.onmessage = async (event: MessageEvent<WasmEngineRequest>) => {
	const message = event.data;

	if (message.type === 'init') {
		if (!initPromise) initPromise = init();
		try {
			await initPromise;
			post({ type: 'ready' });
		} catch (err) {
			post({ type: 'init-error', message: err instanceof Error ? err.message : String(err) });
		}
		return;
	}

	if (message.type === 'render') {
		const { requestId } = message;
		try {
			if (!pyodideEngine || !typstCompiler) {
				throw new Error('render requested before the engine finished initializing');
			}
			const typSource = await pyodideEngine.buildTypstSource(message.docs);
			const pdf = await typstCompiler.compileToPdf(typSource);
			post({ type: 'render-result', requestId, ok: true, pdf }, [pdf.buffer]);
		} catch (err) {
			post({
				type: 'render-result',
				requestId,
				ok: false,
				message: err instanceof Error ? err.message : String(err)
			});
		}
	}
};

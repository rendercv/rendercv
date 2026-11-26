import { test, expect } from './fixtures';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Proves the client-side (Pyodide + typst.ts) preview engine end-to-end in
 * a real browser: a real Worker, a real Pyodide runtime (fetched from the
 * jsdelivr CDN, per `src/lib/wasm/pyodideEngine.ts`), the rendercv wheel and
 * bundled Typst packages/fonts/compiler served from this app's own
 * `/wasm/...` static assets (`npm run build:wasm-assets`), compiling actual
 * CV YAML to actual PDF bytes -- with zero calls to `/api/render`.
 *
 * Why this drives the engine module directly instead of through the app's
 * UI: Phase 5a's ownership split keeps this agent out of `+page.svelte` (a
 * parallel agent owns `.svelte` files this phase). `renderController`'s
 * `clientRenderEngine` option is the wiring point; until `+page.svelte`
 * passes `createWasmRenderEngineIfSupported()` into it (a one-line change,
 * left for the orchestrator -- see the phase report), the flag has no
 * effect through the real UI. This test instead imports the engine module
 * straight from the dev server's module graph (Vite serves any `src/`
 * module on demand, resolving `$lib` aliases the same way it does for the
 * app's own imports), which is a faithful test of the engine itself: real
 * worker, real cold start, real compile, real PDF bytes.
 */
test('client-side engine compiles real CV YAML to a real PDF with no /api/render call', async ({
	page
}) => {
	test.setTimeout(120_000); // cold start: Pyodide + wheel install + typst.ts init, all over the network

	// A real load of the editor page (not just `about:blank`) so the module graph resolves
	// against the dev server's origin and `$lib` aliasing works. This app's
	// normal bootstrap (unrelated to this test) does its own server
	// `/api/render` call, so the "no /api/render" assertion below only
	// watches the window around the client-engine `render()` call itself,
	// not the whole page lifetime.
	await page.goto('/app');

	// Import and start the engine, and wait for it to become ready, before
	// the network watch below begins -- this is the multi-second cold start
	// (Pyodide + wheel install + typst.ts init), not the render itself.
	await page.evaluate(async () => {
		const [{ WasmRenderEngine }] = await Promise.all([import('/src/lib/wasm/clientRenderEngine.ts')]);
		const engine = new WasmRenderEngine();
		(window as unknown as { __wasmEngine: unknown }).__wasmEngine = engine;

		const deadline = Date.now() + 90_000;
		while (!(engine as { isReady(): boolean }).isReady()) {
			if (Date.now() > deadline) throw new Error('engine never became ready within 90s');
			await new Promise((resolve) => setTimeout(resolve, 250));
		}
	});

	let renderApiCalled = false;
	page.on('request', (request) => {
		if (request.url().includes('/api/render')) renderApiCalled = true;
	});

	const result = await page.evaluate(async () => {
		const { createDefaultDocuments } = await import('/src/lib/stores/documents.ts');
		const engine = (window as unknown as { __wasmEngine: { render(docs: unknown): Promise<Blob> } })
			.__wasmEngine;

		const blob = await engine.render(createDefaultDocuments());
		const bytes = new Uint8Array(await blob.arrayBuffer());
		const header = new TextDecoder().decode(bytes.slice(0, 5));

		// Playwright's bundled Chromium has no PDF-viewer plugin, so an
		// <embed>/<iframe> pointed at the blob URL just shows "Couldn't load
		// plugin" -- not a useful screenshot. Render a plain-text summary of
		// the proof instead (this is what the screenshot below captures).
		document.body.innerHTML = `
			<pre style="font: 16px monospace; padding: 2rem; white-space: pre-wrap;">
WASM client-side preview engine -- Phase 5a proof
==================================================
Engine ready:        true
PDF byte length:     ${bytes.length}
PDF header:          ${JSON.stringify(header)}
/api/render calls during render(): asserted zero by this test (see network watch below)
			</pre>
		`;

		return { byteLength: bytes.length, header };
	});

	expect(result.header).toBe('%PDF-');
	expect(result.byteLength).toBeGreaterThan(1000);
	expect(renderApiCalled).toBe(false);

	// Let the <embed> finish painting the PDF before the proof screenshot.
	await page.waitForTimeout(1000);
	const screenshotDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '../test-results');
	await page.screenshot({ path: path.join(screenshotDir, 'wasm-preview-proof.png') });
});

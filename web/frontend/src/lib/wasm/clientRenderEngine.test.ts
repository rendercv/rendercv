import { describe, it, expect } from 'vitest';
import { WasmRenderEngine } from './clientRenderEngine';
import type { WasmEngineRequest, WasmEngineResponse } from './protocol';
import type { CvDocuments } from '$lib/stores/documents';

/**
 * A fake `Worker` that records every message posted to it and lets the test
 * drive responses back, without spinning up a real Worker (unavailable in
 * the Vitest node environment anyway) or touching Pyodide/typst.ts.
 */
class FakeWorker {
	posted: WasmEngineRequest[] = [];
	onmessage: ((event: MessageEvent<WasmEngineResponse>) => void) | null = null;
	terminated = false;

	postMessage(message: WasmEngineRequest): void {
		this.posted.push(message);
	}

	terminate(): void {
		this.terminated = true;
	}

	/** Test helper: simulates the worker sending a response back. */
	respond(message: WasmEngineResponse): void {
		this.onmessage?.({ data: message } as MessageEvent<WasmEngineResponse>);
	}
}

function docs(): CvDocuments {
	return { cv: 'cv:\n  name: John Doe\n', design: '', locale: '', settings: '' };
}

describe('WasmRenderEngine', () => {
	it('posts an init message immediately and is not ready until the worker replies ready', () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);

		expect(worker.posted).toEqual([{ type: 'init' }]);
		expect(engine.isReady()).toBe(false);

		worker.respond({ type: 'ready' });
		expect(engine.isReady()).toBe(true);
	});

	it('stays not-ready forever if the worker reports an init error', () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);

		worker.respond({ type: 'init-error', message: 'wheel install failed' });
		expect(engine.isReady()).toBe(false);
	});

	it('rejects render() before the engine is ready, without posting a render message', async () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);

		await expect(engine.render(docs())).rejects.toThrow('not ready');
		expect(worker.posted).toEqual([{ type: 'init' }]);
	});

	it('resolves render() with a PDF blob once the worker answers with a matching requestId', async () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);
		worker.respond({ type: 'ready' });

		const promise = engine.render(docs());
		const renderMessage = worker.posted.find((m) => m.type === 'render');
		expect(renderMessage).toBeDefined();
		const requestId = (renderMessage as { requestId: number }).requestId;

		const pdfBytes = new Uint8Array([1, 2, 3]);
		worker.respond({ type: 'render-result', requestId, ok: true, pdf: pdfBytes });

		const blob = await promise;
		expect(blob.type).toBe('application/pdf');
		expect(await blob.arrayBuffer()).toEqual(pdfBytes.buffer);
	});

	it('rejects render() when the worker answers with ok: false for the matching requestId', async () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);
		worker.respond({ type: 'ready' });

		const promise = engine.render(docs());
		const requestId = (worker.posted.find((m) => m.type === 'render') as { requestId: number })
			.requestId;

		worker.respond({ type: 'render-result', requestId, ok: false, message: 'compile failed' });

		await expect(promise).rejects.toThrow('compile failed');
	});

	it('correlates concurrent renders by requestId rather than resolving in post order', async () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);
		worker.respond({ type: 'ready' });

		const first = engine.render(docs());
		const second = engine.render(docs());
		const [firstId, secondId] = worker.posted
			.filter((m) => m.type === 'render')
			.map((m) => (m as { requestId: number }).requestId);

		// Answer the second request first.
		worker.respond({ type: 'render-result', requestId: secondId, ok: true, pdf: new Uint8Array([2]) });
		worker.respond({ type: 'render-result', requestId: firstId, ok: true, pdf: new Uint8Array([1]) });

		const [firstBlob, secondBlob] = await Promise.all([first, second]);
		expect(await firstBlob.arrayBuffer()).toEqual(new Uint8Array([1]).buffer);
		expect(await secondBlob.arrayBuffer()).toEqual(new Uint8Array([2]).buffer);
	});

	it('dispose() terminates the worker and rejects renders still in flight', async () => {
		const worker = new FakeWorker();
		const engine = new WasmRenderEngine(() => worker as unknown as Worker);
		worker.respond({ type: 'ready' });

		const promise = engine.render(docs());
		engine.dispose();

		expect(worker.terminated).toBe(true);
		await expect(promise).rejects.toThrow('disposed');
	});
});

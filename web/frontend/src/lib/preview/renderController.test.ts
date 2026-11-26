import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get, writable } from 'svelte/store';
import { createRenderController, type ClientRenderEngine } from './renderController';
import type { CvDocuments } from '$lib/stores/documents';
import type { RenderResult } from '$lib/api/render';

/** A fake client render engine for the fallback/selection tests below -- never touches real wasm. */
function fakeEngine(overrides: Partial<ClientRenderEngine> = {}): ClientRenderEngine {
	return {
		isReady: () => true,
		render: vi.fn(async () => new Blob(['client-pdf'])),
		...overrides
	};
}

function docs(cv = 'cv:\n  name: John Doe\n'): CvDocuments {
	return { cv, design: '', locale: '', settings: '' };
}

describe('createRenderController', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('debounces: a burst of document changes triggers exactly one render', async () => {
		const source = writable<CvDocuments>(docs());
		const render = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['pdf']) })
		);
		let urlCounter = 0;
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => `blob:${++urlCounter}`,
			revokeObjectURL: () => {}
		});

		// Rapid edits within the debounce window.
		source.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(300);
		source.set(docs('cv:\n  name: AB\n'));
		vi.advanceTimersByTime(300);
		source.set(docs('cv:\n  name: ABC\n'));

		// Still inside the debounce window from the last change.
		vi.advanceTimersByTime(799);
		expect(render).not.toHaveBeenCalled();

		vi.advanceTimersByTime(1);
		await vi.waitFor(() => expect(render).toHaveBeenCalledTimes(1));

		expect(render).toHaveBeenCalledWith(docs('cv:\n  name: ABC\n'));
		controller.destroy();
	});

	it('shows a pending status before the first successful render, then the blob URL', async () => {
		const source = writable<CvDocuments>(docs());
		let resolveRender: (result: RenderResult) => void = () => {};
		const render = vi.fn(
			() =>
				new Promise<RenderResult>((resolve) => {
					resolveRender = resolve;
				})
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => 'blob:first',
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800);
		expect(get(controller.state).status).toBe('pending');
		expect(get(controller.state).hasRenderedOnce).toBe(false);

		resolveRender({ ok: true, blob: new Blob(['pdf']) });
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));

		expect(get(controller.state).url).toBe('blob:first');
		expect(get(controller.state).hasRenderedOnce).toBe(true);
		controller.destroy();
	});

	it('keeps the last good preview visible when a later render is invalid', async () => {
		const source = writable<CvDocuments>(docs());
		const render = vi
			.fn<() => Promise<RenderResult>>()
			.mockResolvedValueOnce({ ok: true, blob: new Blob(['pdf']) })
			.mockResolvedValueOnce({
				ok: false,
				errors: [
					{
						location: 'cv.name',
						message: 'Field required',
						yaml_source: 'main_yaml_file',
						yaml_line: 2
					}
				]
			});
		const revokeObjectURL = vi.fn();
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => 'blob:good',
			revokeObjectURL
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));
		expect(get(controller.state).url).toBe('blob:good');

		source.set(docs('cv:\n  name: \n')); // now invalid
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('error'));

		const state = get(controller.state);
		expect(state.url).toBe('blob:good'); // last good preview retained
		expect(state.errors).toEqual([
			{ location: 'cv.name', message: 'Field required', yaml_source: 'main_yaml_file', yaml_line: 2 }
		]);
		expect(revokeObjectURL).not.toHaveBeenCalled(); // only replaced on a new success
		controller.destroy();
	});

	it('revokes the previous blob URL once a newer render succeeds', async () => {
		const source = writable<CvDocuments>(docs());
		let call = 0;
		const render = vi.fn(async (): Promise<RenderResult> => {
			call += 1;
			return { ok: true, blob: new Blob([`pdf-${call}`]) };
		});
		const revokeObjectURL = vi.fn();
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => `blob:${call}`,
			revokeObjectURL
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).url).toBe('blob:1'));

		source.set(docs('cv:\n  name: B\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).url).toBe('blob:2'));

		expect(revokeObjectURL).toHaveBeenCalledWith('blob:1');
		controller.destroy();
	});

	it('renderNow bypasses the debounce timer', async () => {
		const source = writable<CvDocuments>(docs());
		const render = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => 'blob:now',
			revokeObjectURL: () => {}
		});

		controller.renderNow(docs('cv:\n  name: Now\n'));
		await vi.waitFor(() => expect(render).toHaveBeenCalledTimes(1));
		expect(render).toHaveBeenCalledWith(docs('cv:\n  name: Now\n'));
		controller.destroy();
	});

	it('startPaused: does not react to the source (or fire a render) until activate() is called', async () => {
		const source = writable<CvDocuments>(docs());
		const render = vi.fn(async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['pdf']) }));
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => 'blob:paused',
			revokeObjectURL: () => {},
			startPaused: true
		});

		// A store change before activation (e.g. a bootstrap placeholder) must
		// not schedule a render, however long we wait.
		source.set(docs('cv:\n  name: Placeholder\n'));
		vi.advanceTimersByTime(5000);
		expect(render).not.toHaveBeenCalled();
		expect(get(controller.state).url).toBeNull();

		controller.activate();
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(render).toHaveBeenCalledTimes(1));
		expect(render).toHaveBeenCalledWith(docs('cv:\n  name: Placeholder\n'));

		controller.destroy();
	});

	it('startPaused: activate() is idempotent (a second call does not double-subscribe)', async () => {
		const source = writable<CvDocuments>(docs());
		const render = vi.fn(async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['pdf']) }));
		const controller = createRenderController(source, {
			debounceMs: 800,
			render,
			createObjectURL: () => 'blob:once',
			revokeObjectURL: () => {},
			startPaused: true
		});

		controller.activate();
		controller.activate();

		source.set(docs('cv:\n  name: Once\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(render).toHaveBeenCalledTimes(1));

		controller.destroy();
	});
});

describe('createRenderController: client (wasm) engine selection and fallback', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('uses the client engine when enabled and ready, and never calls the server render', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine();
		const serverRender = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['server-pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => true,
			createObjectURL: () => 'blob:client',
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));

		expect(engine.render).toHaveBeenCalledTimes(1);
		expect(serverRender).not.toHaveBeenCalled();
		expect(get(controller.state).url).toBe('blob:client');
		expect(get(controller.state).renderedBy).toBe('client');
		controller.destroy();
	});

	it('falls back to the server when the flag is off, even with a ready engine', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine();
		const serverRender = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['server-pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => false,
			createObjectURL: () => 'blob:server',
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));

		expect(engine.render).not.toHaveBeenCalled();
		expect(serverRender).toHaveBeenCalledTimes(1);
		expect(get(controller.state).renderedBy).toBe('server');
		controller.destroy();
	});

	it('falls back to the server when the engine reports not ready', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine({ isReady: () => false });
		const serverRender = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['server-pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => true,
			createObjectURL: () => 'blob:server',
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));

		expect(engine.render).not.toHaveBeenCalled();
		expect(serverRender).toHaveBeenCalledTimes(1);
		controller.destroy();
	});

	it('falls back to the server for a render whose client attempt rejects, without marking the engine unhealthy after only one failure', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine({
			render: vi
				.fn(async () => new Blob(['client-pdf']))
				.mockRejectedValueOnce(new Error('boom'))
		});
		let call = 0;
		const serverRender = vi.fn(async (): Promise<RenderResult> => {
			call += 1;
			return { ok: true, blob: new Blob([`server-${call}`]) };
		});
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => true,
			createObjectURL: () => `blob:${call}`,
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('success'));
		expect(serverRender).toHaveBeenCalledTimes(1);
		expect(get(controller.state).renderedBy).toBe('server');

		// A second edit: the engine (now resolving normally again) should still
		// be tried, since one failure alone must not flag it unhealthy.
		source.set(docs('cv:\n  name: Second\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(engine.render).toHaveBeenCalledTimes(2));
		await vi.waitFor(() => expect(get(controller.state).renderedBy).toBe('client'));

		controller.destroy();
	});

	it('marks the engine unhealthy after 3 consecutive failures and skips it for subsequent renders', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine({ render: vi.fn().mockRejectedValue(new Error('boom')) });
		const serverRender = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['server-pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => true,
			clientRenderMaxConsecutiveFailures: 3,
			createObjectURL: () => 'blob:server',
			revokeObjectURL: () => {}
		});

		for (let i = 1; i <= 3; i++) {
			source.set(docs(`cv:\n  name: Attempt ${i}\n`));
			vi.advanceTimersByTime(800);
			await vi.waitFor(() => expect(engine.render).toHaveBeenCalledTimes(i));
			await vi.waitFor(() => expect(serverRender).toHaveBeenCalledTimes(i));
		}

		// A 4th edit: the engine must now be skipped entirely (still called 3 times).
		source.set(docs('cv:\n  name: Attempt 4\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(serverRender).toHaveBeenCalledTimes(4));
		expect(engine.render).toHaveBeenCalledTimes(3);

		controller.destroy();
	});

	it('treats a client render that never settles as a failure once the timeout elapses, and still falls back to the server', async () => {
		const source = writable<CvDocuments>(docs());
		const engine = fakeEngine({ render: vi.fn(() => new Promise<Blob>(() => {})) });
		const serverRender = vi.fn(
			async (): Promise<RenderResult> => ({ ok: true, blob: new Blob(['server-pdf']) })
		);
		const controller = createRenderController(source, {
			debounceMs: 800,
			render: serverRender,
			clientRenderEngine: engine,
			clientRenderEnabled: () => true,
			clientRenderTimeoutMs: 2000,
			createObjectURL: () => 'blob:server',
			revokeObjectURL: () => {}
		});

		vi.advanceTimersByTime(800); // fires the debounced render
		vi.advanceTimersByTime(2000); // the client engine's timeout elapses
		await vi.waitFor(() => expect(serverRender).toHaveBeenCalledTimes(1));
		expect(get(controller.state).renderedBy).toBe('server');

		controller.destroy();
	});
});

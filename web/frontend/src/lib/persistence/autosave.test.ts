import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get, writable } from 'svelte/store';
import { createAutosaveController } from './autosave';
import type { CvDocuments } from '$lib/stores/documents';
import type { ActiveCvMeta } from '$lib/stores/cvSession';
import type { UpdateCvResult } from '$lib/api/cvs';

function docs(cv = 'cv:\n  name: John Doe\n'): CvDocuments {
	return { cv, design: '', locale: '', settings: '' };
}

function meta(name = 'Untitled CV'): ActiveCvMeta {
	return { id: 1, name };
}

describe('createAutosaveController', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('does not save when a fresh baseline is set (loading a CV is not a dirty edit)', () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi.fn();
		const controller = createAutosaveController(documentsSource, metaSource, { updateCv });

		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });
		vi.advanceTimersByTime(5000);

		expect(updateCv).not.toHaveBeenCalled();
		expect(get(controller.state).status).toBe('saved');
		controller.destroy();
	});

	it('debounces: a burst of edits triggers exactly one save after 1500ms', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => ({ ok: true, updatedAt: 't1' }));
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(500);
		documentsSource.set(docs('cv:\n  name: AB\n'));
		vi.advanceTimersByTime(500);
		documentsSource.set(docs('cv:\n  name: ABC\n'));

		vi.advanceTimersByTime(1499);
		expect(updateCv).not.toHaveBeenCalled();
		expect(get(controller.state).status).toBe('saved'); // still idle, not yet triggered

		vi.advanceTimersByTime(1);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));

		expect(updateCv).toHaveBeenCalledWith(
			1,
			{ name: 'Untitled CV', documents: docs('cv:\n  name: ABC\n'), seenUpdatedAt: 't0' },
			undefined,
			{}
		);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('saved'));
		controller.destroy();
	});

	it('a rename (name-only change) is dirty too', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta('Untitled CV'));
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => ({ ok: true, updatedAt: 't1' }));
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		metaSource.set(meta('My Resume'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));
		expect(updateCv).toHaveBeenCalledWith(
			1,
			expect.objectContaining({ name: 'My Resume' }),
			undefined,
			{}
		);
		controller.destroy();
	});

	it('serializes saves: an edit arriving while a save is in flight re-queues instead of firing a second request concurrently', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		let resolveFirst: (r: UpdateCvResult) => void = () => {};
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockImplementationOnce(
				() =>
					new Promise((resolve) => {
						resolveFirst = resolve;
					})
			)
			.mockResolvedValueOnce({ ok: true, updatedAt: 't2' });

		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));
		expect(get(controller.state).status).toBe('saving');

		// A second edit arrives while the first save is still in flight.
		documentsSource.set(docs('cv:\n  name: AB\n'));
		vi.advanceTimersByTime(1500); // the debounce for this edit elapses while still in flight

		expect(updateCv).toHaveBeenCalledTimes(1); // no concurrent second request yet

		resolveFirst({ ok: true, updatedAt: 't1' });
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(2));
		expect(updateCv).toHaveBeenNthCalledWith(
			2,
			1,
			expect.objectContaining({ documents: docs('cv:\n  name: AB\n'), seenUpdatedAt: 't1' }),
			undefined,
			{}
		);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('saved'));
		controller.destroy();
	});

	it('retries once after 3s on failure, then surfaces an error', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockResolvedValue({ ok: false, kind: 'error', message: 'boom' });
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			retryDelayMs: 3000,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));
		await vi.waitFor(() => expect(get(controller.state).status).toBe('retrying'));

		vi.advanceTimersByTime(3000);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(2));
		await vi.waitFor(() => expect(get(controller.state).status).toBe('error'));
		controller.destroy();
	});

	it('retryNow immediately retries after a surfaced error', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockResolvedValueOnce({ ok: false, kind: 'error', message: 'boom' })
			.mockResolvedValueOnce({ ok: false, kind: 'error', message: 'boom' })
			.mockResolvedValueOnce({ ok: true, updatedAt: 't1' });
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			retryDelayMs: 3000,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));
		vi.advanceTimersByTime(3000);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('error'));

		controller.retryNow();
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(3));
		await vi.waitFor(() => expect(get(controller.state).status).toBe('saved'));
		controller.destroy();
	});

	it('on a 409 conflict, freezes further autosaves and surfaces the server state; "reload" adopts it', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const serverDocs = docs('cv:\n  name: Server Wins\n');
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockResolvedValueOnce({ ok: false, kind: 'conflict', current: { updatedAt: 'tserver', documents: serverDocs } });
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: Local Edit\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('conflict'));
		expect(get(controller.state).conflict).toEqual({ updatedAt: 'tserver', documents: serverDocs });

		// Further edits while conflicted must not trigger a new autosave attempt.
		documentsSource.set(docs('cv:\n  name: Another Local Edit\n'));
		vi.advanceTimersByTime(5000);
		expect(updateCv).toHaveBeenCalledTimes(1);

		documentsSource.set(serverDocs); // caller applies "Tải bản mới" by writing the server docs into the store
		controller.resolveConflict('reload');
		expect(get(controller.state).status).toBe('saved');

		// Now further edits resume normal autosaving against the new baseline.
		updateCv.mockResolvedValueOnce({ ok: true, updatedAt: 'tnext' });
		documentsSource.set(docs('cv:\n  name: Fresh Edit\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(2));
		expect(updateCv).toHaveBeenNthCalledWith(
			2,
			1,
			expect.objectContaining({ seenUpdatedAt: 'tserver' }),
			undefined,
			{}
		);
		controller.destroy();
	});

	it('"overwrite" re-submits the local edit against the server\'s current updatedAt', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const localDocs = docs('cv:\n  name: Local Edit\n');
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockResolvedValueOnce({
				ok: false,
				kind: 'conflict',
				current: { updatedAt: 'tserver', documents: docs('cv:\n  name: Server\n') }
			})
			.mockResolvedValueOnce({ ok: true, updatedAt: 'tafter' });
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(localDocs);
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('conflict'));

		controller.resolveConflict('overwrite');
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(2));
		expect(updateCv).toHaveBeenNthCalledWith(
			2,
			1,
			expect.objectContaining({ documents: localDocs, seenUpdatedAt: 'tserver' }),
			undefined,
			{}
		);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('saved'));
		controller.destroy();
	});

	it('flush() awaits an in-flight save and then saves again if still dirty', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		let resolveFirst: (r: UpdateCvResult) => void = () => {};
		const updateCv = vi
			.fn<() => Promise<UpdateCvResult>>()
			.mockImplementationOnce(
				() =>
					new Promise((resolve) => {
						resolveFirst = resolve;
					})
			)
			.mockResolvedValueOnce({ ok: true, updatedAt: 't2' });
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));

		documentsSource.set(docs('cv:\n  name: AB\n')); // a trailing edit, still within its own debounce window

		const flushPromise = controller.flush();
		resolveFirst({ ok: true, updatedAt: 't1' });
		await flushPromise;

		expect(updateCv).toHaveBeenCalledTimes(2);
		expect(get(controller.state).status).toBe('saved');
		controller.destroy();
	});

	it('flush() is a no-op when nothing is dirty', async () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => ({ ok: true, updatedAt: 't1' }));
		const controller = createAutosaveController(documentsSource, metaSource, { updateCv });
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		await controller.flush();
		expect(updateCv).not.toHaveBeenCalled();
		controller.destroy();
	});

	it('flushBeforeUnload fires a keepalive save without waiting for it', () => {
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => ({ ok: true, updatedAt: 't1' }));
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv:\n  name: A\n'));
		controller.flushBeforeUnload();

		expect(updateCv).toHaveBeenCalledWith(
			1,
			expect.objectContaining({ documents: docs('cv:\n  name: A\n') }),
			undefined,
			{ keepalive: true }
		);
		controller.destroy();
	});

	it('never puts two saves on the wire at once when flush races a queued follow-up save', async () => {
		// Regression: `flush()` awaited only the save that was on the wire when
		// it was called. That save's success handler starts the queued
		// follow-up, so flush then started a *second* save alongside it -- both
		// carrying the same `seenUpdatedAt`, so the loser 409s and the user sees
		// a conflict bar against their own edit.
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());

		let inFlightCount = 0;
		let maxConcurrent = 0;
		const gates: Array<() => void> = [];
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => {
			inFlightCount += 1;
			maxConcurrent = Math.max(maxConcurrent, inFlightCount);
			await new Promise<void>((resolve) => gates.push(resolve));
			inFlightCount -= 1;
			return { ok: true, updatedAt: `t${updateCv.mock.calls.length}` };
		});
		const settle = async (): Promise<void> => {
			for (let i = 0; i < 20; i += 1) await Promise.resolve();
		};

		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv: {name: A}'));
		vi.advanceTimersByTime(1500); // save A starts and stays in flight (gated)
		documentsSource.set(docs('cv: {name: AB}'));
		vi.advanceTimersByTime(1500); // triggers while in flight -> queues the follow-up

		const flushed = controller.flush();
		gates.shift()?.(); // let save A land: its handler starts the queued save
		await settle();

		// The queued save is now on the wire. Before the fix, flush resumed here
		// and started a second one alongside it.
		expect(maxConcurrent).toBe(1);

		// Drain whatever is still gated so `flush()` can resolve.
		for (let i = 0; i < 5 && (gates.length > 0 || inFlightCount > 0); i += 1) {
			gates.shift()?.();
			await settle();
		}
		await flushed;
		expect(get(controller.state).status).toBe('saved');
		controller.destroy();
	});

	
	it('drops a save result that lands after the baseline moved to another CV', async () => {
		// Regression: the success handler reinstalled its own snapshot as the
		// baseline unconditionally. A save for CV 1 resolving after the app had
		// loaded CV 2 reset the baseline back to CV 1, and `isDirty()`'s id
		// check then reported every later edit as clean -- autosave silently
		// dead until reload.
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());

		let release!: () => void;
		const savedCvIds: number[] = [];
		const updateCv = vi.fn(async (id: number): Promise<UpdateCvResult> => {
			savedCvIds.push(id);
			await new Promise<void>((resolve) => {
				release = resolve;
			});
			return { ok: true, updatedAt: 't1' };
		});

		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv: {name: A}'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));

		// CV 2 is loaded while CV 1's save is still on the wire.
		metaSource.set({ id: 2, name: 'Second CV' });
		documentsSource.set(docs('cv: {name: second}'));
		controller.setBaseline({
			id: 2,
			name: 'Second CV',
			documents: docs('cv: {name: second}'),
			updatedAt: 's0'
		});

		release();
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(1));

		// Editing CV 2 must still autosave: the stale result must not have
		// restored CV 1's baseline.
		documentsSource.set(docs('cv: {name: second edited}'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(updateCv).toHaveBeenCalledTimes(2));
		expect(savedCvIds).toEqual([1, 2]);
		controller.destroy();
	});

	it('surfaces a too-large save as a permanent error instead of retrying it', async () => {
		// Regression: 413/404 are deterministic, but they fell into the generic
		// retry path -- the identical oversized payload was resent and the user
		// only ever saw "Save failed" with a Retry that could not succeed.
		const documentsSource = writable<CvDocuments>(docs());
		const metaSource = writable<ActiveCvMeta | null>(meta());
		const updateCv = vi.fn(async (): Promise<UpdateCvResult> => ({ ok: false, kind: 'too-large' }));
		const controller = createAutosaveController(documentsSource, metaSource, {
			debounceMs: 1500,
			retryDelayMs: 3000,
			updateCv
		});
		controller.setBaseline({ id: 1, name: 'Untitled CV', documents: docs(), updatedAt: 't0' });

		documentsSource.set(docs('cv: {name: A}'));
		vi.advanceTimersByTime(1500);
		await vi.waitFor(() => expect(get(controller.state).status).toBe('error'));

		expect(get(controller.state).permanentError).toMatch(/too large/i);

		vi.advanceTimersByTime(10000); // no retry is ever scheduled
		expect(updateCv).toHaveBeenCalledTimes(1);
		controller.destroy();
	});
});

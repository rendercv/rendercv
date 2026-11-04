import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get, writable } from 'svelte/store';
import { createFormSync, type FormSyncController } from './formSync';
import type { CvDocuments } from '$lib/stores/documents';
import type { ParseResult, PatchResult } from '$lib/api/documents';
import type { PatchOp } from './patchOps';

function docs(cv: string): CvDocuments {
	return { cv, design: '', locale: '', settings: '' };
}

describe('formSync', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});
	afterEach(() => {
		vi.useRealTimers();
	});

	it('activate() parses the current cv yaml into the form model', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({ ok: true, data: { cv: { name: 'John' } } })
		);
		const patch = vi.fn(async (): Promise<PatchResult> => ({ ok: true, yaml: '' }));
		const sync = createFormSync(store, { parse, patch });

		await sync.activate();

		expect(parse).toHaveBeenCalledWith('cv:\n  name: John\n');
		expect(get(sync.state)).toEqual({
			status: 'ready',
			data: { cv: { name: 'John' } },
			errors: [],
			toast: null
		});
		sync.destroy();
	});

	it('a document replaced mid-parse is still picked up', async () => {
		// Importing a CV writes the documents twice in quick succession: the
		// empty CV the server just created, then the imported text. The
		// second write lands while the first parse is still in flight, and
		// the subscription cannot act on it yet -- so the parse itself has
		// to notice on the way out. Without that the form kept showing the
		// document that is no longer open, which is how an imported
		// `engineeringresumes` design was displayed as `classic`.
		const store = writable(docs('cv:\n  name: Old\n'));
		const resolvers: ((result: ParseResult) => void)[] = [];
		const parse = vi.fn(
			(): Promise<ParseResult> => new Promise((resolve) => resolvers.push(resolve))
		);
		const sync = createFormSync(store, { parse, patch: vi.fn() });

		const activation = sync.activate();
		store.set(docs('cv:\n  name: New\n'));

		// The first parse answers about the document that has been replaced.
		resolvers[0]({ ok: true, data: { cv: { name: 'Old' } } });
		await activation;

		// It must have gone round again for the document that is actually open.
		await vi.waitFor(() => expect(parse).toHaveBeenCalledTimes(2));
		expect(parse).toHaveBeenLastCalledWith('cv:\n  name: New\n');

		resolvers[1]({ ok: true, data: { cv: { name: 'New' } } });
		await vi.waitFor(() => expect(get(sync.state).data).toEqual({ cv: { name: 'New' } }));
		sync.destroy();
	});

	it('a failed parse surfaces its errors and no data', async () => {
		const store = writable(docs('cv:\n  name: [\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({
				ok: false,
				errors: [{ location: null, message: 'bad yaml', yaml_source: 'main_yaml_file', yaml_line: 2 }]
			})
		);
		const sync = createFormSync(store, { parse, patch: vi.fn() });

		await sync.activate();

		const state = get(sync.state);
		expect(state.status).toBe('error');
		expect(state.data).toBeNull();
		expect(state.errors[0].message).toBe('bad yaml');
		sync.destroy();
	});

	it('submitOp applies an optimistic update immediately, before any network call resolves', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({ ok: true, data: { cv: { name: 'John' } } })
		);
		let resolvePatch: ((r: PatchResult) => void) | undefined;
		const patch = vi.fn(
			() =>
				new Promise<PatchResult>((resolve) => {
					resolvePatch = resolve;
				})
		);
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'Jane' });

		// Optimistic update is synchronous -- no need to advance timers.
		expect(get(sync.state).data).toEqual({ cv: { name: 'Jane' } });

		await vi.advanceTimersByTimeAsync(300);
		expect(patch).toHaveBeenCalledTimes(1);
		expect(patch).toHaveBeenCalledWith('cv:\n  name: John\n', [
			{ op: 'set', path: ['cv', 'name'], value: 'Jane' }
		]);

		resolvePatch?.({ ok: true, yaml: 'cv:\n  name: Jane\n' });
		await vi.advanceTimersByTimeAsync(0);
		expect(get(store).cv).toBe('cv:\n  name: Jane\n');
		sync.destroy();
	});

	it('debounces and collapses a burst of edits to the same field into a single patch call', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({ ok: true, data: { cv: { name: 'John' } } })
		);
		const patch = vi.fn(async (): Promise<PatchResult> => ({ ok: true, yaml: 'cv:\n  name: Joh\n' }));
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'Jo' });
		await vi.advanceTimersByTimeAsync(100);
		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'Joh' });
		await vi.advanceTimersByTimeAsync(100);
		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'John' });

		await vi.advanceTimersByTimeAsync(300);

		expect(patch).toHaveBeenCalledTimes(1);
		expect(patch).toHaveBeenCalledWith('cv:\n  name: John\n', [
			{ op: 'set', path: ['cv', 'name'], value: 'John' }
		]);
		sync.destroy();
	});

	it('serializes patches: never two in-flight, and flushes ops queued during a request right after it resolves', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({ ok: true, data: { cv: { name: 'John' } } })
		);
		const calls: PatchOp[][] = [];
		const resolvers: Array<(r: PatchResult) => void> = [];
		const patch = vi.fn((_yaml: string, ops: PatchOp[]) => {
			calls.push(ops);
			return new Promise<PatchResult>((resolve) => resolvers.push(resolve));
		});
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'Jane' });
		await vi.advanceTimersByTimeAsync(300);
		expect(patch).toHaveBeenCalledTimes(1);

		// A second edit arrives while the first patch is still in flight.
		sync.submitOp({ op: 'set', path: ['cv', 'headline'], value: 'Engineer' });
		await vi.advanceTimersByTimeAsync(300);
		// Still only one call: the second edit was queued, not sent early.
		expect(patch).toHaveBeenCalledTimes(1);

		resolvers[0]?.({ ok: true, yaml: 'cv:\n  name: Jane\n' });
		await vi.advanceTimersByTimeAsync(0);

		expect(patch).toHaveBeenCalledTimes(2);
		expect(calls[1]).toEqual([{ op: 'set', path: ['cv', 'headline'], value: 'Engineer' }]);

		resolvers[1]?.({ ok: true, yaml: 'cv:\n  name: Jane\n  headline: Engineer\n' });
		await vi.advanceTimersByTimeAsync(0);
		expect(get(store).cv).toBe('cv:\n  name: Jane\n  headline: Engineer\n');
		sync.destroy();
	});

	it('a 400 op-error triggers a toast and a full re-parse from the current store yaml', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi
			.fn()
			.mockResolvedValueOnce({ ok: true, data: { cv: { name: 'John' } } } satisfies ParseResult)
			.mockResolvedValueOnce({ ok: true, data: { cv: { name: 'John' } } } satisfies ParseResult);
		const patch = vi.fn(
			async (): Promise<PatchResult> => ({
				ok: false,
				kind: 'op-error',
				error: { op_index: 0, message: 'bad path' }
			})
		);
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'bogus', 'path'], value: 'x' });
		await vi.advanceTimersByTimeAsync(300);
		await vi.advanceTimersByTimeAsync(0);

		expect(parse).toHaveBeenCalledTimes(2); // activate() + recovery reparse
		const state = get(sync.state);
		expect(state.toast).toBe('bad path');
		expect(state.status).toBe('ready'); // recovered
		sync.destroy();
	});

	it('a 422 validation failure also toasts and recovers via re-parse', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi
			.fn()
			.mockResolvedValueOnce({ ok: true, data: { cv: { name: 'John' } } } satisfies ParseResult)
			.mockResolvedValueOnce({ ok: true, data: { cv: { name: 'John' } } } satisfies ParseResult);
		const patch = vi.fn(
			async (): Promise<PatchResult> => ({
				ok: false,
				kind: 'validation',
				errors: [{ location: 'cv.phone', message: 'not a valid phone number', yaml_source: 'main_yaml_file', yaml_line: 3 }]
			})
		);
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'phone'], value: 'abc' });
		await vi.advanceTimersByTimeAsync(300);
		await vi.advanceTimersByTimeAsync(0);

		expect(get(sync.state).toast).toBe('not a valid phone number');
		sync.destroy();
	});

	it('re-parses when the store changes externally (e.g. undo) while active, but not on our own writes', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(async (): Promise<ParseResult> => ({ ok: true, data: { cv: {} } }));
		const patch = vi.fn(async (): Promise<PatchResult> => ({ ok: true, yaml: 'cv:\n  name: X\n' }));
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();
		expect(parse).toHaveBeenCalledTimes(1);

		// External change (simulating an undo in the YAML editor).
		store.set(docs('cv:\n  name: Undone\n'));
		await vi.advanceTimersByTimeAsync(0);
		expect(parse).toHaveBeenCalledTimes(2);
		sync.destroy();
	});

	it('destroy() flushes a still-debouncing edit instead of dropping it (e.g. toggling back to YAML right after a keystroke)', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(
			async (): Promise<ParseResult> => ({ ok: true, data: { cv: { name: 'John' } } })
		);
		const patch = vi.fn(async (): Promise<PatchResult> => ({ ok: true, yaml: 'cv:\n  name: Jane\n' }));
		const sync = createFormSync(store, { parse, patch, debounceMs: 300 });
		await sync.activate();

		sync.submitOp({ op: 'set', path: ['cv', 'name'], value: 'Jane' });
		// Destroy well before the 300ms debounce would have fired on its own.
		sync.destroy();

		await vi.advanceTimersByTimeAsync(0);
		expect(patch).toHaveBeenCalledWith('cv:\n  name: John\n', [
			{ op: 'set', path: ['cv', 'name'], value: 'Jane' }
		]);
		expect(get(store).cv).toBe('cv:\n  name: Jane\n');
	});

	it('does not re-parse after deactivate() even if the store changes', async () => {
		const store = writable(docs('cv:\n  name: John\n'));
		const parse = vi.fn(async (): Promise<ParseResult> => ({ ok: true, data: { cv: {} } }));
		const sync = createFormSync(store, { parse, patch: vi.fn() });
		await sync.activate();
		sync.deactivate();

		store.set(docs('cv:\n  name: Changed\n'));
		await vi.advanceTimersByTimeAsync(0);
		expect(parse).toHaveBeenCalledTimes(1);
		sync.destroy();
	});

	describe('documentKey (design/locale/settings forms sharing the same sync engine)', () => {
		it('tracks the given document instead of "cv"', async () => {
			const store = writable(docs('cv:\n  name: John\n'));
			store.update((d) => ({ ...d, design: 'design:\n  theme: classic\n' }));
			const parse = vi.fn(
				async (): Promise<ParseResult> => ({ ok: true, data: { design: { theme: 'classic' } } })
			);
			const patch = vi.fn(
				async (): Promise<PatchResult> => ({ ok: true, yaml: 'design:\n  theme: ember\n' })
			);
			const sync = createFormSync(store, { documentKey: 'design', parse, patch, debounceMs: 300 });

			await sync.activate();
			expect(parse).toHaveBeenCalledWith('design:\n  theme: classic\n');

			sync.submitOp({ op: 'set', path: ['design', 'theme'], value: 'ember' });
			await vi.advanceTimersByTimeAsync(300);
			expect(patch).toHaveBeenCalledWith('design:\n  theme: classic\n', [
				{ op: 'set', path: ['design', 'theme'], value: 'ember' }
			]);
			await vi.advanceTimersByTimeAsync(0);

			expect(get(store).design).toBe('design:\n  theme: ember\n');
			expect(get(store).cv).toBe('cv:\n  name: John\n'); // untouched
			sync.destroy();
		});

		it('the first write on a still-blank document patches "{}" instead of the literal blank string (the backend rejects a truly empty document)', async () => {
			const store = writable(docs('cv:\n  name: John\n')); // design starts blank
			const parse = vi.fn(async (): Promise<ParseResult> => ({ ok: true, data: {} }));
			const patch = vi.fn(
				async (): Promise<PatchResult> => ({ ok: true, yaml: 'design:\n  theme: ember\n' })
			);
			const sync = createFormSync(store, { documentKey: 'design', parse, patch, debounceMs: 300 });
			await sync.activate();

			sync.submitOp({ op: 'set', path: ['design'], value: { theme: 'ember' } });
			await vi.advanceTimersByTimeAsync(300);

			expect(patch).toHaveBeenCalledWith('{}', [
				{ op: 'set', path: ['design'], value: { theme: 'ember' } }
			]);
			sync.destroy();
		});

		it('a blank document (never touched) resolves to an empty tree without calling parse', async () => {
			const store = writable(docs('cv:\n  name: John\n')); // design/locale/settings default to ''
			const parse = vi.fn(async (): Promise<ParseResult> => ({ ok: true, data: {} }));
			const sync = createFormSync(store, { documentKey: 'design', parse, patch: vi.fn() });

			await sync.activate();

			expect(parse).not.toHaveBeenCalled();
			expect(get(sync.state)).toEqual({ status: 'ready', data: {}, errors: [], toast: null });
			sync.destroy();
		});
	});
});

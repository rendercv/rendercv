import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get, writable } from 'svelte/store';
import { createValidateController } from './validateController';
import type { CvDocuments } from '$lib/stores/documents';
import type { ValidateResult } from '$lib/api/validate';

function docs(cv = 'cv:\n  name: John Doe\n'): CvDocuments {
	return { cv, design: '', locale: '', settings: '' };
}

describe('createValidateController', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('debounces: a burst of document changes triggers exactly one validation', async () => {
		const source = writable<CvDocuments>(docs());
		const validate = vi.fn(async (): Promise<ValidateResult> => ({ ok: true }));
		const controller = createValidateController(source, { debounceMs: 800, validate });

		source.set(docs('cv:\n  name: A\n'));
		vi.advanceTimersByTime(300);
		source.set(docs('cv:\n  name: AB\n'));
		vi.advanceTimersByTime(799);
		expect(validate).not.toHaveBeenCalled();

		vi.advanceTimersByTime(1);
		await vi.waitFor(() => expect(validate).toHaveBeenCalledTimes(1));
		expect(validate).toHaveBeenCalledWith(docs('cv:\n  name: AB\n'));
		controller.destroy();
	});

	it('starts unchecked, then reports errors from a failed validation', async () => {
		const source = writable<CvDocuments>(docs());
		const validate = vi.fn(
			async (): Promise<ValidateResult> => ({
				ok: false,
				errors: [
					{
						location: 'cv.phone',
						message: 'This is not a valid phone number.',
						yaml_source: 'main_yaml_file',
						yaml_line: 3
					}
				]
			})
		);
		const controller = createValidateController(source, { debounceMs: 800, validate });

		expect(get(controller.state)).toEqual({ checked: false, errors: [] });

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).checked).toBe(true));

		expect(get(controller.state).errors).toEqual([
			{
				location: 'cv.phone',
				message: 'This is not a valid phone number.',
				yaml_source: 'main_yaml_file',
				yaml_line: 3
			}
		]);
		controller.destroy();
	});

	it('clears errors once a later validation succeeds', async () => {
		const source = writable<CvDocuments>(docs());
		const validate = vi
			.fn<() => Promise<ValidateResult>>()
			.mockResolvedValueOnce({
				ok: false,
				errors: [{ location: 'cv.phone', message: 'bad phone', yaml_source: 'main_yaml_file', yaml_line: 3 }]
			})
			.mockResolvedValueOnce({ ok: true });
		const controller = createValidateController(source, { debounceMs: 800, validate });

		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).errors.length).toBe(1));

		source.set(docs('cv:\n  name: Fixed\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(get(controller.state).errors.length).toBe(0));

		controller.destroy();
	});

	it('drops a stale in-flight validation when a newer one resolves first', async () => {
		const source = writable<CvDocuments>(docs());
		let resolveFirst: (r: ValidateResult) => void = () => {};
		let resolveSecond: (r: ValidateResult) => void = () => {};
		const validate = vi
			.fn<() => Promise<ValidateResult>>()
			.mockImplementationOnce(() => new Promise((resolve) => (resolveFirst = resolve)))
			.mockImplementationOnce(() => new Promise((resolve) => (resolveSecond = resolve)));
		const controller = createValidateController(source, { debounceMs: 800, validate });

		vi.advanceTimersByTime(800);
		source.set(docs('cv:\n  name: B\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(validate).toHaveBeenCalledTimes(2));

		// Second (newer) request resolves first with success...
		resolveSecond({ ok: true });
		await vi.waitFor(() => expect(get(controller.state).checked).toBe(true));
		// ...then the stale first request resolves with an error, which must be ignored.
		resolveFirst({
			ok: false,
			errors: [{ location: 'x', message: 'stale', yaml_source: 'main_yaml_file', yaml_line: 1 }]
		});

		expect(get(controller.state).errors).toEqual([]);
		controller.destroy();
	});

	it('startPaused: does not react to the source until activate() is called', async () => {
		const source = writable<CvDocuments>(docs());
		const validate = vi.fn(async (): Promise<ValidateResult> => ({ ok: true }));
		const controller = createValidateController(source, { debounceMs: 800, validate, startPaused: true });

		// A change before activation must not schedule anything, even given plenty of time.
		source.set(docs('cv:\n  name: Placeholder\n'));
		vi.advanceTimersByTime(5000);
		expect(validate).not.toHaveBeenCalled();

		controller.activate();
		// activate() itself doesn't validate synchronously -- it starts
		// reacting to subsequent (and, via the subscribe-on-activate contract,
		// the store's *current* value) changes on the normal debounce.
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(validate).toHaveBeenCalledTimes(1));
		expect(validate).toHaveBeenCalledWith(docs('cv:\n  name: Placeholder\n'));

		controller.destroy();
	});

	it('startPaused: activate() is idempotent (a second call does not double-subscribe)', async () => {
		const source = writable<CvDocuments>(docs());
		const validate = vi.fn(async (): Promise<ValidateResult> => ({ ok: true }));
		const controller = createValidateController(source, { debounceMs: 800, validate, startPaused: true });

		controller.activate();
		controller.activate();

		source.set(docs('cv:\n  name: Once\n'));
		vi.advanceTimersByTime(800);
		await vi.waitFor(() => expect(validate).toHaveBeenCalledTimes(1));

		controller.destroy();
	});
});

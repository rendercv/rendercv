import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createPreferenceWriter } from './preferenceWriter';

describe('createPreferenceWriter', () => {
	beforeEach(() => {
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('debounces rapid writes to the same key into the last value', async () => {
		const setPreference = vi.fn().mockResolvedValue(undefined);
		const writer = createPreferenceWriter({ debounceMs: 500, setPreference });

		writer.write('zoom', '110');
		vi.advanceTimersByTime(200);
		writer.write('zoom', '120');
		vi.advanceTimersByTime(200);
		writer.write('zoom', '130');

		vi.advanceTimersByTime(499);
		expect(setPreference).not.toHaveBeenCalled();
		vi.advanceTimersByTime(1);
		await vi.waitFor(() => expect(setPreference).toHaveBeenCalledTimes(1));
		expect(setPreference).toHaveBeenCalledWith('zoom', '130');
		writer.destroy();
	});

	it('debounces independently per key', async () => {
		const setPreference = vi.fn().mockResolvedValue(undefined);
		const writer = createPreferenceWriter({ debounceMs: 500, setPreference });

		writer.write('zoom', '110');
		vi.advanceTimersByTime(300);
		writer.write('sidebar_collapsed', 'true');
		vi.advanceTimersByTime(200); // zoom's 500ms elapses; sidebar's own 500ms hasn't yet

		await vi.waitFor(() => expect(setPreference).toHaveBeenCalledWith('zoom', '110'));
		expect(setPreference).toHaveBeenCalledTimes(1);

		vi.advanceTimersByTime(300);
		await vi.waitFor(() => expect(setPreference).toHaveBeenCalledWith('sidebar_collapsed', 'true'));
		expect(setPreference).toHaveBeenCalledTimes(2);
		writer.destroy();
	});

	it('destroy cancels pending writes', () => {
		const setPreference = vi.fn().mockResolvedValue(undefined);
		const writer = createPreferenceWriter({ debounceMs: 500, setPreference });

		writer.write('zoom', '110');
		writer.destroy();
		vi.advanceTimersByTime(1000);

		expect(setPreference).not.toHaveBeenCalled();
	});
});

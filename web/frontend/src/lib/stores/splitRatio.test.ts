import { describe, it, expect, vi } from 'vitest';
import { get } from 'svelte/store';
import {
	createSplitRatioStore,
	SPLIT_RATIO_STORAGE_KEY,
	SPLIT_RATIO_PREFERENCE_KEY
} from './splitRatio';
import { DEFAULT_SPLIT_RATIO, MIN_SPLIT_RATIO, MAX_SPLIT_RATIO } from '$lib/layout/splitRatio';

function fakeStorage(initial: Record<string, string> = {}): {
	storage: Pick<Storage, 'getItem' | 'setItem'>;
	data: Record<string, string>;
} {
	const data = { ...initial };
	return {
		data,
		storage: {
			getItem: (key: string) => (key in data ? data[key] : null),
			setItem: (key: string, value: string) => {
				data[key] = value;
			}
		}
	};
}

describe('createSplitRatioStore', () => {
	it('defaults to 50 when nothing is stored', () => {
		const { storage } = fakeStorage();
		const store = createSplitRatioStore({ storage });
		expect(get(store)).toBe(DEFAULT_SPLIT_RATIO);
	});

	it('initializes from the localStorage mirror when present', () => {
		const { storage } = fakeStorage({ [SPLIT_RATIO_STORAGE_KEY]: '65' });
		const store = createSplitRatioStore({ storage });
		expect(get(store)).toBe(65);
	});

	it('clamps a corrupted/out-of-range stored value', () => {
		const { storage } = fakeStorage({ [SPLIT_RATIO_STORAGE_KEY]: '999' });
		const store = createSplitRatioStore({ storage });
		expect(get(store)).toBe(MAX_SPLIT_RATIO);
	});

	it('set() clamps, updates the store immediately, and persists to the localStorage mirror synchronously', () => {
		const { storage, data } = fakeStorage();
		const store = createSplitRatioStore({ storage });

		store.set(1);

		expect(get(store)).toBe(MIN_SPLIT_RATIO);
		expect(data[SPLIT_RATIO_STORAGE_KEY]).toBe(String(MIN_SPLIT_RATIO));
	});

	it('debounces the PUT /api/preferences write across rapid set() calls (a drag)', () => {
		vi.useFakeTimers();
		try {
			const { storage } = fakeStorage();
			const setPreference = vi.fn().mockResolvedValue(undefined);
			const store = createSplitRatioStore({ storage, setPreference, debounceMs: 400 });

			store.set(52);
			store.set(58);
			store.set(63);

			expect(setPreference).not.toHaveBeenCalled();

			vi.advanceTimersByTime(400);

			expect(setPreference).toHaveBeenCalledTimes(1);
			expect(setPreference).toHaveBeenCalledWith(SPLIT_RATIO_PREFERENCE_KEY, '63');
		} finally {
			vi.useRealTimers();
		}
	});

	it('applyPersistedPreference updates state from bootstrap without re-writing it', () => {
		const { storage, data } = fakeStorage();
		const setPreference = vi.fn().mockResolvedValue(undefined);
		const store = createSplitRatioStore({ storage, setPreference });

		store.applyPersistedPreference('70');

		expect(get(store)).toBe(70);
		expect(data[SPLIT_RATIO_STORAGE_KEY]).toBe('70');
		expect(setPreference).not.toHaveBeenCalled();
	});

	it('applyPersistedPreference ignores an unset value', () => {
		const { storage } = fakeStorage();
		const store = createSplitRatioStore({ storage });

		store.applyPersistedPreference(undefined);

		expect(get(store)).toBe(DEFAULT_SPLIT_RATIO);
	});

	it('destroy() cancels a pending debounced write', () => {
		vi.useFakeTimers();
		try {
			const { storage } = fakeStorage();
			const setPreference = vi.fn().mockResolvedValue(undefined);
			const store = createSplitRatioStore({ storage, setPreference, debounceMs: 400 });

			store.set(60);
			store.destroy();
			vi.advanceTimersByTime(1000);

			expect(setPreference).not.toHaveBeenCalled();
		} finally {
			vi.useRealTimers();
		}
	});
});

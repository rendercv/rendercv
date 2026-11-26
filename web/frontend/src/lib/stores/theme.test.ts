import { describe, it, expect, vi } from 'vitest';
import { get } from 'svelte/store';
import { createThemeStore, THEME_STORAGE_KEY, THEME_PREFERENCE_KEY } from './theme';

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

describe('createThemeStore', () => {
	it('initializes from the saved preference (localStorage mirror) when present, ignoring the OS setting', () => {
		const { storage } = fakeStorage({ [THEME_STORAGE_KEY]: 'dark' });
		const applyToDocument = vi.fn();

		const store = createThemeStore({ storage, prefersDark: () => false, applyToDocument });

		expect(get(store)).toBe('dark');
		expect(applyToDocument).toHaveBeenCalledWith('dark');
	});

	it('falls back to the OS prefers-color-scheme when no saved preference exists', () => {
		const { storage } = fakeStorage();
		const applyToDocument = vi.fn();

		const darkFromOS = createThemeStore({ storage, prefersDark: () => true, applyToDocument });
		expect(get(darkFromOS)).toBe('dark');

		const { storage: storage2 } = fakeStorage();
		const lightFromOS = createThemeStore({ storage: storage2, prefersDark: () => false, applyToDocument });
		expect(get(lightFromOS)).toBe('light');
	});

	it('toggle flips the mode and persists to both the localStorage mirror and the preferences API', async () => {
		const { storage, data } = fakeStorage({ [THEME_STORAGE_KEY]: 'light' });
		const applyToDocument = vi.fn();
		const setPreference = vi.fn().mockResolvedValue(undefined);

		const store = createThemeStore({ storage, prefersDark: () => false, applyToDocument, setPreference });

		store.toggle();

		expect(get(store)).toBe('dark');
		expect(data[THEME_STORAGE_KEY]).toBe('dark');
		expect(applyToDocument).toHaveBeenLastCalledWith('dark');
		expect(setPreference).toHaveBeenCalledWith(THEME_PREFERENCE_KEY, 'dark');

		store.toggle();

		expect(get(store)).toBe('light');
		expect(data[THEME_STORAGE_KEY]).toBe('light');
		expect(setPreference).toHaveBeenCalledWith(THEME_PREFERENCE_KEY, 'light');
	});

	it('set() persists an explicit mode the same way toggle does', () => {
		const { storage, data } = fakeStorage();
		const applyToDocument = vi.fn();
		const setPreference = vi.fn().mockResolvedValue(undefined);

		const store = createThemeStore({ storage, prefersDark: () => false, applyToDocument, setPreference });

		store.set('dark');

		expect(get(store)).toBe('dark');
		expect(data[THEME_STORAGE_KEY]).toBe('dark');
		expect(setPreference).toHaveBeenCalledWith(THEME_PREFERENCE_KEY, 'dark');
	});

	it('applyPersistedPreference updates state from a bootstrap GET /api/preferences value without re-writing it', () => {
		const { storage, data } = fakeStorage();
		const applyToDocument = vi.fn();
		const setPreference = vi.fn().mockResolvedValue(undefined);

		const store = createThemeStore({ storage, prefersDark: () => false, applyToDocument, setPreference });
		expect(get(store)).toBe('light');

		store.applyPersistedPreference('dark');

		expect(get(store)).toBe('dark');
		expect(data[THEME_STORAGE_KEY]).toBe('dark');
		expect(applyToDocument).toHaveBeenLastCalledWith('dark');
		// The value came FROM preferences -- writing it back would be redundant/racy.
		expect(setPreference).not.toHaveBeenCalled();
	});

	it('applyPersistedPreference ignores an unset/invalid value and a value matching the current mode', () => {
		const { storage } = fakeStorage({ [THEME_STORAGE_KEY]: 'light' });
		const applyToDocument = vi.fn();

		const store = createThemeStore({ storage, prefersDark: () => false, applyToDocument });
		applyToDocument.mockClear();

		store.applyPersistedPreference(undefined);
		store.applyPersistedPreference('not-a-theme');
		store.applyPersistedPreference('light');

		expect(get(store)).toBe('light');
		expect(applyToDocument).not.toHaveBeenCalled();
	});
});

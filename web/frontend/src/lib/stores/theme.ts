import { writable, type Readable } from 'svelte/store';
import { setPreference as setPreferenceApi } from '$lib/api/preferences';

export type ThemeMode = 'light' | 'dark';

/** localStorage mirror key -- read synchronously by the inline script in `app.html` to avoid a flash of the wrong theme before hydration, and by this store at construction time. */
export const THEME_STORAGE_KEY = 'rendercv.uiTheme';

/** The `PUT /api/preferences` key this store persists to (Phase 5b task). */
export const THEME_PREFERENCE_KEY = 'ui_theme';

function isThemeMode(value: unknown): value is ThemeMode {
	return value === 'light' || value === 'dark';
}

export interface ThemeStoreDeps {
	/** Defaults to `window.localStorage` in the browser; `undefined` under SSR/tests unless injected. */
	storage?: Pick<Storage, 'getItem' | 'setItem'>;
	/** Defaults to a real `matchMedia('(prefers-color-scheme: dark)')` check in the browser. */
	prefersDark?: () => boolean;
	/** Defaults to toggling the `dark` class on `document.documentElement`. */
	applyToDocument?: (mode: ThemeMode) => void;
	/** Defaults to the real `PUT /api/preferences` client. */
	setPreference?: typeof setPreferenceApi;
}

export interface ThemeStore extends Readable<ThemeMode> {
	/** Flips light<->dark; persists to both the localStorage mirror and `PUT /api/preferences`. */
	toggle: () => void;
	/** Sets an explicit mode; same persistence as `toggle`. */
	set: (mode: ThemeMode) => void;
	/**
	 * Applies a value read from `GET /api/preferences` at bootstrap.
	 *
	 * Why this is not just `set`: preferences arrive asynchronously, after
	 * the store has already picked an initial mode from the localStorage
	 * mirror (or the OS preference) -- see the module doc comment. Calling
	 * `set` here would immediately write that same value straight back to
	 * `PUT /api/preferences`, which is both redundant traffic and a race
	 * with a legitimate concurrent write from another tab. This only
	 * updates local state (store + DOM class + localStorage mirror) and
	 * skips the network write.
	 */
	applyPersistedPreference: (value: string | undefined) => void;
}

function defaultStorage(): Pick<Storage, 'getItem' | 'setItem'> | undefined {
	if (typeof window === 'undefined') return undefined;
	try {
		return window.localStorage;
	} catch {
		// Storage access can throw (e.g. disabled in a locked-down browser context).
		return undefined;
	}
}

function defaultPrefersDark(): boolean {
	if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
	return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function defaultApplyToDocument(mode: ThemeMode): void {
	if (typeof document === 'undefined') return;
	document.documentElement.classList.toggle('dark', mode === 'dark');
}

/**
 * Two-state (light/dark) UI theme store. Initial value: the saved
 * `rendercv.uiTheme` localStorage mirror if present, else the OS
 * `prefers-color-scheme`. Applies/removes the `dark` class on `<html>` on
 * every change (Tailwind's `dark:` variant is configured class-based --
 * see `layout.css`'s `@custom-variant dark`).
 *
 * A factory (rather than only a module singleton) so the sync logic is
 * unit-testable with fakes for storage/matchMedia/DOM/network, matching
 * `createPreferenceWriter`'s pattern in `$lib/persistence/preferenceWriter.ts`.
 */
export function createThemeStore(deps: ThemeStoreDeps = {}): ThemeStore {
	const storage = deps.storage ?? defaultStorage();
	const prefersDark = deps.prefersDark ?? defaultPrefersDark;
	const applyToDocument = deps.applyToDocument ?? defaultApplyToDocument;
	const setPreference = deps.setPreference ?? setPreferenceApi;

	const stored = storage?.getItem(THEME_STORAGE_KEY);
	let mode: ThemeMode = isThemeMode(stored) ? stored : prefersDark() ? 'dark' : 'light';

	const { subscribe, set: setStore } = writable<ThemeMode>(mode);
	applyToDocument(mode);

	function persistLocal(next: ThemeMode): void {
		storage?.setItem(THEME_STORAGE_KEY, next);
	}

	function applyLocally(next: ThemeMode): void {
		mode = next;
		setStore(next);
		applyToDocument(next);
		persistLocal(next);
	}

	function set(next: ThemeMode): void {
		applyLocally(next);
		void setPreference(THEME_PREFERENCE_KEY, next);
	}

	function toggle(): void {
		set(mode === 'dark' ? 'light' : 'dark');
	}

	function applyPersistedPreference(value: string | undefined): void {
		if (!isThemeMode(value) || value === mode) return;
		applyLocally(value);
	}

	return { subscribe, toggle, set, applyPersistedPreference };
}

/** The app-wide singleton, used by `EditorPane`'s toggle button and bootstrap. */
export const theme = createThemeStore();

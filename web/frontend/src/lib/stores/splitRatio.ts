import { writable, type Readable } from 'svelte/store';
import { setPreference as setPreferenceApi } from '$lib/api/preferences';
import { DEFAULT_SPLIT_RATIO, clampSplitRatio, parseSplitRatio } from '$lib/layout/splitRatio';

/** localStorage mirror key -- read synchronously at construction so the split doesn't jump right after first paint, mirroring `$lib/stores/theme.ts`'s `THEME_STORAGE_KEY` pattern. */
export const SPLIT_RATIO_STORAGE_KEY = 'rendercv.splitRatio';

/** The `PUT /api/preferences` key this store persists to. */
export const SPLIT_RATIO_PREFERENCE_KEY = 'split_ratio';

export interface SplitRatioStoreDeps {
	/** Defaults to `window.localStorage` in the browser; `undefined` under SSR/tests unless injected. */
	storage?: Pick<Storage, 'getItem' | 'setItem'>;
	/** Defaults to the real `PUT /api/preferences` client. */
	setPreference?: typeof setPreferenceApi;
	/** Idle time after the last `set` before it's written to `PUT /api/preferences` -- dragging fires many updates a second. */
	debounceMs?: number;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
}

export interface SplitRatioStore extends Readable<number> {
	/** Sets a new ratio; persists to both the localStorage mirror (immediately) and `PUT /api/preferences` (debounced). */
	set: (ratio: number) => void;
	/**
	 * Applies a value read from `GET /api/preferences` at bootstrap without
	 * re-writing it back -- same rationale as `theme.ts`'s
	 * `applyPersistedPreference`: preferences arrive asynchronously, after
	 * this store already picked an initial value from the localStorage
	 * mirror (or the default).
	 */
	applyPersistedPreference: (value: string | undefined) => void;
	/** Cancels a pending debounced write (does not flush it). Call on unmount. */
	destroy: () => void;
}

function defaultStorage(): Pick<Storage, 'getItem' | 'setItem'> | undefined {
	if (typeof window === 'undefined') return undefined;
	try {
		return window.localStorage;
	} catch {
		return undefined;
	}
}

/**
 * The editor/preview split ratio (percentage the editor pane occupies),
 * persisted the same two-tier way as `$lib/stores/theme.ts`'s `ui_theme`:
 * a synchronous localStorage mirror for the initial value, plus a debounced
 * `PUT /api/preferences` write (debounced here, unlike theme's toggle,
 * because a drag can emit dozens of updates a second).
 */
export function createSplitRatioStore(deps: SplitRatioStoreDeps = {}): SplitRatioStore {
	const storage = deps.storage ?? defaultStorage();
	const setPreference = deps.setPreference ?? setPreferenceApi;
	const debounceMs = deps.debounceMs ?? 400;
	const setTimeoutFn = deps.setTimeoutFn ?? setTimeout;
	const clearTimeoutFn = deps.clearTimeoutFn ?? clearTimeout;

	const stored = storage?.getItem(SPLIT_RATIO_STORAGE_KEY);
	let ratio = stored !== null && stored !== undefined ? parseSplitRatio(stored) : DEFAULT_SPLIT_RATIO;

	const { subscribe, set: setStore } = writable<number>(ratio);

	let pendingWrite: ReturnType<typeof setTimeout> | undefined;

	function persistLocal(next: number): void {
		storage?.setItem(SPLIT_RATIO_STORAGE_KEY, String(next));
	}

	function schedulePreferenceWrite(next: number): void {
		if (pendingWrite) clearTimeoutFn(pendingWrite);
		pendingWrite = setTimeoutFn(() => {
			pendingWrite = undefined;
			void setPreference(SPLIT_RATIO_PREFERENCE_KEY, String(next));
		}, debounceMs);
	}

	function set(next: number): void {
		const clamped = clampSplitRatio(next);
		if (clamped === ratio) return;
		ratio = clamped;
		setStore(clamped);
		persistLocal(clamped);
		schedulePreferenceWrite(clamped);
	}

	function applyPersistedPreference(value: string | undefined): void {
		if (value === undefined) return;
		const parsed = parseSplitRatio(value);
		if (parsed === ratio) return;
		ratio = parsed;
		setStore(parsed);
		persistLocal(parsed);
	}

	function destroy(): void {
		if (pendingWrite) clearTimeoutFn(pendingWrite);
		pendingWrite = undefined;
	}

	return { subscribe, set, applyPersistedPreference, destroy };
}

/** The app-wide singleton, used by `+page.svelte` and `Splitter.svelte`. */
export const splitRatio = createSplitRatioStore();

/**
 * The client-side (Pyodide + typst.ts) preview path is off by default and is
 * opted into per-browser via localStorage, not a UI control (Phase 5a ships
 * the engine; a settings toggle is a later phase's job).
 *
 * Why localStorage and not a store: the flag must be readable before any
 * Svelte store/app code runs (e.g. from `renderController`'s default option
 * evaluation), and it must survive reloads without a network round trip.
 */
export const WASM_PREVIEW_FLAG_KEY = 'rendercv.wasmPreview';

/**
 * Reads the flag. Safe to call anywhere (SSR, tests without a DOM) -- returns
 * `false` whenever `localStorage` is unavailable or throws (e.g. disabled by
 * browser privacy settings).
 */
export function isWasmPreviewEnabled(): boolean {
	try {
		if (typeof localStorage === 'undefined') return false;
		return localStorage.getItem(WASM_PREVIEW_FLAG_KEY) === 'true';
	} catch {
		return false;
	}
}

/** Sets the flag. Exposed for manual testing/e2e (`e2e/wasm.spec.ts`) via `page.evaluate`. */
export function setWasmPreviewEnabled(enabled: boolean): void {
	try {
		if (typeof localStorage === 'undefined') return;
		if (enabled) {
			localStorage.setItem(WASM_PREVIEW_FLAG_KEY, 'true');
		} else {
			localStorage.removeItem(WASM_PREVIEW_FLAG_KEY);
		}
	} catch {
		// Ignore: same "unavailable storage" case as the getter.
	}
}

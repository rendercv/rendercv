import { setPreference as setPreferenceApi } from '$lib/api/preferences';

export interface PreferenceWriterOptions {
	/** Idle time after the last write to a given key before it's sent. */
	debounceMs?: number;
	setPreference?: typeof setPreferenceApi;
	setTimeoutFn?: typeof setTimeout;
	clearTimeoutFn?: typeof clearTimeout;
}

export interface PreferenceWriter {
	/** Debounced per-key: rapid writes to the same key coalesce into the last value. */
	write: (key: string, value: string) => void;
	/** Cancels all pending writes (does not flush them). */
	destroy: () => void;
}

/**
 * A generic debounced writer for `PUT /api/preferences`, one independent
 * debounce timer per key -- so writing `zoom` rapidly doesn't delay a
 * `sidebar_collapsed` write already in flight, and vice versa
 * (docs/plans/completed/cv-editor-web-app.md, Phase 4c: "persist last_cv_id,
 * sidebar_collapsed, yaml_mode, zoom via the API (debounce writes; read
 * once at bootstrap)").
 */
export function createPreferenceWriter(options: PreferenceWriterOptions = {}): PreferenceWriter {
	const {
		debounceMs = 500,
		setPreference = setPreferenceApi,
		setTimeoutFn = setTimeout,
		clearTimeoutFn = clearTimeout
	} = options;

	const timers = new Map<string, ReturnType<typeof setTimeout>>();

	function write(key: string, value: string): void {
		const existing = timers.get(key);
		if (existing) clearTimeoutFn(existing);
		timers.set(
			key,
			setTimeoutFn(() => {
				timers.delete(key);
				void setPreference(key, value);
			}, debounceMs)
		);
	}

	function destroy(): void {
		for (const timer of timers.values()) clearTimeoutFn(timer);
		timers.clear();
	}

	return { write, destroy };
}

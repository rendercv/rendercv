import { apiFetch } from '$lib/api/http';

/**
 * Client for `GET`/`PUT /api/preferences` (`rendercv_web/preferences.py`):
 * session-scoped `{key: value}` UI state (`last_cv_id`, `sidebar_collapsed`,
 * `yaml_mode`, `zoom`) read once at bootstrap and written back debounced
 * (see `$lib/persistence/preferenceWriter.ts`).
 */

/** `GET /api/preferences` -- every stored preference for the current session. */
export async function getPreferences(fetchImpl: typeof fetch = apiFetch): Promise<Record<string, string>> {
	const response = await fetchImpl('/api/preferences');
	if (!response.ok) throw new Error(`GET /api/preferences failed with status ${response.status}`);
	return (await response.json()) as Record<string, string>;
}

/** `PUT /api/preferences` -- upserts one key/value pair. */
export async function setPreference(
	key: string,
	value: string,
	fetchImpl: typeof fetch = apiFetch
): Promise<void> {
	const response = await fetchImpl('/api/preferences', {
		method: 'PUT',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ key, value })
	});
	if (response.status !== 204) {
		throw new Error(`PUT /api/preferences failed with status ${response.status}`);
	}
}

/**
 * Client for `GET /api/themes`: one entry per built-in theme, each carrying
 * that theme's full default design options (see `rendercv_web/themes.py`).
 *
 * Why cache alongside the schema: the design form's "effective value"
 * display (approved semantics — see the phase task) needs both the schema
 * (to build the field list) and this list (to know each field's
 * theme-dependent default) on every render; fetching once per session avoids
 * a request storm across every field.
 */

import { apiFetch } from '$lib/api/http';

export interface ThemeInfo {
	name: string;
	design_defaults: Record<string, unknown>;
}

let cached: ThemeInfo[] | null = null;
let inFlight: Promise<ThemeInfo[]> | null = null;

export async function fetchThemes(
	fetchImpl: typeof fetch = apiFetch,
	options: { force?: boolean } = {}
): Promise<ThemeInfo[]> {
	if (cached && !options.force) return cached;
	if (inFlight && !options.force) return inFlight;

	inFlight = (async () => {
		const response = await fetchImpl('/api/themes');
		if (!response.ok) {
			throw new Error(`GET /api/themes failed with status ${response.status}`);
		}
		const body = (await response.json()) as ThemeInfo[];
		cached = body;
		return body;
	})();

	try {
		return await inFlight;
	} finally {
		inFlight = null;
	}
}

/** Clears the cached theme list (tests only). */
export function resetThemesCache(): void {
	cached = null;
	inFlight = null;
}

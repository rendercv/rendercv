/**
 * The one shared `fetch` wrapper for every call this app makes to its own
 * backend.
 *
 * Why: the backend identifies a session purely via a signed HTTPOnly cookie
 * (`rendercv_web/auth.py`) -- every request MUST carry `credentials:
 * 'include'` or the browser will not send (or accept `Set-Cookie` for) it.
 * Centralizing this here means every API client module (`documents.ts`,
 * `render.ts`, `validate.ts`, `themes.ts`, `cvs.ts`, `preferences.ts`)
 * defaults its injectable `fetchImpl` to this function instead of repeating
 * `credentials: 'include'` at every call site.
 */
export function apiFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
	return fetch(input, { ...init, credentials: 'include' });
}

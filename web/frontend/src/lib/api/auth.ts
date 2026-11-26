import { apiFetch } from '$lib/api/http';

/**
 * Client for `/api/auth/*` (`rendercv_web/oauth.py`): who the current
 * session belongs to, and whether this deployment offers sign-in at all.
 *
 * Why sign-in itself is a plain link and not a function here: the OAuth
 * flow is a full-page browser redirect to Google, not a fetch. `fetch`ing
 * `/api/auth/google/start` would follow the redirect in the background and
 * accomplish nothing, so the UI navigates to it instead.
 */

/** Shape of `GET /api/auth/me`. */
export interface AuthStatus {
	authenticated: boolean;
	email: string | null;
	displayName: string | null;
	/** False when the server has no Google credentials configured -- hide the sign-in UI entirely. */
	providerAvailable: boolean;
}

interface AuthStatusPayload {
	authenticated: boolean;
	email: string | null;
	display_name: string | null;
	provider_available: boolean;
}

/** The address the "sign in" control navigates to; the backend redirects on to Google. */
export const GOOGLE_SIGN_IN_PATH = '/api/auth/google/start';

/**
 * `GET /api/auth/me` -- the current session's account state.
 *
 * Never throws: a failure here must not stop the editor from loading,
 * because the editor works perfectly well signed out. An unreachable or
 * erroring endpoint is reported as "anonymous, no provider", which renders
 * exactly like a deployment that has no sign-in configured.
 */
export async function getAuthStatus(fetchImpl: typeof fetch = apiFetch): Promise<AuthStatus> {
	try {
		const response = await fetchImpl('/api/auth/me');
		if (!response.ok) return signedOutStatus();
		const body = (await response.json()) as AuthStatusPayload;
		return {
			authenticated: body.authenticated,
			email: body.email,
			displayName: body.display_name,
			providerAvailable: body.provider_available
		};
	} catch {
		return signedOutStatus();
	}
}

/** `POST /api/auth/logout` -- clears the session cookie for this browser. */
export async function signOut(fetchImpl: typeof fetch = apiFetch): Promise<boolean> {
	const response = await fetchImpl('/api/auth/logout', { method: 'POST' });
	return response.status === 204;
}

/**
 * `DELETE /api/auth/me` -- erases the account and everything it owns.
 *
 * Why this returns a boolean rather than throwing: the caller has already
 * shown the user a confirmation and needs to know whether to send them
 * back to the landing page or leave them where they are with the account
 * intact. A thrown error would say the same thing less directly.
 */
export async function deleteAccount(fetchImpl: typeof fetch = apiFetch): Promise<boolean> {
	const response = await fetchImpl('/api/auth/me', { method: 'DELETE' });
	return response.status === 204;
}

function signedOutStatus(): AuthStatus {
	return { authenticated: false, email: null, displayName: null, providerAvailable: false };
}

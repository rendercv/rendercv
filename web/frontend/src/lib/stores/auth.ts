import { writable, type Readable } from 'svelte/store';
import {
	deleteAccount as deleteAccountApi,
	getAuthStatus,
	signOut as signOutApi,
	type AuthStatus
} from '$lib/api/auth';

/**
 * Who the current session belongs to, and whether this deployment offers
 * sign-in at all (`GET /api/auth/me`).
 *
 * Why it starts as "anonymous, no provider" rather than null or a loading
 * flag: that is exactly how a deployment without Google credentials looks,
 * and it is the state in which the UI shows no auth controls. So the first
 * paint -- before the status has been fetched -- renders the same as the
 * quietest possible answer, and the controls appear only once the server
 * has actually said they should. No flash of a sign-in button that then
 * vanishes, and no spinner for something nobody is waiting on.
 */
const UNKNOWN_STATUS: AuthStatus = {
	authenticated: false,
	email: null,
	displayName: null,
	providerAvailable: false
};

export interface AuthController {
	status: Readable<AuthStatus>;
	/** Fetches `/api/auth/me` and publishes it. Safe to call repeatedly. */
	refresh: () => Promise<void>;
	/** Signs this browser out, then refreshes so the UI follows. */
	signOut: () => Promise<void>;
	/** Erases the account and everything it owns. Resolves to whether it worked. */
	deleteAccount: () => Promise<boolean>;
}

export function createAuthController(
	deps: {
		fetchStatus?: typeof getAuthStatus;
		requestSignOut?: typeof signOutApi;
		requestDeleteAccount?: typeof deleteAccountApi;
	} = {}
): AuthController {
	const {
		fetchStatus = getAuthStatus,
		requestSignOut = signOutApi,
		requestDeleteAccount = deleteAccountApi
	} = deps;
	const status = writable<AuthStatus>(UNKNOWN_STATUS);

	async function refresh(): Promise<void> {
		// `getAuthStatus` never throws -- an unreachable endpoint resolves to
		// the anonymous status, which is the correct thing to render.
		status.set(await fetchStatus());
	}

	async function signOut(): Promise<void> {
		await requestSignOut();
		await refresh();
	}

	async function deleteAccount(): Promise<boolean> {
		const deleted = await requestDeleteAccount();
		// Only refresh on success. A failed delete leaves the account
		// intact, and re-reading the status would report it as still
		// signed in -- true, but easily read as the delete having worked
		// and the UI lagging.
		if (deleted) await refresh();
		return deleted;
	}

	return { status: { subscribe: status.subscribe }, refresh, signOut, deleteAccount };
}

/** The app-wide controller; components subscribe to `auth.status`. */
export const auth = createAuthController();

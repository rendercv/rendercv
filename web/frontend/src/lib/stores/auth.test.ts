import { describe, it, expect, vi } from 'vitest';
import { get } from 'svelte/store';
import { createAuthController } from './auth';
import type { AuthStatus } from '$lib/api/auth';

function status(overrides: Partial<AuthStatus> = {}): AuthStatus {
	return {
		authenticated: false,
		email: null,
		displayName: null,
		providerAvailable: true,
		...overrides
	};
}

describe('createAuthController', () => {
	it('starts with no provider so the first paint shows no auth controls', () => {
		const controller = createAuthController({ fetchStatus: vi.fn() });

		// Rendering "sign in" before the server has said sign-in exists would
		// flash a control that then vanishes on deployments without OAuth.
		expect(get(controller.status).providerAvailable).toBe(false);
		expect(get(controller.status).authenticated).toBe(false);
	});

	it('publishes the fetched status', async () => {
		const fetchStatus = vi.fn(async () =>
			status({ authenticated: true, email: 'a@b.c', displayName: 'A B' })
		);
		const controller = createAuthController({ fetchStatus });

		await controller.refresh();

		expect(get(controller.status)).toEqual({
			authenticated: true,
			email: 'a@b.c',
			displayName: 'A B',
			providerAvailable: true
		});
	});

	it('signs out and refreshes so the UI follows in one step', async () => {
		const responses = [
			status({ authenticated: true, email: 'a@b.c' }),
			status({ authenticated: false })
		];
		const fetchStatus = vi.fn(async () => responses.shift() ?? status());
		const requestSignOut = vi.fn(async () => true);
		const controller = createAuthController({ fetchStatus, requestSignOut });
		await controller.refresh();
		expect(get(controller.status).authenticated).toBe(true);

		await controller.signOut();

		expect(requestSignOut).toHaveBeenCalledTimes(1);
		expect(get(controller.status).authenticated).toBe(false);
	});

	it('a failing status request leaves the app rendering as signed out', async () => {
		// `getAuthStatus` absorbs errors, so this asserts the contract the
		// controller relies on: refresh() must not reject and take the
		// editor's onMount down with it.
		const fetchStatus = vi.fn(async () => status({ providerAvailable: false }));
		const controller = createAuthController({ fetchStatus });

		await expect(controller.refresh()).resolves.toBeUndefined();

		expect(get(controller.status).providerAvailable).toBe(false);
	});
});

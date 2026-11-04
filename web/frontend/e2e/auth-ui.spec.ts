import { test, expect } from './fixtures';
import type { Page } from '@playwright/test';
import { gotoReady } from './helpers';

/**
 * What the auth controls render in each state the server can report, and
 * what `/app` does with someone who has no account.
 *
 * Why `/api/auth/me` is intercepted in most of these rather than really
 * signing in: the real flow ends at Google's consent screen, which a test
 * cannot drive and which needs credentials this repository does not have.
 * The backend half -- state checking, account resolution, the anonymous
 * merge -- is covered for real in `web/backend/tests/test_auth_api.py`.
 * What is left to prove here is that the UI renders the right thing for
 * each answer, and that is exactly what the interception fixes.
 *
 * Every case is intercepted, including the unconfigured one. Reading the
 * backend's real answer there would make the suite pass or fail based on
 * whether the person running it happens to have Google configured in their
 * own `.env`, which is not a property of the code under test.
 *
 * The one case that is *not* intercepted is the last describe block: a
 * browser arriving with no session cookie at all. Nothing is faked there,
 * because the point is what the real server does with a real stranger.
 */

async function serveAuthStatus(
	page: Page,
	body: {
		authenticated: boolean;
		email: string | null;
		display_name: string | null;
		provider_available: boolean;
	}
): Promise<void> {
	await page.route('**/api/auth/me', (route) =>
		route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
	);
}

test.describe('Auth controls', () => {
	test('a deployment without Google credentials cannot be entered at all', async ({ page }) => {
		// Intercepted like the others rather than relying on the backend's own
		// answer: a developer who has configured Google locally would
		// otherwise fail this test purely because of their `.env`, which is
		// not something the suite should have an opinion about. That the
		// server really does report `provider_available: false` when the
		// credentials are unset is covered where it belongs, in
		// `web/backend/tests/test_auth_api.py`.
		await serveAuthStatus(page, {
			authenticated: false,
			email: null,
			display_name: null,
			provider_available: false
		});

		await page.goto('/');
		await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Sign in' })).toHaveCount(0);

		await page.goto('/app');

		// No dead sign-in button: with no provider there is nothing to press,
		// so the gate names the missing configuration instead.
		await expect(page.getByRole('heading', { name: 'Sign-in is not configured' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Sign in with Google' })).toHaveCount(0);
	});

	test('when sign-in is available the landing page offers it', async ({ page }) => {
		await serveAuthStatus(page, {
			authenticated: false,
			email: null,
			display_name: null,
			provider_available: true
		});

		await page.goto('/');

		const signIn = page.getByRole('link', { name: 'Sign in' });
		await expect(signIn).toBeVisible();
		await expect(signIn).toHaveAttribute('href', '/api/auth/google/start');
	});

	test('the editor is gated behind sign-in, not merely decorated with it', async ({ page }) => {
		await serveAuthStatus(page, {
			authenticated: false,
			email: null,
			display_name: null,
			provider_available: true
		});

		await page.goto('/app');

		const signIn = page.getByRole('link', { name: 'Sign in with Google' });
		await expect(signIn).toBeVisible();
		await expect(signIn).toHaveAttribute('href', '/api/auth/google/start');

		// The editor itself must be absent, not just hidden behind an
		// overlay -- its controls would otherwise still be reachable by
		// keyboard, and every one of them would 401.
		await expect(page.getByRole('button', { name: 'Create new CV' })).toHaveCount(0);
		await expect(page.getByTitle('CV PDF preview')).toHaveCount(0);
	});

	test('someone already signed in is not sent back through Google', async ({ page }) => {
		// Offering "Sign in" to a live session is not just a redundant
		// control: following it re-runs the whole authorization-code flow,
		// and `/google/start` sends `prompt=select_account` (which is what
		// makes switching accounts possible), so it puts Google's account
		// chooser in front of someone who only wanted the editor. The way
		// in for them is the editor link, which needs no round trip.
		await serveAuthStatus(page, {
			authenticated: true,
			email: 'person@example.com',
			display_name: 'A Person',
			provider_available: true
		});

		await page.goto('/');

		await expect(page.getByRole('link', { name: 'Sign in' })).toHaveCount(0);
		await expect(page.getByTestId('signed-in-as')).toHaveText('A Person');
		await expect(page.getByRole('link', { name: 'Open the editor' }).first()).toHaveAttribute(
			'href',
			'/app'
		);
	});

	test('the editor link goes straight in for a signed-in visitor', async ({ page }) => {
		// End to end on the real session rather than an intercepted status:
		// landing page, one click, editor -- no Google, no gate.
		await page.goto('/');
		await page.getByRole('link', { name: 'Open the editor' }).first().click();

		await expect(page.locator('[data-app-ready="true"]')).toHaveCount(1, { timeout: 15_000 });
		await expect(page.getByRole('heading', { name: 'Sign in to open the editor' })).toHaveCount(0);
	});

	test('the editor sidebar shows who is signed in, and a way out', async ({ page }) => {
		await serveAuthStatus(page, {
			authenticated: true,
			email: 'person@example.com',
			display_name: 'A Person',
			provider_available: true
		});

		await gotoReady(page);

		await expect(page.getByText('A Person')).toBeVisible();
		await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Sign in with Google' })).toHaveCount(0);
	});

	test('signing out posts to the backend and returns to the gate', async ({ page }) => {
		await serveAuthStatus(page, {
			authenticated: true,
			email: 'person@example.com',
			display_name: 'A Person',
			provider_available: true
		});
		let logoutCalls = 0;
		await page.route('**/api/auth/logout', (route) => {
			logoutCalls += 1;
			return route.fulfill({ status: 204, body: '' });
		});

		await gotoReady(page);
		// The reload after signing out must see the signed-out answer, or the
		// page would come back still showing the account.
		await serveAuthStatus(page, {
			authenticated: false,
			email: null,
			display_name: null,
			provider_available: true
		});
		await page.getByRole('button', { name: 'Sign out' }).click();

		await expect(page.getByRole('link', { name: 'Sign in with Google' })).toBeVisible();
		expect(logoutCalls).toBe(1);
	});
});

test.describe('Deleting an account', () => {
	// `/api/auth/me` is intercepted only so the account strip renders: the
	// suite's backend runs without Google credentials, so it reports
	// `provider_available: false` and `AccountMenu` draws nothing at all.
	// The deletion itself is real -- `DELETE /api/auth/me` is a different
	// route and reaches the server, against the account this test owns
	// (see `e2e/fixtures.ts`), so erasing it cannot disturb another test.
	test.beforeEach(async ({ page }) => {
		await page.route('**/api/auth/me', (route) => {
			if (route.request().method() !== 'GET') return route.fallback();
			return route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					authenticated: true,
					email: 'person@example.com',
					display_name: 'A Person',
					provider_available: true
				})
			});
		});
	});

	test('the control asks before doing anything', async ({ page }) => {
		await gotoReady(page);

		await page.getByRole('button', { name: 'Delete account' }).click();

		const dialog = page.getByRole('alertdialog', { name: 'Delete account?' });
		await expect(dialog).toBeVisible();
		// The dialog has to say what goes, not just ask twice.
		await expect(dialog).toContainText(/version history/i);
		await expect(dialog).toContainText(/cannot be undone/i);
	});

	test('cancelling leaves the account and its CVs alone', async ({ page }) => {
		// The failure this guards against is the worst one available here:
		// a mis-wired cancel that deletes anyway. Nothing would report it,
		// and the data would be gone.
		await gotoReady(page);

		await page.getByRole('button', { name: 'Delete account' }).click();
		await page.getByRole('button', { name: 'Cancel' }).click();

		await expect(page.getByRole('alertdialog')).toHaveCount(0);
		expect((await page.request.get('/api/cvs')).status()).toBe(200);

		// Still usable after the near miss, not merely still authenticated.
		await page.reload();
		await expect(page.locator('[data-app-ready="true"]')).toHaveCount(1, { timeout: 15_000 });
	});

	test('confirming erases the account and returns to the landing page', async ({ page }) => {
		await gotoReady(page);
		expect((await page.request.get('/api/cvs')).status()).toBe(200);

		await page.getByRole('button', { name: 'Delete account' }).click();
		await page.getByRole('button', { name: 'Delete account', exact: true }).last().click();

		await expect(page).toHaveURL(/\/$/, { timeout: 15_000 });
		// The session is gone, not just the page: the same cookie now buys
		// nothing. Asserted against `/api/cvs`, which this file does not
		// intercept, so the answer comes from the server.
		expect((await page.request.get('/api/cvs')).status()).toBe(401);
	});
});

test.describe('A browser with no session at all', () => {
	// Nothing intercepted and no seeded cookie: this is the real server
	// answering a real stranger, which is the only way to prove the gate is
	// backed by the API refusing rather than by the UI choosing to hide.
	test.use({ signedIn: false });

	test('is sent to the gate instead of the editor', async ({ page }) => {
		await page.goto('/app');

		await expect(page.getByRole('heading', { name: /Sign in to open the editor|Sign-in is not configured/ })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Create new CV' })).toHaveCount(0);
	});

	test('is refused by the CV and preference endpoints', async ({ page }) => {
		const cvs = await page.request.get('/api/cvs');
		expect(cvs.status()).toBe(401);

		const preferences = await page.request.get('/api/preferences');
		expect(preferences.status()).toBe(401);
	});

	test('can still read the public endpoints the landing page needs', async ({ page }) => {
		// The gate is on the user's data, not on the app. Locking these too
		// would break the landing page for visitors who have not signed in --
		// exactly the people it exists for.
		expect((await page.request.get('/api/themes')).status()).toBe(200);
		expect((await page.request.get('/api/auth/me')).status()).toBe(200);
	});
});

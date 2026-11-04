import { test as base, expect } from '@playwright/test';
import { appendFileSync, readFileSync, writeFileSync } from 'node:fs';
import {
	ACCOUNT_CURSOR_PATH,
	ACCOUNT_POOL_SIZE,
	SESSION_COOKIE_NAME,
	cookieForAccount
} from './testAccount';

/**
 * The `test` every spec in this suite imports, instead of Playwright's.
 *
 * It does one thing Playwright's does not: put a signed-in session cookie
 * on the browser context before the test body runs, taking the next
 * account from the pool `globalSetup` seeded. Since the editor became
 * account-only, a context without one lands on the sign-in gate and never
 * reaches anything a spec is trying to test.
 *
 * Why a fixture rather than `storageState` in the config: `storageState`
 * is one fixed state shared by every test, and these tests need an account
 * each -- see `testAccount.ts`. The fixture also gives specs an explicit
 * way to opt out (`test.use({ signedIn: false })`) for the cases that are
 * *about* not being signed in.
 */

/**
 * Hands out the next unused pool index, counting on disk rather than in
 * memory.
 *
 * Why not a module-level variable, which is what this was: Playwright
 * restarts its worker after a test fails, and a restart re-imports this
 * module and resets the count to zero. Every test after the first failure
 * then gets an account an earlier test had already written CVs into --
 * so one genuine failure turned into a cascade of unrelated ones, each
 * looking like a real bug in whatever spec happened to run next. That was
 * observed: a broken theme switcher produced three further failures in
 * two other files, and all three passed when run alone.
 *
 * A file survives the restart. `workers: 1` (see `playwright.config.ts`)
 * means there is no concurrent reader to race with.
 *
 * @returns The index of an account no other test in this run has used.
 */
function claimAccount(): number {
	let used = 0;
	try {
		used = readFileSync(ACCOUNT_CURSOR_PATH, 'utf8').length;
	} catch {
		// First test of the run; the file does not exist yet.
	}
	appendFileSync(ACCOUNT_CURSOR_PATH, '.');
	return used;
}

/** Clears the cursor so each run starts from the first account again. */
export function resetAccountCursor(): void {
	writeFileSync(ACCOUNT_CURSOR_PATH, '');
}

export const test = base.extend<{ signedIn: boolean; account: number }>({
	// Opt out with `test.use({ signedIn: false })` in a describe block.
	signedIn: [true, { option: true }],

	/**
	 * The pool index this test owns. Exposed so a spec can tell two
	 * contexts apart when it deliberately needs the same account twice.
	 */
	account: [
		// eslint-disable-next-line no-empty-pattern
		async ({}, use) => {
			const index = claimAccount();
			if (index >= ACCOUNT_POOL_SIZE) {
				throw new Error(
					`e2e account pool exhausted (${ACCOUNT_POOL_SIZE}); raise ACCOUNT_POOL_SIZE in e2e/testAccount.ts`
				);
			}
			await use(index);
		},
		{ scope: 'test' }
	],

	context: async ({ context, signedIn, account }, use) => {
		if (signedIn) {
			await context.addCookies([
				{
					name: SESSION_COOKIE_NAME,
					value: cookieForAccount(account),
					domain: 'localhost',
					path: '/',
					httpOnly: true,
					secure: false,
					sameSite: 'Lax'
				}
			]);
		}
		await use(context);
	}
});

export { expect };

import { request as playwrightRequest, type APIRequestContext } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { resetAccountCursor } from './fixtures';
import { ACCOUNT_POOL_SIZE, DATABASE_URL, TEST_SECRET } from './testAccount';

const PORT = 5199;
const BASE_URL = `http://localhost:${PORT}`;
const MAX_WAIT_MS = 60_000;
const POLL_INTERVAL_MS = 500;

async function waitUntilReachable(context: APIRequestContext): Promise<void> {
	const deadline = Date.now() + MAX_WAIT_MS;
	while (Date.now() < deadline) {
		try {
			await context.get('/');
			return;
		} catch {
			await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
		}
	}
}

/**
 * Creates the pool of accounts the tests sign in as.
 *
 * The rows are written by `e2e/seedAccount.py`, running production
 * repository code against the throwaway database Playwright started the
 * backend on -- see `e2e/testAccount.ts` for why they are not created by
 * signing in for real, and `e2e/fixtures.ts` for how a test picks one.
 */
function seedAccountPool(): void {
	const here = dirname(fileURLToPath(import.meta.url));

	execFileSync(
		'uv',
		['run', '--frozen', 'python', join(here, 'seedAccount.py'), String(ACCOUNT_POOL_SIZE)],
		{
			cwd: join(here, '..', '..', 'backend'),
			env: {
				...process.env,
				RENDERCV_WEB_DATABASE_URL: DATABASE_URL,
				RENDERCV_WEB_SECRET: TEST_SECRET
			},
			stdio: 'inherit'
		}
	);
}

/**
 * Prepares everything that must exist before the first test runs.
 *
 * Two jobs, both one-time costs the suite should not charge to whichever
 * test happens to go first:
 *
 * 1. Seeding the account pool. Every spec but the signed-out ones takes
 *    an account from it, and the rows must exist before the first test
 *    puts one of their cookies on a browser context.
 *
 * 2. Warming the backend's first Typst render -- a freshly-started
 *    `uvicorn` pays a one-time cost there (font loading, Python import
 *    warm-up, first-call overhead in the `typst` bindings) on top of
 *    whatever a test asks for. Without this, whichever test ran first
 *    absorbed it and could push its own generous wait past its timeout;
 *    observed directly as an otherwise-stable suite failing only its first
 *    test immediately after a backend restart.
 *
 * The warm-up polls for reachability first rather than assuming the
 * `webServer` entries are already up: Playwright's `globalSetup` vs
 * `webServer` start order is not a contract this file should depend on.
 */
export default async function globalSetup(): Promise<void> {
	seedAccountPool();
	// The cursor is a file, so last run's would otherwise carry over and
	// start this one part-way through the pool.
	resetAccountCursor();

	const context = await playwrightRequest.newContext({ baseURL: BASE_URL });
	try {
		await waitUntilReachable(context);
		await context.post('/api/render', {
			data: {
				cv_yaml: 'cv:\n  name: Warmup\n  sections: {}\n',
				design_yaml: '',
				locale_yaml: '',
				settings_yaml: ''
			},
			timeout: 60_000
		});
	} catch {
		// Best-effort only: if the backend never became reachable (or this
		// warmup call itself fails), every test's own wait is still the
		// authoritative check -- this is a latency optimization, not a
		// correctness dependency.
	} finally {
		await context.dispose();
	}
}

import { defineConfig, devices } from '@playwright/test';
import { BACKEND_PORT, DATABASE_URL, TEST_SECRET } from './e2e/testAccount';

const PORT = 5199;
const BASE_URL = `http://localhost:${PORT}`;

/**
 * Playwright config for the Phase 1 edit -> preview loop.
 *
 * Why its own port: the orchestrator may already have a dev server on 5173
 * (or 8000 for the backend); this spins up an isolated instance on 5199 so
 * tests never fight over a shared port, and tears it down when done.
 *
 * Why `workers: 1` and `globalSetup` (Phase 4c follow-up -- two separate
 * backend-capacity issues, found by re-running the same suite against a
 * freshly-restarted backend at successively lower worker counts):
 *
 * 1. The backend is a single uvicorn process. Its renders run in a bounded
 *    4-thread pool (`rendercv_web/app.py`), but Typst/Jinja2 templating is
 *    CPU-bound pure Python -- under CPython's GIL, several of those threads
 *    working at once can stall the *same process's* asyncio event loop
 *    handling `/api/validate` and bootstrap's own requests, even though
 *    they're different endpoints/pools. At the default local parallelism
 *    (4 browser contexts on an 8-core machine, each issuing its own
 *    bootstrap + render + validate calls), that showed up as occasional
 *    12/13 runs with a different test timing out each time. `workers: 1`
 *    fully serializes e2e runs against this single-process dev backend.
 * 2. Independent of parallelism: a *freshly-started* backend's very first
 *    `/api/render` pays a one-time cost (font loading, Python import
 *    warm-up) that a mid-session render doesn't -- observed even at
 *    `workers: 1`, always on the first test to touch a just-restarted
 *    backend. `globalSetup` (`e2e/global-setup.ts`) absorbs that cost with
 *    its own long timeout before any test runs, instead of it eating into
 *    an individual test's budget.
 */
export default defineConfig({
	testDir: './e2e',
	globalSetup: './e2e/global-setup.ts',
	timeout: 30_000,
	expect: { timeout: 10_000 },
	fullyParallel: false,
	workers: 1,
	retries: 0,
	reporter: [['list']],
	use: {
		baseURL: BASE_URL,
		trace: 'retain-on-failure',
		screenshot: 'only-on-failure'
	},
	// Both servers are the suite's own. Why the backend moved in here from
	// a terminal the runner had to remember to open: it has to be started
	// with a throwaway database and a known signing secret, and asking a
	// person to do that by hand meant a mistake wrote e2e CVs into their
	// real database. Playwright now owns both, and `npx playwright test`
	// is the whole command again.
	webServer: [
		{
			command: `uv run --frozen uvicorn rendercv_web.app:app --port ${BACKEND_PORT}`,
			cwd: '../backend',
			url: `http://localhost:${BACKEND_PORT}/api/themes`,
			reuseExistingServer: false,
			timeout: 120_000,
			env: {
				RENDERCV_WEB_DATABASE_URL: DATABASE_URL,
				RENDERCV_WEB_SECRET: TEST_SECRET
			}
		},
		{
			command: `npm run dev -- --port ${PORT} --strictPort`,
			url: BASE_URL,
			reuseExistingServer: false,
			timeout: 60_000,
			env: { RENDERCV_API_TARGET: `http://localhost:${BACKEND_PORT}` }
		}
	],
	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] }
		}
	]
});

import { createHmac } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

/**
 * The accounts the e2e suite runs as, and the wiring that makes them exist.
 *
 * Why the suite needs accounts at all: `/api/cvs` and `/api/preferences`
 * refuse callers without one, so a browser context with no session cookie
 * gets the sign-in gate instead of the editor.
 *
 * Why one account per test rather than one for the suite: every spec is
 * written as if it were a new visitor -- an empty CV list that bootstrap
 * fills with a fresh default CV. That used to come for free, because a new
 * browser context meant a new anonymous session. A single shared account
 * would carry one test's edits into the next.
 *
 * Why the sessions are minted here rather than by signing in for real: the
 * real flow ends at Google's consent screen, which a test cannot drive.
 * The alternative -- a test-only login endpoint on the server -- would be
 * an authentication bypass living in production code, one deployment
 * misconfiguration away from being reachable by anyone. Nothing on the
 * server knows this file exists; it builds the same signed cookie the
 * server would have issued, against a database only this suite uses.
 */

/** Port the suite's own backend listens on, deliberately not the dev 8000. */
export const BACKEND_PORT = 8100;

/** Signing secret for the suite's backend. Only ever used against it. */
export const TEST_SECRET = 'e2e-only-secret';

/**
 * Throwaway database, so a run can never touch real CVs.
 *
 * The file outlives the run, and deliberately is not deleted between
 * runs: Playwright starts the backend on it before `globalSetup` gets to
 * act, and re-imports this config in worker processes, so anything that
 * deletes the file would fire again mid-run and pull it out from under
 * the live server. The pool accounts are emptied instead, by
 * `e2e/seedAccount.py` -- see the note there.
 */
export const DATABASE_URL = `sqlite:///${join(tmpdir(), 'rendercv-e2e.db')}`;

/**
 * Where the suite records how many pool accounts it has handed out.
 *
 * On disk rather than in memory because Playwright restarts its worker
 * after a failure, which would reset an in-process counter and start
 * reissuing accounts earlier tests had already dirtied. `globalSetup`
 * truncates it at the start of every run.
 */
export const ACCOUNT_CURSOR_PATH = join(tmpdir(), 'rendercv-e2e-accounts-used');

/**
 * How many accounts `globalSetup` creates up front.
 *
 * Comfortably above the number of tests: they cost a row each, and running
 * out would silently start sharing accounts between tests, which is the
 * exact failure this pool exists to prevent.
 */
export const ACCOUNT_POOL_SIZE = 200;

/** The session cookie's name, matching `auth.SESSION_COOKIE_NAME`. */
export const SESSION_COOKIE_NAME = 'rendercv_session';

/**
 * The signed cookie value for pool account `index`.
 *
 * Mirrors `auth.encode_cookie`: the token, a dot, and its HMAC-SHA256
 * signature in hex.
 *
 * @param index Position in the pool, below `ACCOUNT_POOL_SIZE`.
 * @returns The cookie value the server will accept for that account.
 */
export function cookieForAccount(index: number): string {
	const token = `e2e-token-${index}`;
	const signature = createHmac('sha256', TEST_SECRET).update(token).digest('hex');
	return `${token}.${signature}`;
}

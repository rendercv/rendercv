import { expect, type Page } from '@playwright/test';

/**
 * Waits for the PDF preview iframe to have a `blob:` URL, returning it.
 *
 * Why a generous 25s timeout (previously 15s, duplicated per spec file):
 * the backend renders through a bounded thread pool (4 workers --
 * `rendercv_web/app.py`) shared by every parallel Playwright worker's
 * browser context; under a cold backend start plus several e2e workers
 * each issuing a handful of renders in quick succession (bootstrap's own
 * first render, then each test's edits), a render can legitimately queue
 * for several seconds without anything being wrong -- the server itself
 * only gives up after 30s (`RENDER_TIMEOUT_SECONDS`). 25s leaves headroom
 * under that without masking a genuine hang.
 */
export async function firstPreviewUrl(page: Page): Promise<string> {
	const iframe = page.getByTitle('CV PDF preview');
	await expect(iframe).toHaveAttribute('src', /^blob:/, { timeout: 25_000 });
	return (await iframe.getAttribute('src')) ?? '';
}

/**
 * Navigates to the app and waits for it to be fully ready: bootstrap
 * (`GET /api/cvs` -> create-if-empty -> load its documents, plus initial
 * preferences) has completed and the real CV is in the `documents` store.
 *
 * Why not just wait for the preview iframe's `src` to look like a blob URL
 * (the old, pre-persistence readiness check): the render/validate
 * controllers only start reacting to `documents` once bootstrap seeds it
 * (see `+page.svelte`), so nothing renders at all until bootstrap is done --
 * but relying on that as an implicit readiness signal is exactly the kind
 * of coupling that caused cross-test e2e flakiness once bootstrap became
 * async (docs/plans/completed/cv-editor-web-app.md, Phase 4c follow-up): it's
 * indirect, and a future change to the render pipeline could silently
 * reintroduce a race. `+page.svelte` sets `data-app-ready="true"` on its
 * root element as an explicit, single-purpose signal for exactly this --
 * every spec should wait on it before interacting with the page.
 */
export async function gotoReady(page: Page, path = '/app'): Promise<void> {
	await page.goto(path);
	await expect(page.locator('[data-app-ready="true"]')).toHaveCount(1, { timeout: 15_000 });
}

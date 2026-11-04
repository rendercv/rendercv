import { test, expect } from './fixtures';
import { gotoReady } from './helpers';

/**
 * The sidebar collapse toggle.
 *
 * Why this measures the rendered width rather than the class: the control
 * shipped broken precisely because its *state* was right and its *layout*
 * was not. The class flipped to `w-12`, the contents hid, and the
 * preference persisted -- while the rail stayed at its full 256px, because
 * a flex item's default `min-width: auto` floors it at its content width
 * and silently defeats the width utility. Asserting on the class would
 * have passed against the broken build, so these assertions read the box
 * the user actually sees.
 */

const EXPANDED_WIDTH = 256; // w-64
const COLLAPSED_WIDTH = 48; // w-12

function sidebar(page: import('@playwright/test').Page) {
	return page.getByRole('complementary', { name: 'CV list' });
}

function toggle(page: import('@playwright/test').Page) {
	return page.getByRole('button', { name: /collapse sidebar|expand sidebar/i });
}

async function sidebarWidth(page: import('@playwright/test').Page): Promise<number> {
	const box = await sidebar(page).boundingBox();
	if (!box) throw new Error('sidebar not found');
	return box.width;
}

test.describe('Sidebar collapse', () => {
	test.beforeEach(async ({ page }) => {
		// Start from the expanded default, ignoring any persisted preference.
		await page.addInitScript(() => window.localStorage.removeItem('rendercv.sidebarCollapsed'));
	});

	test('collapsing actually narrows the rail, not just its state', async ({ page }) => {
		await gotoReady(page);
		expect(await sidebarWidth(page)).toBeCloseTo(EXPANDED_WIDTH, -1);

		await toggle(page).click();

		// The transition is 150ms; poll rather than sampling once.
		await expect
			.poll(() => sidebarWidth(page), { timeout: 5000 })
			.toBeLessThan(EXPANDED_WIDTH / 2);
		expect(await sidebarWidth(page)).toBeCloseTo(COLLAPSED_WIDTH, -1);
	});

	test('expanding again restores the full width', async ({ page }) => {
		await gotoReady(page);

		await toggle(page).click();
		await expect.poll(() => sidebarWidth(page), { timeout: 5000 }).toBeLessThan(100);

		await toggle(page).click();

		await expect
			.poll(() => sidebarWidth(page), { timeout: 5000 })
			.toBeGreaterThan(EXPANDED_WIDTH - 20);
	});

	test('the collapsed rail hides the CV list but keeps the brand mark', async ({ page }) => {
		await gotoReady(page);
		await expect(page.getByRole('button', { name: 'Create new CV' })).toBeVisible();

		await toggle(page).click();

		await expect(page.getByRole('button', { name: 'Create new CV' })).toBeHidden();
		// The rail is still there -- collapsed, not removed.
		await expect(sidebar(page)).toBeVisible();
	});

	test('the collapsed state survives a reload', async ({ page }) => {
		await gotoReady(page);

		// The preference write is debounced by 500ms (`preferenceWriter`), so
		// the reload has to wait for it to actually reach the server. Without
		// this the test reloads a fraction of a second too early and reads a
		// server that was never told -- a race in the test, not in the app.
		// Match the sidebar write specifically: bootstrap also PUTs `zoom` and
		// `yaml_mode`, and waiting on "any preference write" would resolve on
		// one of those instead.
		const saved = page.waitForResponse(
			(response) =>
				response.url().includes('/api/preferences') &&
				response.request().method() === 'PUT' &&
				(response.request().postData() ?? '').includes('sidebar_collapsed')
		);
		await toggle(page).click();
		await expect.poll(() => sidebarWidth(page), { timeout: 5000 }).toBeLessThan(100);
		await saved;

		await gotoReady(page);

		await expect.poll(() => sidebarWidth(page), { timeout: 5000 }).toBeLessThan(100);
	});
});

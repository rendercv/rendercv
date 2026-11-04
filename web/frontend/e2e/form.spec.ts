import { test, expect } from './fixtures';
import type { Page } from '@playwright/test';
import { gotoReady } from './helpers';

/**
 * End-to-end coverage for the Phase 2 schema-driven form editor: the YAML
 * toggle's CV-tab form view, editing a header field, and adding a section
 * entry -- each round-tripping through `/api/documents/parse` +
 * `/api/documents/patch`.
 *
 * Why this file self-skips instead of asserting failure: those two
 * endpoints are being built in parallel by another block and were NOT live
 * when this file was written. A `beforeAll` probe checks for them once and
 * every test in this file calls `test.skip()` if they 404, so this spec
 * never fails CI before the two blocks are integrated -- see the phase
 * task. `e2e/editor.spec.ts` (the Phase 1 YAML-only loop) is unaffected and
 * keeps running unconditionally.
 */

let formEndpointsLive = false;

test.beforeAll(async ({ request }) => {
	const response = await request.post('/api/documents/parse', {
		data: { yaml: 'cv:\n  name: Probe\n' },
		failOnStatusCode: false
	});
	formEndpointsLive = response.status() !== 404;
});

async function switchToFormMode(page: Page): Promise<void> {
	await gotoReady(page);

	// Wait for the app to actually be interactive before clicking anything.
	// Why: on a cold dev-server start, SvelteKit's client bundle can take a
	// few seconds to finish hydrating; a click that lands in that window is
	// silently lost (the DOM exists, but no listener is attached yet). The
	// first successful preview render is a reliable "hydration is done and
	// reactivity is live" signal, exactly like `editor.spec.ts`'s own
	// `firstPreviewUrl` helper.
	await expect(page.getByTitle('CV PDF preview')).toHaveAttribute('src', /^blob:/, { timeout: 15_000 });

	const toggle = page.getByRole('switch', { name: 'Toggle YAML editor' });
	await expect(toggle).toHaveAttribute('aria-checked', 'true');
	await toggle.click();
	await expect(toggle).toHaveAttribute('aria-checked', 'false', { timeout: 5_000 });
}

test.describe('CV form editor (schema-driven, CV tab)', () => {
	test.beforeEach(() => {
		test.skip(!formEndpointsLive, '/api/documents/{parse,patch} are not live yet in this environment.');
	});

	test('YAML toggle OFF shows the schema-driven form with the seeded name field', async ({ page }) => {
		await switchToFormMode(page);

		const nameInput = page.getByLabel('Name', { exact: true });
		await expect(nameInput).toHaveValue('John Doe');
	});

	test('editing a header field patches the document and the YAML view reflects it on toggle back', async ({
		page
	}) => {
		await switchToFormMode(page);

		const nameInput = page.getByLabel('Name', { exact: true });
		await nameInput.fill('Jane Doe');
		await nameInput.blur();

		// Give the 300ms form-sync debounce + patch round trip time to land.
		await expect
			.poll(async () => nameInput.inputValue(), { timeout: 5_000 })
			.toBe('Jane Doe');

		await page.getByRole('switch', { name: 'Toggle YAML editor' }).click();
		await expect(page.locator('.cm-content')).toContainText('Jane Doe', { timeout: 5_000 });
	});

	test('adding a section and its first entry via the type picker', async ({ page }) => {
		await switchToFormMode(page);

		await page.getByLabel('New section title').fill('Experience');
		await page.getByRole('button', { name: '+ Add section' }).click();

		const section = page.locator('section[aria-label="Section: Experience"]');
		await expect(section).toBeVisible({ timeout: 5_000 });

		await section.getByRole('radio', { name: /Experience/ }).click();

		// Not `exact: true`: the label's accessible name includes the "required"
		// marker span right after "Company", so a substring match is the
		// reliable check here (see FieldRow.svelte's label markup).
		await expect(section.getByLabel('Company')).toBeVisible({ timeout: 5_000 });
	});

	test('markdown fields say what formatting they accept, once per list', async ({ page }) => {
		// Nothing else in the UI tells a form user this: the schema never
		// mentions it, and the B/I/link toolbar buttons are disabled outside
		// YAML mode, which if anything implies the opposite.
		await switchToFormMode(page);

		await page.getByLabel('New section title').fill('Experience');
		await page.getByRole('button', { name: '+ Add section' }).click();

		const section = page.locator('section[aria-label="Section: Experience"]');
		await expect(section).toBeVisible({ timeout: 5_000 });
		await section.getByRole('radio', { name: /Experience/ }).click();
		await expect(section.getByLabel('Company')).toBeVisible({ timeout: 5_000 });

		const hint = section.getByText(/Supports inline Markdown/);
		await expect(hint.first()).toBeVisible({ timeout: 10_000 });

		// Highlights is an array: one editable field per bullet. The hint
		// belongs to the list, so adding bullets must not multiply it.
		const before = await hint.count();
		const highlights = section.locator('div', { hasText: /^Highlights/ }).first();
		await highlights.getByRole('button', { name: '+ Add' }).first().click();
		await highlights.getByRole('button', { name: '+ Add' }).first().click();

		await expect.poll(() => hint.count(), { timeout: 5_000 }).toBe(before);
	});

	test('a long form scrolls inside its pane and never makes the page itself scroll', async ({ page }) => {
		// Regression: the form's `sr-only` labels are `position: absolute`.
		// With no positioned ancestor they were placed against <body>, at
		// the bottom of the whole form, so the page grew to the form's full
		// height (7942px on a 745px window in production) and scrolling past
		// the form showed a long empty area below the editor.
		await switchToFormMode(page);
		await page.getByLabel('New section title').waitFor({ state: 'attached' });

		for (const tab of ['CV', 'Design', 'Locale', 'Settings']) {
			await page.getByRole('tab', { name: tab, exact: true }).click();
			const panel = page.locator('[role="tabpanel"]:visible').first();
			await expect(panel).toBeVisible();

			const sizes = await page.evaluate(() => ({
				page: document.documentElement.scrollHeight,
				viewport: window.innerHeight
			}));
			expect(sizes.page, `page height on the ${tab} tab`).toBeLessThanOrEqual(sizes.viewport);
		}

		// The check above only means something if the CV form really is
		// taller than its pane, so confirm the seeded example overflows it.
		await page.getByRole('tab', { name: 'CV', exact: true }).click();
		const formOverflows = await page.getByLabel('New section title').evaluate((input) => {
			let node: HTMLElement | null = input.parentElement;
			while (node && getComputedStyle(node).overflowY !== 'auto') node = node.parentElement;
			return node !== null && node.scrollHeight > node.clientHeight;
		});
		expect(formOverflows).toBe(true);
	});
});

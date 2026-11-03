import { test, expect } from './fixtures';
import type { Page } from '@playwright/test';
import { gotoReady, firstPreviewUrl } from './helpers';

/**
 * End-to-end coverage for Phase 3: the tab-bar theme switcher and the
 * Design/Locale form editors' effective-value overlay (approved semantics
 * — see the phase task). Each test is self-contained (its own `gotoReady`
 * call): a fresh browser context has no session cookie, so bootstrap always
 * creates a brand-new default CV (see `e2e/helpers.ts`).
 */

async function goToTab(page: Page, name: 'CV' | 'Design' | 'Locale' | 'Settings'): Promise<void> {
	await page.getByRole('tab', { name: new RegExp(`^${name}`) }).click();
}

async function yamlText(page: Page): Promise<string> {
	return (await page.locator('.cm-content').textContent()) ?? '';
}

async function setYamlMode(page: Page, on: boolean): Promise<void> {
	const toggle = page.getByRole('switch', { name: 'Toggle YAML editor' });
	const checked = (await toggle.getAttribute('aria-checked')) === 'true';
	if (checked !== on) {
		await toggle.click();
		await expect(toggle).toHaveAttribute('aria-checked', on ? 'true' : 'false', { timeout: 5_000 });
	}
}

test.describe('Theme switcher (tab bar, visible on every tab)', () => {
	test('switching theme rewrites the design document with the new theme\'s values', async ({
		page
	}) => {
		// This used to patch only the `theme:` line, which was right when a
		// fresh design document was blank -- the named theme supplied
		// everything else. It is wrong now that the starter document spells
		// out every option at the starting theme's values: those explicit
		// values win over the name, so renaming the theme produced a
		// byte-identical PDF. Measured before the fix: classic and ember
		// rendered to the same SHA-256.
		await gotoReady(page);
		const initialPreviewUrl = await firstPreviewUrl(page);

		await goToTab(page, 'Design');
		await setYamlMode(page, true);

		// A fresh CV's design document is filled in, not blank.
		const before = await yamlText(page);
		expect(before).toMatch(/theme:\s*classic/);
		expect(before).toMatch(/page:/);
		expect(before).toMatch(/bottom_margin:\s*0\.7in/); // classic's

		await page.getByRole('button', { name: 'Next Theme' }).click();

		await expect
			.poll(async () => yamlText(page), { timeout: 20_000 })
			.toMatch(/theme:\s*ember/);

		const after = await yamlText(page);
		// Still a full document -- the block was replaced, not emptied.
		expect(after).toMatch(/page:/);
		expect(after).toMatch(/colors:/);
		// And a value that differs between the two themes really moved. Without
		// this the test would pass on a switcher that changed only the name,
		// which is exactly the bug it exists to catch.
		expect(after).toMatch(/bottom_margin:\s*0\.6in/); // ember's
		expect(after).not.toMatch(/bottom_margin:\s*0\.7in/);

		await expect
			.poll(async () => (await page.getByTitle('CV PDF preview').getAttribute('src')) ?? '', {
				timeout: 25_000
			})
			.not.toBe(initialPreviewUrl);
	});

	test('the theme name dropdown opens, lists all 9 themes with a checkmark on the current one, and Escape closes it', async ({
		page
	}) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const trigger = page.getByRole('button', { name: 'Theme', exact: true });
		await trigger.click();

		const listbox = page.getByRole('listbox', { name: 'Theme' });
		await expect(listbox).toBeVisible();
		await expect(listbox.getByRole('option')).toHaveCount(9);

		// The checkmark itself is `aria-hidden` (purely visual); the
		// authoritative "this is the current one" signal is `aria-selected`.
		// The label is the display name (`themeDisplayName`), while the value
		// written to `design.theme` stays the raw identifier -- the YAML
		// assertions further down are what pin that half.
		const currentOption = listbox.getByRole('option', { name: 'Classic', exact: true });
		await expect(currentOption).toHaveAttribute('aria-selected', 'true');
		await expect(currentOption).toContainText('✓');
		await expect(listbox.getByRole('option', { name: 'Ember', exact: true })).toHaveAttribute(
			'aria-selected',
			'false'
		);

		await page.keyboard.press('Escape');
		await expect(listbox).not.toBeVisible();
	});

	test('cycling does not move the arrow that does the cycling', async ({ page }) => {
		// The theme identifiers differ hugely in length (`ink` against
		// `engineeringresumes`). With the value button sized to its content,
		// every press of `›` resized it and shifted the `›` itself sideways,
		// so a second press landed on empty space or on whatever had slid
		// underneath the pointer -- cycling through nine themes was
		// impossible without re-aiming each time. The box is asserted here
		// rather than the CSS because the width utility is not the property
		// that matters; where the button ends up is.
		await gotoReady(page);
		await firstPreviewUrl(page);

		const next = page.getByRole('button', { name: 'Next Theme' });
		const before = await next.boundingBox();
		if (!before) throw new Error('the Next Theme button is not rendered');

		// Walk the whole list back to the start: if any single label resizes
		// the control, one of these positions differs.
		for (let i = 0; i < 9; i += 1) {
			await next.click();
			const after = await next.boundingBox();
			if (!after) throw new Error('the Next Theme button vanished mid-cycle');
			expect(Math.abs(after.x - before.x)).toBeLessThan(1);
		}
	});
});

test.describe('Design form: effective-value overlay', () => {
	test('a form edit reaches the YAML', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		await goToTab(page, 'Design');
		await setYamlMode(page, false);

		const topMargin = page.getByLabel('Top Margin', { exact: true });
		await expect(topMargin).toBeVisible({ timeout: 20_000 });

		await topMargin.fill('0.5');
		await topMargin.blur();

		await setYamlMode(page, true);
		await expect
			.poll(async () => yamlText(page), { timeout: 20_000 })
			.toMatch(/top_margin:\s*0\.5in/);
	});

	test('switching theme replaces design edits, which is the accepted cost', async ({
		page
	}) => {
		// The opposite of what this file asserted before, and deliberately
		// so. While a fresh design document was blank, an edit was the only
		// thing in it and a theme switch could leave it alone. Now the
		// document holds every option, and the switcher has to replace the
		// whole block or the new theme has no effect at all -- so an edit
		// goes with it. Keeping edits would mean telling apart values the
		// user chose from values that merely came with the old theme, and
		// the document does not record that difference.
		await gotoReady(page);
		await firstPreviewUrl(page);

		await goToTab(page, 'Design');
		await setYamlMode(page, false);

		const topMargin = page.getByLabel('Top Margin', { exact: true });
		await expect(topMargin).toBeVisible({ timeout: 20_000 });
		await topMargin.fill('0.5');
		await topMargin.blur();

		await setYamlMode(page, true);
		await expect
			.poll(async () => yamlText(page), { timeout: 20_000 })
			.toMatch(/top_margin:\s*0\.5in/);

		await page.getByRole('button', { name: 'Next Theme' }).click();

		await expect
			.poll(async () => yamlText(page), { timeout: 20_000 })
			.toMatch(/theme:\s*ember/);
		// Gone, replaced by ember's own top margin.
		expect(await yamlText(page)).not.toMatch(/top_margin:\s*0\.5in/);
	});
});

test.describe('Reset to theme defaults', () => {
	test('flags a customised design and puts the theme defaults back', async ({ page }) => {
		// Why this exists: a Harvard CV carrying a stale `separator: ' | '`
		// rendered nothing like Harvard, and the only way back was to switch
		// away and return. The button names the overrides and resets them.
		await gotoReady(page);
		await firstPreviewUrl(page);

		const reset = page.getByTestId('reset-theme-defaults');
		// A fresh CV is exactly the classic defaults: nothing to reset.
		await expect(reset).toBeDisabled({ timeout: 20_000 });

		await goToTab(page, 'Design');
		await setYamlMode(page, false);
		const topMargin = page.getByLabel('Top Margin', { exact: true });
		await expect(topMargin).toBeVisible({ timeout: 20_000 });
		await topMargin.fill('0.5');
		await topMargin.blur();

		await expect(reset).toBeEnabled({ timeout: 20_000 });
		await expect(reset).toHaveAttribute('title', /page\.top_margin/);

		await reset.click();
		const dialog = page.getByRole('alertdialog');
		await expect(dialog).toContainText('page.top_margin');
		await dialog.getByRole('button', { name: 'Reset' }).click();

		await expect(dialog).toBeHidden();
		await expect(reset).toBeDisabled({ timeout: 20_000 });
		await setYamlMode(page, true);
		await expect
			.poll(async () => yamlText(page), { timeout: 20_000 })
			.not.toMatch(/top_margin:\s*0\.5in/);
		expect(await yamlText(page)).toMatch(/theme:\s*classic/);
	});
});

test.describe('Locale form', () => {
	test('editing a month name updates the locale YAML', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		await goToTab(page, 'Locale');
		await setYamlMode(page, false);

		const january = page.getByLabel('January', { exact: true });
		await expect(january).toBeVisible({ timeout: 20_000 });
		await expect(january).toHaveValue('January'); // effective default (English locale)

		await january.fill('Januarius');
		await january.blur();

		await setYamlMode(page, true);
		await expect.poll(async () => yamlText(page), { timeout: 20_000 }).toMatch(/Januarius/);
		expect(await yamlText(page)).toMatch(/month_names:/);
	});
});

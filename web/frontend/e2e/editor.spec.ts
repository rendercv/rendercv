import { test, expect } from './fixtures';
import type { Page } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
import { gotoReady, firstPreviewUrl } from './helpers';

/**
 * End-to-end coverage for the Phase 1 YAML-first MVP: edit -> debounced
 * preview render, and inline validation errors at the right tab/line.
 *
 * Why one spec file with sequential steps instead of independent `test()`
 * blocks per scenario: each scenario builds on the CV document state left
 * behind by the previous one (matches how a real editing session unfolds),
 * and avoids re-waiting for the ~800ms debounce + first render from scratch
 * for every assertion.
 */

/**
 * Puts the cursor at the end of the editor line containing `text`.
 *
 * Why the tests reach for an existing line rather than inserting one: the
 * starter CV is the core's sample and already declares `phone:`, so typing
 * a second one made a duplicate key -- a YAML syntax error, not the schema
 * error these tests are about. One of them failed outright; the other kept
 * passing, because a syntax error raises a lint marker too, and quietly
 * stopped testing what its name says.
 */
async function cursorAtEndOfLine(page: Page, text: string): Promise<void> {
	const line = page.locator('.cm-line', { hasText: text }).first();
	await line.click();
	await page.keyboard.press('End');
}

test.describe('CV editor: edit -> preview loop', () => {
	test('valid edit re-renders the preview with a new blob URL', async ({ page }) => {
		await gotoReady(page);

		const initialUrl = await firstPreviewUrl(page);

		const editor = page.locator('.cm-content');
		await editor.click();
		// Land right after "John Doe" on the name line, and append to it (no
		// newline involved), so the document stays valid and visibly changes.
		await page.keyboard.press('Control+Home');
		await page.keyboard.press('ArrowDown'); // to the "  name: John Doe" line
		await page.keyboard.press('End');
		await page.keyboard.type(' Jr');

		await expect
			.poll(async () => (await page.getByTitle('CV PDF preview').getAttribute('src')) ?? '', {
				timeout: 25_000
			})
			.not.toBe(initialUrl);

		const updatedUrl = await page.getByTitle('CV PDF preview').getAttribute('src');
		expect(updatedUrl).toMatch(/^blob:/);
	});

	test('a schema error shows a gutter marker on the right tab/line, preview stays visible', async ({
		page
	}) => {
		await gotoReady(page);
		const goodUrl = await firstPreviewUrl(page);

		// The sample ships `phone:` with no value; filling it with something
		// unparsable is a schema error and nothing else.
		await cursorAtEndOfLine(page, 'phone:');
		await page.keyboard.type(' abc');

		// The CV tab gets a red error dot.
		const cvTab = page.getByRole('tab', { name: /^CV/ });
		await expect(cvTab.locator('span[aria-label*="error"]')).toBeVisible({ timeout: 25_000 });

		// A gutter marker appears in the lint gutter, on the phone line.
		const marker = page.locator('.cm-lint-marker-error');
		await expect(marker).toBeVisible({ timeout: 25_000 });

		// The line the marker sits on is the one just edited.
		const phoneLineNumber = await page.evaluate(() => {
			const lines = Array.from(document.querySelectorAll('.cm-line'));
			return lines.findIndex((el) => el.textContent?.includes('phone: abc')) + 1;
		});
		expect(phoneLineNumber).toBeGreaterThan(0);

		// The error bar lists it under the CV tab with the message from the backend.
		await expect(page.getByRole('alert')).toContainText('phone');
		await expect(page.getByRole('alert')).toContainText(/not a valid phone number/i);

		// The last good preview is still visible (not blanked out).
		await expect(page.getByTitle('CV PDF preview')).toHaveAttribute('src', goodUrl);
	});

	test('fixing the error clears the gutter marker and the tab dot', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		await cursorAtEndOfLine(page, 'phone:');
		await page.keyboard.type(' abc');

		await expect(page.locator('.cm-lint-marker-error')).toBeVisible({ timeout: 25_000 });

		// Fix it: take the four characters back off, leaving `phone:` empty
		// again, which is how the sample ships it.
		for (let i = 0; i < 4; i += 1) {
			await page.keyboard.press('Backspace');
		}

		await expect(page.locator('.cm-lint-marker-error')).toHaveCount(0, { timeout: 25_000 });
		const cvTab = page.getByRole('tab', { name: /^CV/ });
		await expect(cvTab.locator('span[aria-label*="error"]')).toHaveCount(0, { timeout: 25_000 });
	});
});


test.describe('Downloading the YAML source', () => {
	// The PDF is the output; the YAML is the source, and the only one of the
	// two that can be edited again -- here, or by RenderCV's own CLI. This
	// exists because the deployment's database is disposable, so "get your
	// work out" has to be a button rather than a console snippet.

	test('one button offers both formats at the same depth', async ({ page }) => {
		// It used to be a split control: the left half downloaded the PDF and
		// the right half opened a menu offering the PDF again, so the format
		// nobody thinks to look for was the one behind the caret.
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();

		const menu = page.getByRole('menu', { name: 'Download options' });
		await expect(menu.getByRole('menuitem', { name: 'PDF', exact: true })).toBeVisible();
		await expect(menu.getByRole('menuitem', { name: 'YAML', exact: true })).toBeVisible();
		await expect(menu.getByRole('menuitem', { name: 'Image', exact: true })).toBeVisible();
		// The old split control offered "Download PDF" outside the menu.
		await expect(page.getByRole('button', { name: 'Download PDF' })).toHaveCount(0);
	});

	test('it saves one file that RenderCV could read back', async ({ page }) => {
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const downloadStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'YAML' }).click();
		const download = await downloadStarted;

		// Named after the CV, and sharing its stem with the PDF so both files
		// sort together in a downloads folder.
		expect(download.suggestedFilename()).toMatch(/\.yaml$/);

		const stream = await download.createReadStream();
		const chunks: Buffer[] = [];
		for await (const chunk of stream) chunks.push(Buffer.from(chunk));
		const text = Buffer.concat(chunks).toString('utf-8');

		// One file carrying the documents as top-level keys is exactly the
		// shape `rendercv render` accepts -- that is the whole reason the
		// export concatenates rather than zipping four files.
		expect(text).toContain('cv:');
		expect(text).toContain('settings:');
		// The starter CV's name, proving it exported the open document rather
		// than an empty shell.
		expect(text).toContain('name:');
		expect(text.endsWith('\n')).toBe(true);
	});

	test('the menu closes after the download starts', async ({ page }) => {
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const downloadStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'YAML' }).click();
		await downloadStarted;

		await expect(page.getByRole('menu', { name: 'Download options' })).toHaveCount(0);
	});
});


test.describe('Downloading the CV as images', () => {
	// A second Typst compilation, so it is rendered on request rather than
	// kept beside the preview.

	test('every page comes back, archived when there is more than one', async ({
		page
	}) => {
		// The starter CV runs to two pages, so this is the archive path. The
		// single-page path is covered where it can be built deliberately --
		// `tests/test_api.py`, `TestRenderImages`.
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const downloadStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'Image', exact: true }).click();
		const download = await downloadStarted;

		expect(download.suggestedFilename()).toMatch(/\.zip$/);

		const stream = await download.createReadStream();
		const chunks: Buffer[] = [];
		for await (const chunk of stream) chunks.push(Buffer.from(chunk));
		const bytes = Buffer.concat(chunks);

		// A real archive, not an error page that happened to download.
		expect(bytes.subarray(0, 2)).toEqual(Buffer.from('PK'));
		// Both page entries are named inside it, so no page was dropped.
		const text = bytes.toString('latin1');
		expect(text).toContain('page-1.png');
		expect(text).toContain('page-2.png');
	});

	test('the file shares its name with the PDF', async ({ page }) => {
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const imageStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'Image', exact: true }).click();
		const image = await imageStarted;

		await page.getByRole('button', { name: 'Download' }).click();
		const yamlStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'YAML', exact: true }).click();
		const yaml = await yamlStarted;

		const stem = (name: string) => name.replace(/\.[^.]+$/, '');
		expect(stem(image.suggestedFilename())).toBe(stem(yaml.suggestedFilename()));
	});
});

test.describe('Importing a YAML file', () => {
	// The other half of the export. A backup you cannot put back is a file,
	// not a backup, so the test that matters is the round trip rather than
	// either direction alone.

	test('a file this app exported comes back in as a new CV', async ({ page }, testInfo) => {
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const downloadStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'YAML' }).click();
		// Saved under a name we choose: the CV is named after the file, and
		// Playwright's own temporary name for a download is random.
		const saved = testInfo.outputPath('round-trip.yaml');
		await (await downloadStarted).saveAs(saved);

		// Set on the input directly rather than clicking the button, which
		// would open the operating system's file dialog.
		await page.getByLabel('YAML file to import').setInputFiles(saved);

		const list = page.getByRole('navigation', { name: 'Saved CVs' });
		await expect(list.getByText('round-trip')).toBeVisible({ timeout: 15_000 });
	});

	test('the imported CV really holds the imported text, after a reload', async ({
		page
	}, testInfo) => {
		// Reloaded on purpose: the import writes through the autosave, and
		// the failure worth catching is the one where the editor shows the
		// right thing and the server was never told.
		await gotoReady(page);

		await page.getByRole('button', { name: 'Download' }).click();
		const downloadStarted = page.waitForEvent('download');
		await page.getByRole('menuitem', { name: 'YAML' }).click();
		const saved = testInfo.outputPath('persisted.yaml');
		await (await downloadStarted).saveAs(saved);

		await page.getByLabel('YAML file to import').setInputFiles(saved);
		await expect(page.getByRole('navigation', { name: 'Saved CVs' }).getByText('persisted')).toBeVisible({
			timeout: 15_000
		});
		// Let the debounced save land before throwing the page away.
		await expect(page.getByText(/saved/i).first()).toBeVisible({ timeout: 20_000 });

		await page.reload();
		await expect(page.locator('.cm-content')).toContainText('name:', { timeout: 25_000 });
	});

	test('the theme switcher shows the theme that was imported', async ({
		page
	}, testInfo) => {
		// The visible contract: the label must name the theme the CV will
		// actually render with.
		//
		// It does NOT reproduce the bug that prompted it -- the switcher
		// showing `classic` for an imported `engineeringresumes` design.
		// That needed the import to land while the first parse was still in
		// flight, and by the time this test imports, the page has been idle
		// long enough that it never is. Checked: this test passes with the
		// fix reverted. `formSync.test.ts` holds the timing still and is
		// what pins the regression.
		const file = testInfo.outputPath('themed.yaml');
		await writeFile(
			file,
			[
				'cv:',
				'  name: Imported Person',
				'  sections: {}',
				'',
				'design:',
				'  theme: engineeringresumes',
				''
			].join('\n')
		);

		await gotoReady(page);
		await page.getByLabel('YAML file to import').setInputFiles(file);

		await expect(page.getByRole('navigation', { name: 'Saved CVs' }).getByText('themed')).toBeVisible({
			timeout: 15_000
		});
		await expect(page.getByRole('button', { name: 'Theme', exact: true })).toHaveText(
			'Engineering Resumes',
			{ timeout: 20_000 }
		);
	});

	test('a file that is not a RenderCV file is refused, and nothing is created', async ({
		page
	}, testInfo) => {
		await gotoReady(page);
		const list = page.getByRole('navigation', { name: 'Saved CVs' });
		const before = await list.getByRole('button').count();

		const notACv = testInfo.outputPath('not-a-cv.yaml');
		await writeFile(notACv, 'Nguyen Minh Quan\nData Scientist\n');
		await page.getByLabel('YAML file to import').setInputFiles(notACv);

		await expect(page.getByRole('alert')).toContainText('does not start with');
		expect(await list.getByRole('button').count()).toBe(before);
	});
});

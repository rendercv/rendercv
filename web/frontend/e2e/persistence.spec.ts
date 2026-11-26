import { test, expect } from './fixtures';
import type { Page } from '@playwright/test';
import { gotoReady, firstPreviewUrl } from './helpers';

/**
 * End-to-end coverage for Phase 4c: the real sidebar, autosave, and reload
 * persistence (docs/plans/completed/cv-editor-web-app.md, Phase 4). Requires
 * the FastAPI backend running on :8000 with a throwaway database -- see the
 * phase task for how this file's runner starts it.
 *
 * Each test gets its own browser context (Playwright's default), which
 * means its own session cookie, which means its own anonymous user and
 * empty CV list at `gotoReady()` -- tests never see each other's data.
 */

async function editorText(page: Page): Promise<string> {
	return (await page.locator('.cm-content').textContent()) ?? '';
}

/** Appends `suffix` right after "John Doe" on the CV name line, keeping the document valid. */
async function appendToName(page: Page, suffix: string): Promise<void> {
	const editor = page.locator('.cm-content');
	await editor.click();
	await page.keyboard.press('Control+Home');
	await page.keyboard.press('ArrowDown'); // the "  name: John Doe" line
	await page.keyboard.press('End');
	await page.keyboard.type(suffix);
}

test.describe('Persistence: autosave, sidebar, reload', () => {
	test('editing the CV, waiting for "Saved", then reloading keeps the edit', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		await appendToName(page, ' Jr');
		await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 20_000 });
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe Jr');

		await page.reload();
		await firstPreviewUrl(page);
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe Jr');
	});

	test('creating a second CV and switching between them keeps each CV\'s own content', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		await appendToName(page, ' First');
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe First');
		await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 20_000 });

		const firstBlobUrl = await page.getByTitle('CV PDF preview').getAttribute('src');

		await page.getByRole('button', { name: '+ Create new CV' }).click();

		// A new CV renders its own (default "John Doe") preview -- wait for a
		// different blob URL, then confirm the form/YAML actually reset too.
		await expect
			.poll(async () => (await page.getByTitle('CV PDF preview').getAttribute('src')) ?? '', { timeout: 25_000 })
			.not.toBe(firstBlobUrl);
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).not.toContain('First');
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe');

		await appendToName(page, ' Second');
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe Second');
		await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 20_000 });

		const items = page.locator('nav[aria-label="Saved CVs"] li');
		await expect(items).toHaveCount(2);

		// Newest-updated-first: the just-created/edited CV (index 0) is "Second"; the original is index 1.
		await items.nth(1).locator('button').first().click();
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe First');
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).not.toContain('Second');

		await items.nth(0).locator('button').first().click();
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('John Doe Second');
	});

	test('a background change to the open CV surfaces the conflict bar; "Tải bản mới" adopts the server content', async ({
		page
	}) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const listResponse = await page.request.get('/api/cvs');
		const list = (await listResponse.json()) as { id: number; name: string; updated_at: string }[];
		expect(list.length).toBe(1);
		const cvId = list[0].id;

		const getResponse = await page.request.get(`/api/cvs/${cvId}`);
		const cv = (await getResponse.json()) as {
			name: string;
			updated_at: string;
			documents: { cv_yaml: string; design_yaml: string; locale_yaml: string; settings_yaml: string };
		};

		// Simulate a save from "another tab": succeeds, advancing the server's
		// updated_at past what the open UI still has as its baseline.
		const bumpResponse = await page.request.put(`/api/cvs/${cvId}`, {
			data: {
				name: cv.name,
				documents: { ...cv.documents, cv_yaml: cv.documents.cv_yaml.replace('John Doe', 'Server Ghost') },
				seen_updated_at: cv.updated_at
			}
		});
		expect(bumpResponse.status()).toBe(200);

		// Now edit in the UI: its autosave still holds the stale updated_at, so this write loses the race.
		await appendToName(page, ' Local');
		await expect(page.getByText('CV này đã thay đổi ở nơi khác')).toBeVisible({ timeout: 20_000 });

		await page.getByRole('button', { name: 'Tải bản mới' }).click();
		await expect.poll(async () => editorText(page), { timeout: 20_000 }).toContain('Server Ghost');
		await expect(page.getByText('CV này đã thay đổi ở nơi khác')).toHaveCount(0);
	});
});

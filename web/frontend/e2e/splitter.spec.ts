import { test, expect } from './fixtures';
import { gotoReady, firstPreviewUrl } from './helpers';

/**
 * End-to-end coverage for the Phase 5 wave 3 resizable editor/preview split
 * (the user's explicit #1 request for this wave): pointer drag, keyboard,
 * double-click reset, and reload persistence.
 */

function separator(page: import('@playwright/test').Page) {
	return page.getByRole('separator', { name: /resize editor and preview/i });
}

async function editorWidth(page: import('@playwright/test').Page): Promise<number> {
	const box = await page.getByLabel('CV editor').boundingBox();
	if (!box) throw new Error('editor pane not found');
	return box.width;
}

async function previewWidth(page: import('@playwright/test').Page): Promise<number> {
	const box = await page.getByLabel('PDF preview').boundingBox();
	if (!box) throw new Error('preview pane not found');
	return box.width;
}

test.describe('Editor/preview splitter', () => {
	test.beforeEach(async ({ page }) => {
		// Start every test from the default 50/50 split, no saved preference.
		await page.addInitScript(() => window.localStorage.removeItem('rendercv.splitRatio'));
	});

	test('has the expected default ratio and accessible separator semantics', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		await expect(handle).toHaveAttribute('aria-orientation', 'vertical');
		await expect(handle).toHaveAttribute('aria-valuenow', '50');
		await expect(handle).toHaveAttribute('aria-valuemin', '25');
		await expect(handle).toHaveAttribute('aria-valuemax', '75');

		const editorW = await editorWidth(page);
		const previewW = await previewWidth(page);
		// Roughly equal (within the divider's own width).
		expect(Math.abs(editorW - previewW)).toBeLessThan(20);
	});

	test('dragging the handle resizes both panes and shields the PDF iframe mid-drag', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		const box = await handle.boundingBox();
		if (!box) throw new Error('separator not found');

		const startX = box.x + box.width / 2;
		const startY = box.y + box.height / 2;

		const editorWBefore = await editorWidth(page);

		await page.mouse.move(startX, startY);
		await page.mouse.down();
		// Move partway and check the drag shield is up (the classic
		// iframe-swallows-pointer-events bug this overlay works around).
		await page.mouse.move(startX + 100, startY, { steps: 5 });
		await expect(page.locator('[data-testid="splitter-drag-shield"]')).toBeVisible();

		await page.mouse.move(startX + 200, startY, { steps: 5 });
		await page.mouse.up();

		await expect(page.locator('[data-testid="splitter-drag-shield"]')).toHaveCount(0);

		const editorWAfter = await editorWidth(page);
		expect(editorWAfter).toBeGreaterThan(editorWBefore + 50);

		const valueNow = Number(await handle.getAttribute('aria-valuenow'));
		expect(valueNow).toBeGreaterThan(50);
		expect(valueNow).toBeLessThanOrEqual(75);
	});

	test('dragging past the bounds clamps to 25%/75%', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		const box = await handle.boundingBox();
		if (!box) throw new Error('separator not found');

		await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
		await page.mouse.down();
		await page.mouse.move(box.x + 5000, box.y + box.height / 2, { steps: 10 });
		await page.mouse.up();

		await expect(handle).toHaveAttribute('aria-valuenow', '75');
	});

	test('double-click resets the split to the default 50/50', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		const box = await handle.boundingBox();
		if (!box) throw new Error('separator not found');

		await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
		await page.mouse.down();
		await page.mouse.move(box.x + 150, box.y + box.height / 2, { steps: 5 });
		await page.mouse.up();

		await expect(handle).not.toHaveAttribute('aria-valuenow', '50');

		await handle.dblclick();

		await expect(handle).toHaveAttribute('aria-valuenow', '50');
	});

	test('ArrowLeft/ArrowRight step by 2%, Home/End jump to the clamped bounds', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		await handle.focus();

		await page.keyboard.press('ArrowRight');
		await expect(handle).toHaveAttribute('aria-valuenow', '52');

		await page.keyboard.press('ArrowRight');
		await expect(handle).toHaveAttribute('aria-valuenow', '54');

		await page.keyboard.press('ArrowLeft');
		await expect(handle).toHaveAttribute('aria-valuenow', '52');

		await page.keyboard.press('End');
		await expect(handle).toHaveAttribute('aria-valuenow', '75');

		await page.keyboard.press('Home');
		await expect(handle).toHaveAttribute('aria-valuenow', '25');
	});

	test('the ratio persists across reload', async ({ page }) => {
		await gotoReady(page);
		await firstPreviewUrl(page);

		const handle = separator(page);
		await handle.focus();
		for (let i = 0; i < 5; i++) {
			await page.keyboard.press('ArrowRight');
		}
		await expect(handle).toHaveAttribute('aria-valuenow', '60');

		// The debounced `PUT /api/preferences` write (see
		// `$lib/stores/splitRatio.ts`) needs a moment to land before reload,
		// so bootstrap's `GET /api/preferences` sees it.
		await page.waitForTimeout(700);

		await gotoReady(page);
		await expect(separator(page)).toHaveAttribute('aria-valuenow', '60');
	});
});

import { describe, it, expect, vi } from 'vitest';
import { createThemeMemory } from './themeMemory';

const harvardTuned = {
	theme: 'harvard',
	entries: { space_between_entries: '0.7em' }
};
const harvardDefaults = {
	theme: 'harvard',
	entries: { space_between_entries: '1em' }
};
const classicDefaults = { theme: 'classic' };

describe('createThemeMemory', () => {
	it('stores the design being left and arrives at defaults when nothing is remembered', async () => {
		const putThemeDesign = vi.fn().mockResolvedValue(true);
		const getThemeDesign = vi.fn().mockResolvedValue(null);
		const memory = createThemeMemory({ putThemeDesign, getThemeDesign });

		const outcome = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'harvard',
			fromDesign: harvardTuned,
			toTheme: 'classic',
			toDefaults: classicDefaults
		});

		expect(putThemeDesign).toHaveBeenCalledWith(7, 'harvard', harvardTuned);
		expect(getThemeDesign).toHaveBeenCalledWith(7, 'classic');
		expect(outcome).toEqual({
			design: classicDefaults,
			restored: false,
			rememberFailed: false
		});
	});

	it("restores the server's design when coming back -- e.g. one stored from the other device", async () => {
		const memory = createThemeMemory({
			putThemeDesign: vi.fn().mockResolvedValue(true),
			getThemeDesign: vi.fn().mockResolvedValue(harvardTuned)
		});

		const outcome = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});

		expect(outcome).toEqual({
			design: harvardTuned,
			restored: true,
			rememberFailed: false
		});
	});

	it('falls back to the copy kept in this tab when the server cannot be reached', async () => {
		const memory = createThemeMemory({
			putThemeDesign: vi.fn().mockResolvedValue(false),
			getThemeDesign: vi.fn().mockRejectedValue(new Error('offline'))
		});

		const away = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'harvard',
			fromDesign: harvardTuned,
			toTheme: 'classic',
			toDefaults: classicDefaults
		});
		expect(away.rememberFailed).toBe(true);

		const back = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});
		expect(back.design).toEqual(harvardTuned);
		expect(back.restored).toBe(true);
	});

	it('keeps a copy, not a reference: later edits to the left design do not leak into it', async () => {
		const memory = createThemeMemory({
			putThemeDesign: vi.fn().mockResolvedValue(false),
			getThemeDesign: vi.fn().mockResolvedValue(null)
		});
		const leaving = structuredClone(harvardTuned);

		await memory.switchTheme({
			cvId: 7,
			fromTheme: 'harvard',
			fromDesign: leaving,
			toTheme: 'classic',
			toDefaults: classicDefaults
		});
		leaving.entries.space_between_entries = '9em';

		const back = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});
		expect(back.design).toEqual(harvardTuned);
	});

	it('never stores a design that does not belong to the theme being left', async () => {
		// A document that failed to parse has no design to trust; storing it
		// would overwrite the good copy from the last switch.
		const putThemeDesign = vi.fn().mockResolvedValue(true);
		const memory = createThemeMemory({
			putThemeDesign,
			getThemeDesign: vi.fn().mockResolvedValue(null)
		});

		for (const fromDesign of [undefined, null, 'not a mapping', { theme: 'classic' }]) {
			await memory.switchTheme({
				cvId: 7,
				fromTheme: 'harvard',
				fromDesign,
				toTheme: 'classic',
				toDefaults: classicDefaults
			});
		}

		expect(putThemeDesign).not.toHaveBeenCalled();
	});

	it('ignores a remembered design that names another theme, and uses the defaults', async () => {
		const memory = createThemeMemory({
			putThemeDesign: vi.fn().mockResolvedValue(true),
			getThemeDesign: vi.fn().mockResolvedValue({ theme: 'classic' })
		});

		const outcome = await memory.switchTheme({
			cvId: 7,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});

		expect(outcome.design).toEqual(harvardDefaults);
		expect(outcome.restored).toBe(false);
	});

	it('keeps different CVs apart in the per-tab copy', async () => {
		const memory = createThemeMemory({
			putThemeDesign: vi.fn().mockResolvedValue(false),
			getThemeDesign: vi.fn().mockRejectedValue(new Error('offline'))
		});
		await memory.switchTheme({
			cvId: 7,
			fromTheme: 'harvard',
			fromDesign: harvardTuned,
			toTheme: 'classic',
			toDefaults: classicDefaults
		});

		const otherCv = await memory.switchTheme({
			cvId: 8,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});

		expect(otherCv.design).toEqual(harvardDefaults);
	});

	it('works without a CV, from the per-tab copy alone', async () => {
		const putThemeDesign = vi.fn();
		const getThemeDesign = vi.fn();
		const memory = createThemeMemory({ putThemeDesign, getThemeDesign });

		await memory.switchTheme({
			cvId: null,
			fromTheme: 'harvard',
			fromDesign: harvardTuned,
			toTheme: 'classic',
			toDefaults: classicDefaults
		});
		const back = await memory.switchTheme({
			cvId: null,
			fromTheme: 'classic',
			fromDesign: classicDefaults,
			toTheme: 'harvard',
			toDefaults: harvardDefaults
		});

		expect(back.design).toEqual(harvardTuned);
		expect(putThemeDesign).not.toHaveBeenCalled();
		expect(getThemeDesign).not.toHaveBeenCalled();
	});
});

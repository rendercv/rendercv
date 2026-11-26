import { describe, it, expect, vi } from 'vitest';
import { bootstrapApp, pickCv } from './bootstrap';
import type { CvDetail, CvSummary } from '$lib/api/cvs';

function summary(id: number, name: string, updatedAt: string): CvSummary {
	return { id, name, updatedAt };
}

function detail(id: number, name: string, updatedAt: string): CvDetail {
	return {
		id,
		name,
		updatedAt,
		documents: { cv: 'cv:\n  name: Test\n', design: '', locale: '', settings: '' }
	};
}

describe('pickCv', () => {
	it('returns null for an empty list', () => {
		expect(pickCv([], null)).toBeNull();
		expect(pickCv([], 5)).toBeNull();
	});

	it('returns the newest (first) entry when lastCvId is null', () => {
		const list = [summary(2, 'B', 't2'), summary(1, 'A', 't1')];
		expect(pickCv(list, null)).toEqual(list[0]);
	});

	it('returns the entry matching lastCvId when it still exists', () => {
		const list = [summary(2, 'B', 't2'), summary(1, 'A', 't1')];
		expect(pickCv(list, 1)).toEqual(list[1]);
	});

	it('falls back to the newest entry when lastCvId no longer exists', () => {
		const list = [summary(2, 'B', 't2'), summary(1, 'A', 't1')];
		expect(pickCv(list, 999)).toEqual(list[0]);
	});
});

describe('bootstrapApp', () => {
	it('creates a default CV when the session has none yet', async () => {
		const created = detail(10, 'Untitled CV', 't0');
		const deps = {
			listCvs: vi.fn().mockResolvedValue([]),
			createCv: vi.fn().mockResolvedValue(created),
			getCv: vi.fn(),
			getPreferences: vi.fn().mockResolvedValue({})
		};

		const result = await bootstrapApp(deps);

		expect(deps.createCv).toHaveBeenCalledTimes(1);
		expect(deps.getCv).not.toHaveBeenCalled();
		expect(result.cv).toEqual(created);
		expect(result.cvsList).toEqual([{ id: 10, name: 'Untitled CV', updatedAt: 't0' }]);
	});

	it('opens the CV named by the last_cv_id preference when it still exists', async () => {
		const list = [summary(2, 'B', 't2'), summary(1, 'A', 't1')];
		const full = detail(1, 'A', 't1');
		const deps = {
			listCvs: vi.fn().mockResolvedValue(list),
			createCv: vi.fn(),
			getCv: vi.fn().mockResolvedValue(full),
			getPreferences: vi.fn().mockResolvedValue({ last_cv_id: '1' })
		};

		const result = await bootstrapApp(deps);

		expect(deps.getCv).toHaveBeenCalledWith(1);
		expect(result.cv).toEqual(full);
		expect(result.cvsList).toEqual(list);
	});

	it('opens the newest CV when last_cv_id is absent', async () => {
		const list = [summary(2, 'B', 't2'), summary(1, 'A', 't1')];
		const full = detail(2, 'B', 't2');
		const deps = {
			listCvs: vi.fn().mockResolvedValue(list),
			createCv: vi.fn(),
			getCv: vi.fn().mockResolvedValue(full),
			getPreferences: vi.fn().mockResolvedValue({})
		};

		const result = await bootstrapApp(deps);
		expect(deps.getCv).toHaveBeenCalledWith(2);
		expect(result.cv).toEqual(full);
	});

	it('falls back to creating a default CV if the chosen one vanished', async () => {
		const list = [summary(1, 'A', 't1')];
		const created = detail(10, 'Untitled CV', 't0');
		const deps = {
			listCvs: vi.fn().mockResolvedValue(list),
			createCv: vi.fn().mockResolvedValue(created),
			getCv: vi.fn().mockResolvedValue(null),
			getPreferences: vi.fn().mockResolvedValue({})
		};

		const result = await bootstrapApp(deps);
		expect(deps.createCv).toHaveBeenCalledTimes(1);
		expect(result.cv).toEqual(created);
		expect(result.cvsList[0]).toEqual({ id: 10, name: 'Untitled CV', updatedAt: 't0' });
	});
});

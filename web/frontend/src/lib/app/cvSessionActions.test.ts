import { describe, it, expect, vi } from 'vitest';
import { get, writable } from 'svelte/store';
import { createCvSessionActions } from './cvSessionActions';
import type { CvDetail, CvSummary } from '$lib/api/cvs';
import type { CvDocuments } from '$lib/stores/documents';
import type { ActiveCvMeta } from '$lib/stores/cvSession';

function docs(name = 'John Doe'): CvDocuments {
	return { cv: `cv:\n  name: ${name}\n`, design: '', locale: '', settings: '' };
}

function detail(id: number, name: string, updatedAt = `t${id}`): CvDetail {
	return { id, name, updatedAt, documents: docs(name) };
}

function makeStores(initialCvs: CvSummary[] = [], initialActive: ActiveCvMeta | null = null) {
	return {
		cvs: writable<CvSummary[]>(initialCvs),
		activeCv: writable<ActiveCvMeta | null>(initialActive),
		documents: writable<CvDocuments>(docs())
	};
}

function fakeAutosave() {
	return {
		state: writable({ status: 'saved' as const, conflict: null }),
		setBaseline: vi.fn(),
		flush: vi.fn().mockResolvedValue(undefined),
		flushBeforeUnload: vi.fn(),
		resolveConflict: vi.fn(),
		retryNow: vi.fn(),
		destroy: vi.fn()
	};
}

describe('createCvSessionActions', () => {
	it('loadInto seeds the baseline before the stores, and sets activeCv/documents', () => {
		const stores = makeStores();
		const autosave = fakeAutosave();
		const actions = createCvSessionActions(stores, autosave);

		const cv = detail(1, 'A');
		actions.loadInto(cv);

		expect(autosave.setBaseline).toHaveBeenCalledWith({
			id: 1,
			name: 'A',
			documents: cv.documents,
			updatedAt: 't1'
		});
		expect(get(stores.activeCv)).toEqual({ id: 1, name: 'A' });
		expect(get(stores.documents)).toEqual(cv.documents);
	});

	it('switchTo flushes the current CV, then loads the target one', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const target = detail(2, 'B');
		const getCv = vi.fn().mockResolvedValue(target);
		const actions = createCvSessionActions(stores, autosave, { getCv });

		await actions.switchTo(2);

		expect(autosave.flush).toHaveBeenCalledTimes(1);
		expect(getCv).toHaveBeenCalledWith(2);
		expect(get(stores.activeCv)).toEqual({ id: 2, name: 'B' });
	});

	it('switchTo is a no-op when the target is already open', async () => {
		const stores = makeStores([], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const getCv = vi.fn();
		const actions = createCvSessionActions(stores, autosave, { getCv });

		await actions.switchTo(1);
		expect(autosave.flush).not.toHaveBeenCalled();
		expect(getCv).not.toHaveBeenCalled();
	});

	it('createNew flushes, creates, prepends to the list, and opens it', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const created = detail(2, 'Untitled CV');
		const createCv = vi.fn().mockResolvedValue(created);
		const actions = createCvSessionActions(stores, autosave, { createCv });

		await actions.createNew();

		expect(autosave.flush).toHaveBeenCalledTimes(1);
		expect(get(stores.cvs)).toEqual([
			{ id: 2, name: 'Untitled CV', updatedAt: 't2' },
			{ id: 1, name: 'A', updatedAt: 't1' }
		]);
		expect(get(stores.activeCv)).toEqual({ id: 2, name: 'Untitled CV' });
	});

	it('importFrom opens a new CV holding the imported documents', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const createCv = vi.fn().mockResolvedValue(detail(2, 'Untitled CV'));
		const actions = createCvSessionActions(stores, autosave, { createCv });
		const imported = {
			cv: 'cv:\n  name: Imported\n',
			design: 'design:\n  theme: classic\n',
			locale: '',
			settings: ''
		};

		await actions.importFrom('My Backup', imported);

		expect(autosave.flush).toHaveBeenCalledTimes(1);
		expect(get(stores.documents)).toEqual(imported);
		expect(get(stores.activeCv)).toEqual({ id: 2, name: 'My Backup' });
		expect(get(stores.cvs)[0]).toEqual({ id: 2, name: 'My Backup', updatedAt: 't2' });
	});

	it('importFrom leaves the imported documents dirty so the autosave writes them', async () => {
		// The failure this guards against is silent and only shows on the
		// next reload: if the documents were set before the baseline, they
		// would match it, count as unchanged, and never be sent -- an import
		// that looks perfect until the CV is opened again and is empty.
		const stores = makeStores([], null);
		const autosave = fakeAutosave();
		const created = detail(2, 'Untitled CV');
		const createCv = vi.fn().mockResolvedValue(created);
		const actions = createCvSessionActions(stores, autosave, { createCv });

		await actions.importFrom('Backup', {
			cv: 'cv:\n  name: Imported\n',
			design: '',
			locale: '',
			settings: ''
		});

		expect(autosave.setBaseline).toHaveBeenCalledTimes(1);
		const baseline = autosave.setBaseline.mock.calls[0][0];
		expect(baseline.documents).toEqual(created.documents);
		expect(get(stores.documents)).not.toEqual(baseline.documents);
	});

	it('rename of the open CV updates the stores immediately without a network call', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const updateCv = vi.fn();
		const actions = createCvSessionActions(stores, autosave, { updateCv });

		await actions.rename(1, 'Renamed');

		expect(updateCv).not.toHaveBeenCalled();
		expect(get(stores.activeCv)).toEqual({ id: 1, name: 'Renamed' });
		expect(get(stores.cvs)[0].name).toBe('Renamed');
	});

	it('rename of a CV that is not open fetches it and writes immediately', async () => {
		const stores = makeStores(
			[
				{ id: 1, name: 'A', updatedAt: 't1' },
				{ id: 2, name: 'B', updatedAt: 't2' }
			],
			{ id: 1, name: 'A' }
		);
		const autosave = fakeAutosave();
		const other = detail(2, 'B');
		const getCv = vi.fn().mockResolvedValue(other);
		const updateCv = vi.fn().mockResolvedValue({ ok: true, updatedAt: 't3' });
		const actions = createCvSessionActions(stores, autosave, { getCv, updateCv });

		await actions.rename(2, 'Renamed B');

		expect(getCv).toHaveBeenCalledWith(2);
		expect(updateCv).toHaveBeenCalledWith(2, {
			name: 'Renamed B',
			documents: other.documents,
			seenUpdatedAt: 't2'
		});
		expect(get(stores.cvs).find((cv) => cv.id === 2)).toEqual({ id: 2, name: 'Renamed B', updatedAt: 't3' });
		// The open CV (id 1) is untouched.
		expect(get(stores.activeCv)).toEqual({ id: 1, name: 'A' });
	});

	it('duplicate adds the copy to the list without switching to it', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const copy = detail(2, 'Copy of A');
		const duplicateCv = vi.fn().mockResolvedValue(copy);
		const actions = createCvSessionActions(stores, autosave, { duplicateCv });

		await actions.duplicate(1);

		expect(get(stores.cvs)).toEqual([
			{ id: 2, name: 'Copy of A', updatedAt: 't2' },
			{ id: 1, name: 'A', updatedAt: 't1' }
		]);
		expect(get(stores.activeCv)).toEqual({ id: 1, name: 'A' }); // unchanged
	});

	it('deleting a CV that is not open just removes it from the list', async () => {
		const stores = makeStores(
			[
				{ id: 1, name: 'A', updatedAt: 't1' },
				{ id: 2, name: 'B', updatedAt: 't2' }
			],
			{ id: 1, name: 'A' }
		);
		const autosave = fakeAutosave();
		const deleteCv = vi.fn().mockResolvedValue(true);
		const actions = createCvSessionActions(stores, autosave, { deleteCv });

		await actions.remove(2);

		expect(get(stores.cvs)).toEqual([{ id: 1, name: 'A', updatedAt: 't1' }]);
		expect(get(stores.activeCv)).toEqual({ id: 1, name: 'A' }); // unchanged
	});

	it('deleting the open CV switches to another remaining CV', async () => {
		const stores = makeStores(
			[
				{ id: 1, name: 'A', updatedAt: 't1' },
				{ id: 2, name: 'B', updatedAt: 't2' }
			],
			{ id: 1, name: 'A' }
		);
		const autosave = fakeAutosave();
		const deleteCv = vi.fn().mockResolvedValue(true);
		const getCv = vi.fn().mockResolvedValue(detail(2, 'B'));
		const actions = createCvSessionActions(stores, autosave, { deleteCv, getCv });

		await actions.remove(1);

		expect(get(stores.cvs)).toEqual([{ id: 2, name: 'B', updatedAt: 't2' }]);
		expect(get(stores.activeCv)).toEqual({ id: 2, name: 'B' });
	});

	it('deleting the last remaining CV creates a fresh default and opens it', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const deleteCv = vi.fn().mockResolvedValue(true);
		const created = detail(9, 'Untitled CV');
		const createCv = vi.fn().mockResolvedValue(created);
		const actions = createCvSessionActions(stores, autosave, { deleteCv, createCv });

		await actions.remove(1);

		expect(createCv).toHaveBeenCalledTimes(1);
		expect(get(stores.cvs)).toEqual([{ id: 9, name: 'Untitled CV', updatedAt: 't9' }]);
		expect(get(stores.activeCv)).toEqual({ id: 9, name: 'Untitled CV' });
	});

	it('restore refreshes the list entry, and reloads documents if it is the open CV', async () => {
		const stores = makeStores([{ id: 1, name: 'A', updatedAt: 't1' }], { id: 1, name: 'A' });
		const autosave = fakeAutosave();
		const restoreVersion = vi.fn().mockResolvedValue({ ok: true, updatedAt: 't2' });
		const restored = detail(1, 'A', 't2');
		const getCv = vi.fn().mockResolvedValue(restored);
		const actions = createCvSessionActions(stores, autosave, { restoreVersion, getCv });

		await actions.restore(1, 5);

		expect(restoreVersion).toHaveBeenCalledWith(1, 5);
		expect(get(stores.documents)).toEqual(restored.documents);
		expect(autosave.setBaseline).toHaveBeenCalledWith({
			id: 1,
			name: 'A',
			documents: restored.documents,
			updatedAt: 't2'
		});
	});
});

import { get, type Writable } from 'svelte/store';
import type { CvDocuments } from '$lib/stores/documents';
import type { ActiveCvMeta } from '$lib/stores/cvSession';
import type { AutosaveController } from '$lib/persistence/autosave';
import {
	listCvs as listCvsApi,
	createCv as createCvApi,
	getCv as getCvApi,
	updateCv as updateCvApi,
	duplicateCv as duplicateCvApi,
	deleteCv as deleteCvApi,
	restoreVersion as restoreVersionApi,
	type CvDetail,
	type CvSummary
} from '$lib/api/cvs';

export interface CvSessionStores {
	cvs: Writable<CvSummary[]>;
	activeCv: Writable<ActiveCvMeta | null>;
	documents: Writable<CvDocuments>;
}

export interface CvSessionActionsDeps {
	listCvs?: typeof listCvsApi;
	createCv?: typeof createCvApi;
	getCv?: typeof getCvApi;
	updateCv?: typeof updateCvApi;
	duplicateCv?: typeof duplicateCvApi;
	deleteCv?: typeof deleteCvApi;
	restoreVersion?: typeof restoreVersionApi;
}

export interface CvSessionActions {
	/** Seeds the autosave baseline and the `activeCv`/`documents` stores from a freshly loaded or created CV, without it registering as a dirty edit. */
	loadInto: (cv: CvDetail) => void;
	/** Refreshes the sidebar list from the server. */
	refreshList: () => Promise<void>;
	/** Flushes the current CV's pending save, then opens a different one. No-op if `id` is already open. */
	switchTo: (id: number) => Promise<void>;
	/** Flushes, creates a new default CV, adds it to the list, and opens it. */
	createNew: () => Promise<void>;
	/** Flushes, creates a CV from imported documents under `name`, and opens it. */
	importFrom: (name: string, imported: CvDocuments) => Promise<void>;
	/** Renames the CV `id`: an in-place edit if it's the open one (autosave picks it up on the normal debounce); an immediate direct write otherwise. */
	rename: (id: number, name: string) => Promise<void>;
	/** Duplicates a CV and adds the copy to the list (does not switch to it). */
	duplicate: (id: number) => Promise<void>;
	/** Deletes a CV. If it was the open one, switches to another CV, or creates a fresh default if none remain. */
	remove: (id: number) => Promise<void>;
	/** Restores a version snapshot, refreshing the list entry and, if it's the open CV, its documents too. */
	restore: (id: number, versionId: number) => Promise<void>;
}

function toSummary(cv: CvDetail): CvSummary {
	return { id: cv.id, name: cv.name, updatedAt: cv.updatedAt };
}

/**
 * Orchestrates the sidebar's CV list against the shared `documents` /
 * `activeCv` / `cvs` stores and the autosave controller
 * (docs/plans/completed/cv-editor-web-app.md, Phase 4c). A standalone factory
 * (same reasoning as every other controller in this codebase) so switch/
 * create/rename/duplicate/delete/restore semantics are unit-testable with
 * injected stores and a fake API -- see `cvSessionActions.test.ts`.
 */
export function createCvSessionActions(
	stores: CvSessionStores,
	autosave: AutosaveController,
	deps: CvSessionActionsDeps = {}
): CvSessionActions {
	const {
		listCvs = listCvsApi,
		createCv = createCvApi,
		getCv = getCvApi,
		updateCv = updateCvApi,
		duplicateCv = duplicateCvApi,
		deleteCv = deleteCvApi,
		restoreVersion = restoreVersionApi
	} = deps;

	function loadInto(cv: CvDetail): void {
		autosave.setBaseline({ id: cv.id, name: cv.name, documents: cv.documents, updatedAt: cv.updatedAt });
		stores.activeCv.set({ id: cv.id, name: cv.name });
		stores.documents.set(cv.documents);
	}

	async function refreshList(): Promise<void> {
		stores.cvs.set(await listCvs());
	}

	async function switchTo(id: number): Promise<void> {
		const current = get(stores.activeCv);
		if (current && current.id === id) return;
		await autosave.flush();
		const full = await getCv(id);
		if (!full) return; // vanished (e.g. deleted in another tab); the list will settle on its next refresh
		loadInto(full);
	}

	async function createNew(): Promise<void> {
		await autosave.flush();
		const created = await createCv();
		stores.cvs.update((list) => [toSummary(created), ...list]);
		loadInto(created);
	}

	async function importFrom(name: string, imported: CvDocuments): Promise<void> {
		await autosave.flush();
		const created = await createCv();
		stores.cvs.update((list) => [toSummary(created), ...list]);
		loadInto(created);
		// Set *after* `loadInto`, deliberately: that call makes the empty CV
		// the server just created the autosave baseline, so the imported text
		// then registers as an edit and gets written. Setting it first would
		// look identical on screen and never reach the server -- an import
		// that appears to work and is gone on the next reload.
		stores.documents.set(imported);
		await rename(created.id, name);
	}

	async function rename(id: number, name: string): Promise<void> {
		const trimmed = name.trim();
		if (trimmed === '') return;

		const current = get(stores.activeCv);
		if (current && current.id === id) {
			stores.activeCv.set({ id, name: trimmed });
			stores.cvs.update((list) => list.map((cv) => (cv.id === id ? { ...cv, name: trimmed } : cv)));
			return; // the autosave controller picks up the name change on its normal debounce
		}

		// Renaming a CV that isn't open: read its current state, then write immediately.
		const full = await getCv(id);
		if (!full) return;
		const result = await updateCv(id, { name: trimmed, documents: full.documents, seenUpdatedAt: full.updatedAt });
		if (result.ok) {
			stores.cvs.update((list) =>
				list.map((cv) => (cv.id === id ? { ...cv, name: trimmed, updatedAt: result.updatedAt } : cv))
			);
		}
		// A conflict/error renaming a CV in the background is left for the next
		// list refresh to reconcile -- out of scope for this phase's acceptance
		// criteria (the reconciliation UI is for the *open* CV's autosave).
	}

	async function duplicate(id: number): Promise<void> {
		const copy = await duplicateCv(id);
		if (!copy) return;
		stores.cvs.update((list) => [toSummary(copy), ...list]);
	}

	async function remove(id: number): Promise<void> {
		const wasActive = get(stores.activeCv)?.id === id;
		// Same race as `restore`: settle the open CV's pending save before the
		// row disappears, so no write is left on the wire against a deleted CV.
		if (wasActive) await autosave.flush();
		const ok = await deleteCv(id);
		if (!ok) return;
		stores.cvs.update((list) => list.filter((cv) => cv.id !== id));

		if (!wasActive) return;

		const remaining = get(stores.cvs);
		if (remaining.length > 0) {
			const full = await getCv(remaining[0].id);
			if (full) {
				loadInto(full);
				return;
			}
		}
		const created = await createCv();
		stores.cvs.update((list) => [toSummary(created), ...list]);
		loadInto(created);
	}

	async function restore(id: number, versionId: number): Promise<void> {
		// A pending or in-flight save carries the pre-restore `seenUpdatedAt`:
		// landing after the restore it 409s (a conflict bar right after a
		// successful restore), landing before it silently reverts the version
		// the user just restored. Settle it first, as `switchTo` does.
		if (get(stores.activeCv)?.id === id) await autosave.flush();
		const result = await restoreVersion(id, versionId);
		if (!result.ok) return; // conflict/not-found: left for the user to retry
		const full = await getCv(id);
		if (!full) return;
		stores.cvs.update((list) => list.map((cv) => (cv.id === id ? toSummary(full) : cv)));
		if (get(stores.activeCv)?.id === id) loadInto(full);
	}

	return {
		loadInto,
		refreshList,
		switchTo,
		createNew,
		importFrom,
		rename,
		duplicate,
		remove,
		restore
	};
}

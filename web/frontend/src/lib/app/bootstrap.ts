import type { CvDetail, CvSummary } from '$lib/api/cvs';

/**
 * Picks which CV to open on load, from the saved-CVs list and the
 * `last_cv_id` preference (docs/plans/completed/cv-editor-web-app.md, Phase 4).
 *
 * Why a standalone pure function: unit-testable without a network or store
 * mounted (`bootstrap.test.ts`) -- the only actual decision logic in an
 * otherwise fully I/O-driven bootstrap sequence.
 *
 * @param cvsList - Every saved CV, newest-updated first (as `GET /api/cvs` returns it).
 * @param lastCvId - The `last_cv_id` preference, parsed to a number, or `null` if unset/unparsable.
 * @returns The CV to open: the one matching `lastCvId` if it still exists, else the newest; `null` if `cvsList` is empty.
 */
export function pickCv(cvsList: CvSummary[], lastCvId: number | null): CvSummary | null {
	if (cvsList.length === 0) return null;
	if (lastCvId !== null) {
		const match = cvsList.find((cv) => cv.id === lastCvId);
		if (match) return match;
	}
	return cvsList[0];
}

export interface BootstrapDeps {
	listCvs: () => Promise<CvSummary[]>;
	createCv: () => Promise<CvDetail>;
	getCv: (id: number) => Promise<CvDetail | null>;
	getPreferences: () => Promise<Record<string, string>>;
}

export interface BootstrapResult {
	/** The CV to load into the editor. */
	cv: CvDetail;
	/** The full sidebar list, including `cv` (freshly created CVs are appended to it here so callers don't need a second round trip). */
	cvsList: CvSummary[];
	preferences: Record<string, string>;
}

/**
 * Resolves which CV to open and fetches it in full, creating a default CV
 * if the session has none yet.
 *
 * Why `getCv` can return `null` here despite `pickCv` choosing an id from a
 * list we just fetched: a race with a concurrent delete in another tab is
 * possible, however unlikely -- falls back to creating a fresh default CV
 * rather than leaving the app stuck loading.
 */
export async function bootstrapApp(deps: BootstrapDeps): Promise<BootstrapResult> {
	const [cvsList, preferences] = await Promise.all([deps.listCvs(), deps.getPreferences()]);

	if (cvsList.length === 0) {
		const created = await deps.createCv();
		return { cv: created, cvsList: [{ id: created.id, name: created.name, updatedAt: created.updatedAt }], preferences };
	}

	const lastCvIdRaw = preferences.last_cv_id;
	const lastCvId = lastCvIdRaw !== undefined && lastCvIdRaw !== '' ? Number(lastCvIdRaw) : null;
	const chosen = pickCv(cvsList, Number.isFinite(lastCvId) ? lastCvId : null);

	const full = chosen ? await deps.getCv(chosen.id) : null;
	if (full) return { cv: full, cvsList, preferences };

	// The chosen id vanished between listing and fetching -- fall back to a fresh default CV.
	const created = await deps.createCv();
	return {
		cv: created,
		cvsList: [{ id: created.id, name: created.name, updatedAt: created.updatedAt }, ...cvsList],
		preferences
	};
}

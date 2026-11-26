import type { CvDocuments } from '$lib/stores/documents';
import { apiFetch } from '$lib/api/http';

/**
 * Client for the multi-CV persistence contract (`web/backend/src/
 * rendercv_web/cvs.py`), fixed for Phase 4c:
 *
 * | Method | Path                                    | Notes                          |
 * |--------|-----------------------------------------|---------------------------------|
 * | GET    | /api/cvs                                 | newest first                    |
 * | POST   | /api/cvs                                 | 201, seeded defaults            |
 * | GET    | /api/cvs/{id}                            | 404 if missing/not owned        |
 * | PUT    | /api/cvs/{id}                            | 409 on lost optimistic race     |
 * | POST   | /api/cvs/{id}/duplicate                  | 201 "Copy of {name}"            |
 * | DELETE | /api/cvs/{id}                            | 204                              |
 * | GET    | /api/cvs/{id}/versions                   | newest first                    |
 * | POST   | /api/cvs/{id}/versions/{vid}/restore     | 200, same conflict shape as PUT |
 * | GET    | /api/cvs/{id}/theme-designs/{theme}      | 404 if none remembered          |
 * | PUT    | /api/cvs/{id}/theme-designs/{theme}      | 204, leaves updated_at alone    |
 *
 * Every function accepts an injectable `fetchImpl` (defaulting to the
 * shared, credentialed `apiFetch`) so tests never hit the network -- see
 * `cvs.test.ts`.
 *
 * Why `updated_at` stays a plain string end-to-end: it is an opaque
 * optimistic-concurrency token as far as the client is concerned
 * (`seen_updated_at` round-trips it verbatim back to the server). Parsing it
 * into a `Date` and re-serializing would risk losing precision the server
 * didn't -- comparisons and display both work fine off the ISO string.
 */

export interface CvSummary {
	id: number;
	name: string;
	updatedAt: string;
}

export interface CvDetail extends CvSummary {
	documents: CvDocuments;
}

export interface CvVersionSummary {
	id: number;
	createdAt: string;
}

export type UpdateCvResult =
	| { ok: true; updatedAt: string }
	| { ok: false; kind: 'not-found' }
	| { ok: false; kind: 'too-large' }
	| { ok: false; kind: 'conflict'; current: { updatedAt: string; documents: CvDocuments } }
	| { ok: false; kind: 'error'; message: string };

interface CvDocumentsPayload {
	cv_yaml: string;
	design_yaml: string;
	locale_yaml: string;
	settings_yaml: string;
}

interface CvSummaryPayload {
	id: number;
	name: string;
	updated_at: string;
}

interface CvDetailPayload extends CvSummaryPayload {
	documents: CvDocumentsPayload;
}

interface CvVersionSummaryPayload {
	id: number;
	created_at: string;
}

/** Converts the wire shape (`cv_yaml`, ...) into the app's `CvDocuments` (`cv`, ...). */
export function toDocuments(payload: CvDocumentsPayload): CvDocuments {
	return {
		cv: payload.cv_yaml,
		design: payload.design_yaml,
		locale: payload.locale_yaml,
		settings: payload.settings_yaml
	};
}

/** Converts `CvDocuments` (`cv`, ...) into the wire shape (`cv_yaml`, ...). */
export function toPayload(docs: CvDocuments): CvDocumentsPayload {
	return {
		cv_yaml: docs.cv,
		design_yaml: docs.design,
		locale_yaml: docs.locale,
		settings_yaml: docs.settings
	};
}

function toSummary(payload: CvSummaryPayload): CvSummary {
	return { id: payload.id, name: payload.name, updatedAt: payload.updated_at };
}

function toDetail(payload: CvDetailPayload): CvDetail {
	return { ...toSummary(payload), documents: toDocuments(payload.documents) };
}

async function unexpectedError(response: Response): Promise<{ ok: false; kind: 'error'; message: string }> {
	const text = await response.text().catch(() => '');
	return { ok: false, kind: 'error', message: text || `Request failed with status ${response.status}` };
}

/** `GET /api/cvs` -- every saved CV, newest-updated first. */
export async function listCvs(fetchImpl: typeof fetch = apiFetch): Promise<CvSummary[]> {
	const response = await fetchImpl('/api/cvs');
	if (!response.ok) throw new Error(`GET /api/cvs failed with status ${response.status}`);
	const body = (await response.json()) as CvSummaryPayload[];
	return body.map(toSummary);
}

/** `POST /api/cvs` -- creates a new CV seeded with the editor's default documents. */
export async function createCv(name?: string, fetchImpl: typeof fetch = apiFetch): Promise<CvDetail> {
	const response = await fetchImpl('/api/cvs', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify(name ? { name } : {})
	});
	if (!response.ok) throw new Error(`POST /api/cvs failed with status ${response.status}`);
	return toDetail((await response.json()) as CvDetailPayload);
}

/** `GET /api/cvs/{id}` -- one CV, in full. `null` if it doesn't exist (or isn't owned). */
export async function getCv(id: number, fetchImpl: typeof fetch = apiFetch): Promise<CvDetail | null> {
	const response = await fetchImpl(`/api/cvs/${id}`);
	if (response.status === 404) return null;
	if (!response.ok) throw new Error(`GET /api/cvs/${id} failed with status ${response.status}`);
	return toDetail((await response.json()) as CvDetailPayload);
}

export interface UpdateCvRequest {
	name: string;
	documents: CvDocuments;
	seenUpdatedAt: string;
}

/** `PUT /api/cvs/{id}` -- the autosave write; fails with `conflict` if the CV changed since `seenUpdatedAt`. */
export async function updateCv(
	id: number,
	request: UpdateCvRequest,
	fetchImpl: typeof fetch = apiFetch,
	init: RequestInit = {}
): Promise<UpdateCvResult> {
	const response = await fetchImpl(`/api/cvs/${id}`, {
		...init,
		method: 'PUT',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({
			name: request.name,
			documents: toPayload(request.documents),
			seen_updated_at: request.seenUpdatedAt
		})
	});

	if (response.status === 200) {
		const body = (await response.json()) as { updated_at: string };
		return { ok: true, updatedAt: body.updated_at };
	}
	if (response.status === 404) return { ok: false, kind: 'not-found' };
	if (response.status === 413) return { ok: false, kind: 'too-large' };
	if (response.status === 409) {
		const body = (await response.json()) as { current: { updated_at: string; documents: CvDocumentsPayload } };
		return {
			ok: false,
			kind: 'conflict',
			current: { updatedAt: body.current.updated_at, documents: toDocuments(body.current.documents) }
		};
	}
	return await unexpectedError(response);
}

/** `POST /api/cvs/{id}/duplicate` -- creates a copy named `Copy of {name}`. */
export async function duplicateCv(id: number, fetchImpl: typeof fetch = apiFetch): Promise<CvDetail | null> {
	const response = await fetchImpl(`/api/cvs/${id}/duplicate`, { method: 'POST' });
	if (response.status === 404) return null;
	if (!response.ok) throw new Error(`POST /api/cvs/${id}/duplicate failed with status ${response.status}`);
	return toDetail((await response.json()) as CvDetailPayload);
}

/** `DELETE /api/cvs/{id}`. Returns `false` if the CV didn't exist (or wasn't owned). */
export async function deleteCv(id: number, fetchImpl: typeof fetch = apiFetch): Promise<boolean> {
	const response = await fetchImpl(`/api/cvs/${id}`, { method: 'DELETE' });
	if (response.status === 404) return false;
	if (response.status !== 204) throw new Error(`DELETE /api/cvs/${id} failed with status ${response.status}`);
	return true;
}

/** `GET /api/cvs/{id}/versions` -- autosave snapshots, newest first. */
export async function listVersions(
	id: number,
	fetchImpl: typeof fetch = apiFetch
): Promise<CvVersionSummary[] | null> {
	const response = await fetchImpl(`/api/cvs/${id}/versions`);
	if (response.status === 404) return null;
	if (!response.ok) throw new Error(`GET /api/cvs/${id}/versions failed with status ${response.status}`);
	const body = (await response.json()) as CvVersionSummaryPayload[];
	return body.map((v) => ({ id: v.id, createdAt: v.created_at }));
}

/** `POST /api/cvs/{id}/versions/{versionId}/restore` -- restores a snapshot as a new autosave write. */
export async function restoreVersion(
	id: number,
	versionId: number,
	fetchImpl: typeof fetch = apiFetch
): Promise<UpdateCvResult> {
	const response = await fetchImpl(`/api/cvs/${id}/versions/${versionId}/restore`, { method: 'POST' });

	if (response.status === 200) {
		const body = (await response.json()) as { updated_at: string };
		return { ok: true, updatedAt: body.updated_at };
	}
	if (response.status === 404) return { ok: false, kind: 'not-found' };
	if (response.status === 409) {
		const body = (await response.json()) as { current: { updated_at: string; documents: CvDocumentsPayload } };
		return {
			ok: false,
			kind: 'conflict',
			current: { updatedAt: body.current.updated_at, documents: toDocuments(body.current.documents) }
		};
	}
	return await unexpectedError(response);
}

/** A `design:` mapping, as the Design form's sync holds it. */
export type DesignMapping = Record<string, unknown>;

/**
 * `GET /api/cvs/{id}/theme-designs/{theme}` -- the design this CV had the
 * last time the user switched away from `theme`, on any device.
 *
 * Returns `null` when nothing is remembered (a 404: the theme was never
 * left, or the CV is gone). Throws on any other failure so the caller can
 * tell "nothing saved" apart from "could not ask" and fall back to what it
 * remembers locally.
 */
export async function getThemeDesign(
	id: number,
	theme: string,
	fetchImpl: typeof fetch = apiFetch
): Promise<DesignMapping | null> {
	const response = await fetchImpl(`/api/cvs/${id}/theme-designs/${encodeURIComponent(theme)}`);
	if (response.status === 404) return null;
	if (!response.ok) {
		throw new Error(`GET /api/cvs/${id}/theme-designs/${theme} failed with status ${response.status}`);
	}
	const body = (await response.json()) as { design: DesignMapping };
	return body.design;
}

/**
 * `PUT /api/cvs/{id}/theme-designs/{theme}` -- remembers `design` as this
 * CV's design under `theme`. Resolves `false` instead of throwing on
 * failure: losing this write must not stop the theme switch itself.
 */
export async function putThemeDesign(
	id: number,
	theme: string,
	design: DesignMapping,
	fetchImpl: typeof fetch = apiFetch
): Promise<boolean> {
	try {
		const response = await fetchImpl(`/api/cvs/${id}/theme-designs/${encodeURIComponent(theme)}`, {
			method: 'PUT',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ design })
		});
		return response.status === 204;
	} catch {
		return false;
	}
}

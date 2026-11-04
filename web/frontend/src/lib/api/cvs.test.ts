import { describe, it, expect, vi } from 'vitest';
import {
	listCvs,
	createCv,
	getCv,
	updateCv,
	duplicateCv,
	deleteCv,
	listVersions,
	restoreVersion,
	getThemeDesign,
	putThemeDesign
} from './cvs';
import type { CvDocuments } from '$lib/stores/documents';

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });
}

const documents: CvDocuments = { cv: 'cv:\n  name: Jo\n', design: '', locale: '', settings: '' };
const documentsPayload = {
	cv_yaml: documents.cv,
	design_yaml: documents.design,
	locale_yaml: documents.locale,
	settings_yaml: documents.settings
};

describe('listCvs', () => {
	it('maps the wire shape (updated_at) to the app shape (updatedAt)', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(200, [{ id: 2, name: 'B', updated_at: '2026-01-02T00:00:00Z' }])
		);
		const result = await listCvs(fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith('/api/cvs');
		expect(result).toEqual([{ id: 2, name: 'B', updatedAt: '2026-01-02T00:00:00Z' }]);
	});
});

describe('createCv', () => {
	it('posts an optional name and returns the full CV', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(201, { id: 1, name: 'Untitled CV', updated_at: 't0', documents: documentsPayload })
		);
		const result = await createCv(undefined, fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/cvs',
			expect.objectContaining({ method: 'POST', body: JSON.stringify({}) })
		);
		expect(result).toEqual({ id: 1, name: 'Untitled CV', updatedAt: 't0', documents });
	});

	it('sends the name when provided', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(201, { id: 1, name: 'My CV', updated_at: 't0', documents: documentsPayload })
		);
		await createCv('My CV', fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/cvs',
			expect.objectContaining({ body: JSON.stringify({ name: 'My CV' }) })
		);
	});
});

describe('getCv', () => {
	it('returns null on 404', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 404 }));
		expect(await getCv(999, fetchImpl)).toBeNull();
	});

	it('returns the full CV on 200', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(200, { id: 1, name: 'A', updated_at: 't0', documents: documentsPayload })
		);
		const result = await getCv(1, fetchImpl);
		expect(result).toEqual({ id: 1, name: 'A', updatedAt: 't0', documents });
	});
});

describe('updateCv', () => {
	it('PUTs the wire shape and returns updatedAt on 200', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { updated_at: 't1' }));
		const result = await updateCv(1, { name: 'A', documents, seenUpdatedAt: 't0' }, fetchImpl);

		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/cvs/1',
			expect.objectContaining({
				method: 'PUT',
				body: JSON.stringify({ name: 'A', documents: documentsPayload, seen_updated_at: 't0' })
			})
		);
		expect(result).toEqual({ ok: true, updatedAt: 't1' });
	});

	it('surfaces a 409 conflict with the server current state', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(409, { current: { updated_at: 'tserver', documents: documentsPayload } })
		);
		const result = await updateCv(1, { name: 'A', documents, seenUpdatedAt: 't0' }, fetchImpl);
		expect(result).toEqual({
			ok: false,
			kind: 'conflict',
			current: { updatedAt: 'tserver', documents }
		});
	});

	it('surfaces a 404 as not-found', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 404 }));
		const result = await updateCv(1, { name: 'A', documents, seenUpdatedAt: 't0' }, fetchImpl);
		expect(result).toEqual({ ok: false, kind: 'not-found' });
	});

	it('surfaces a 413 as too-large', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 413 }));
		const result = await updateCv(1, { name: 'A', documents, seenUpdatedAt: 't0' }, fetchImpl);
		expect(result).toEqual({ ok: false, kind: 'too-large' });
	});

	it('forwards extra fetch init (e.g. keepalive)', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { updated_at: 't1' }));
		await updateCv(1, { name: 'A', documents, seenUpdatedAt: 't0' }, fetchImpl, { keepalive: true });
		expect(fetchImpl).toHaveBeenCalledWith('/api/cvs/1', expect.objectContaining({ keepalive: true }));
	});
});

describe('duplicateCv', () => {
	it('posts to the duplicate endpoint and returns the copy', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(201, { id: 2, name: 'Copy of A', updated_at: 't0', documents: documentsPayload })
		);
		const result = await duplicateCv(1, fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith('/api/cvs/1/duplicate', expect.objectContaining({ method: 'POST' }));
		expect(result).toEqual({ id: 2, name: 'Copy of A', updatedAt: 't0', documents });
	});
});

describe('deleteCv', () => {
	it('returns true on 204', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
		expect(await deleteCv(1, fetchImpl)).toBe(true);
	});

	it('returns false on 404', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 404 }));
		expect(await deleteCv(1, fetchImpl)).toBe(false);
	});
});

describe('listVersions / restoreVersion', () => {
	it('lists versions, mapping created_at to createdAt', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, [{ id: 5, created_at: 't5' }]));
		const result = await listVersions(1, fetchImpl);
		expect(result).toEqual([{ id: 5, createdAt: 't5' }]);
	});

	it('restoreVersion posts to the restore endpoint', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { updated_at: 't6' }));
		const result = await restoreVersion(1, 5, fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/cvs/1/versions/5/restore',
			expect.objectContaining({ method: 'POST' })
		);
		expect(result).toEqual({ ok: true, updatedAt: 't6' });
	});

	it('restoreVersion surfaces a 409 conflict', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(409, { current: { updated_at: 'tserver', documents: documentsPayload } })
		);
		const result = await restoreVersion(1, 5, fetchImpl);
		expect(result).toEqual({ ok: false, kind: 'conflict', current: { updatedAt: 'tserver', documents } });
	});
});

describe('getThemeDesign', () => {
	it('returns the remembered design', async () => {
		const design = { theme: 'harvard', entries: { space_between_entries: '0.7em' } };
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { design }));
		const result = await getThemeDesign(4, 'harvard', fetchImpl);
		expect(fetchImpl).toHaveBeenCalledWith('/api/cvs/4/theme-designs/harvard');
		expect(result).toEqual(design);
	});

	it('returns null when nothing is remembered', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(404, { detail: 'No design saved for this theme.' }));
		expect(await getThemeDesign(4, 'harvard', fetchImpl)).toBeNull();
	});

	it('throws on any other failure, so the caller can fall back', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(500, {}));
		await expect(getThemeDesign(4, 'harvard', fetchImpl)).rejects.toThrow();
	});
});

describe('putThemeDesign', () => {
	it('PUTs the design and reports success on 204', async () => {
		const design = { theme: 'harvard' };
		const fetchImpl = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
		expect(await putThemeDesign(4, 'harvard', design, fetchImpl)).toBe(true);
		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/cvs/4/theme-designs/harvard',
			expect.objectContaining({ method: 'PUT', body: JSON.stringify({ design }) })
		);
	});

	it('reports failure instead of throwing', async () => {
		const failing = vi.fn().mockRejectedValue(new Error('offline'));
		expect(await putThemeDesign(4, 'harvard', { theme: 'harvard' }, failing)).toBe(false);
		const refused = vi.fn().mockResolvedValue(jsonResponse(422, {}));
		expect(await putThemeDesign(4, 'harvard', { theme: 'harvard' }, refused)).toBe(false);
	});
});

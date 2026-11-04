import { describe, it, expect, vi } from 'vitest';
import { renderPreview, parseValidationErrors } from './render';
import type { CvDocuments } from '$lib/stores/documents';

const docs: CvDocuments = {
	cv: 'cv:\n  name: John Doe\n  sections: {}\n',
	design: '',
	locale: '',
	settings: 'settings:\n  pdf_title: NAME - CV\n'
};

describe('renderPreview', () => {
	it('posts the four documents as JSON to /api/render', async () => {
		const fakeBlob = new Blob(['%PDF-1.7'], { type: 'application/pdf' });
		const fetchMock = vi.fn(async () => new Response(fakeBlob, { status: 200 }));

		const result = await renderPreview(docs, fetchMock as unknown as typeof fetch);

		expect(fetchMock).toHaveBeenCalledTimes(1);
		const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
		expect(url).toBe('/api/render');
		expect(init.method).toBe('POST');
		expect(JSON.parse(init.body as string)).toEqual({
			cv_yaml: docs.cv,
			design_yaml: docs.design,
			locale_yaml: docs.locale,
			settings_yaml: docs.settings
		});

		expect(result.ok).toBe(true);
		if (result.ok) {
			expect(result.blob.type).toBe('application/pdf');
		}
	});

	it('returns structured errors on a 422 response', async () => {
		const body = {
			errors: [
				{
					location: 'cv.name',
					message: 'Field required',
					yaml_source: 'main_yaml_file',
					yaml_line: 2
				}
			]
		};
		const fetchMock = vi.fn(
			async () =>
				new Response(JSON.stringify(body), {
					status: 422,
					headers: { 'content-type': 'application/json' }
				})
		);

		const result = await renderPreview(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors).toEqual([
				{
					location: 'cv.name',
					message: 'Field required',
					yaml_source: 'main_yaml_file',
					yaml_line: 2
				}
			]);
		}
	});

	it('shows a friendly generic message (never the raw body) on an unexpected status', async () => {
		const fetchMock = vi.fn(async () => new Response('boom', { status: 500 }));

		const result = await renderPreview(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors[0].message).toBe('Something went wrong — please try again.');
			expect(result.errors[0].message).not.toContain('boom');
			expect(result.errors[0].kind).toBe('system');
		}
	});

	it('surfaces error_id from a structured 500 body without dumping the raw JSON', async () => {
		const fetchMock = vi.fn(
			async () =>
				new Response(JSON.stringify({ error_id: 'render-500-xyz', message: 'Typst compile failed' }), {
					status: 500,
					headers: { 'content-type': 'application/json' }
				})
		);

		const result = await renderPreview(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors[0].errorId).toBe('render-500-xyz');
			expect(result.errors[0].message).not.toContain('Typst compile failed');
		}
	});
});

describe('parseValidationErrors', () => {
	it('normalizes a well-formed payload', () => {
		const errors = parseValidationErrors({
			errors: [
				{
					location: 'design.theme',
					message: 'Unknown theme',
					yaml_source: 'design_yaml_file',
					yaml_line: 5
				}
			]
		});
		expect(errors).toEqual([
			{
				location: 'design.theme',
				message: 'Unknown theme',
				yaml_source: 'design_yaml_file',
				yaml_line: 5
			}
		]);
	});

	it('fills in defaults for missing fields', () => {
		const errors = parseValidationErrors({ errors: [{}] });
		expect(errors).toEqual([
			{ location: 'unknown', message: 'Invalid value.', yaml_source: 'main_yaml_file', yaml_line: null }
		]);
	});

	it('returns an empty array for a malformed payload', () => {
		expect(parseValidationErrors(null)).toEqual([]);
		expect(parseValidationErrors({})).toEqual([]);
		expect(parseValidationErrors({ errors: 'nope' })).toEqual([]);
	});
});

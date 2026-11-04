import { describe, it, expect, vi } from 'vitest';
import { validateDocuments, parseValidationErrors } from './validate';
import type { CvDocuments } from '$lib/stores/documents';

const docs: CvDocuments = {
	cv: 'cv:\n  name: John Doe\n  phone: abc\n',
	design: '',
	locale: '',
	settings: ''
};

describe('validateDocuments', () => {
	it('posts the four documents as JSON to /api/validate', async () => {
		const fetchMock = vi.fn(async () => new Response(null, { status: 200 }));

		const result = await validateDocuments(docs, fetchMock as unknown as typeof fetch);

		expect(fetchMock).toHaveBeenCalledTimes(1);
		const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
		expect(url).toBe('/api/validate');
		expect(init.method).toBe('POST');
		expect(JSON.parse(init.body as string)).toEqual({
			cv_yaml: docs.cv,
			design_yaml: docs.design,
			locale_yaml: docs.locale,
			settings_yaml: docs.settings
		});
		expect(result).toEqual({ ok: true });
	});

	it('returns structured errors with yaml_source on a 422 response', async () => {
		const body = {
			errors: [
				{
					location: 'cv.phone',
					message: 'This is not a valid phone number.',
					yaml_source: 'main_yaml_file',
					yaml_line: 3
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

		const result = await validateDocuments(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors).toEqual([
				{
					location: 'cv.phone',
					message: 'This is not a valid phone number.',
					yaml_source: 'main_yaml_file',
					yaml_line: 3
				}
			]);
		}
	});

	it('shows a friendly generic message (never the raw body) on a plain-text unexpected status', async () => {
		const fetchMock = vi.fn(async () => new Response('boom', { status: 500 }));

		const result = await validateDocuments(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors).toEqual([
				{
					location: null,
					message: 'Something went wrong — please try again.',
					yaml_source: 'main_yaml_file',
					yaml_line: null,
					kind: 'system',
					errorId: null
				}
			]);
		}
	});

	it('surfaces error_id from a structured 500 body without dumping the raw JSON', async () => {
		const fetchMock = vi.fn(
			async () =>
				new Response(JSON.stringify({ error_id: 'abc-123', message: 'Internal error detail' }), {
					status: 500,
					headers: { 'content-type': 'application/json' }
				})
		);

		const result = await validateDocuments(docs, fetchMock as unknown as typeof fetch);

		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors).toHaveLength(1);
			expect(result.errors[0].kind).toBe('system');
			expect(result.errors[0].errorId).toBe('abc-123');
			expect(result.errors[0].message).toBe('Something went wrong — please try again.');
			expect(result.errors[0].message).not.toContain('Internal error detail');
		}
	});
});

describe('parseValidationErrors', () => {
	it('maps each yaml_source string to itself when valid', () => {
		const sources = ['main_yaml_file', 'design_yaml_file', 'locale_yaml_file', 'settings_yaml_file'];
		const errors = parseValidationErrors({
			errors: sources.map((yaml_source) => ({ location: 'x', message: 'y', yaml_source, yaml_line: 1 }))
		});
		expect(errors.map((e) => e.yaml_source)).toEqual(sources);
	});

	it('defaults an unrecognized or missing yaml_source to main_yaml_file', () => {
		const errors = parseValidationErrors({
			errors: [{ location: 'x', message: 'y', yaml_source: 'bogus', yaml_line: 1 }, {}]
		});
		expect(errors[0].yaml_source).toBe('main_yaml_file');
		expect(errors[1].yaml_source).toBe('main_yaml_file');
	});

	it('returns an empty array for a malformed payload', () => {
		expect(parseValidationErrors(null)).toEqual([]);
		expect(parseValidationErrors({})).toEqual([]);
		expect(parseValidationErrors({ errors: 'nope' })).toEqual([]);
	});
});

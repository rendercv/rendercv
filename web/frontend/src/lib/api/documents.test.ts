import { describe, it, expect, vi } from 'vitest';
import { parseCvDocument, patchCvDocument } from './documents';

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json' }
	});
}

describe('parseCvDocument', () => {
	it('posts {yaml} and returns the parsed data on 200', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { data: { cv: { name: 'Jo' } } }));

		const result = await parseCvDocument('cv:\n  name: Jo\n', fetchImpl);

		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/documents/parse',
			expect.objectContaining({
				method: 'POST',
				body: JSON.stringify({ yaml: 'cv:\n  name: Jo\n' })
			})
		);
		expect(result).toEqual({ ok: true, data: { cv: { name: 'Jo' } } });
	});

	it('returns structured errors on 422', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(422, {
				errors: [
					{ location: 'cv.name', message: 'bad', yaml_source: 'main_yaml_file', yaml_line: 2 }
				]
			})
		);

		const result = await parseCvDocument('cv:\n  name: 1\n', fetchImpl);
		expect(result.ok).toBe(false);
		if (!result.ok) {
			expect(result.errors).toEqual([
				{ location: 'cv.name', message: 'bad', yaml_source: 'main_yaml_file', yaml_line: 2 }
			]);
		}
	});
});

describe('patchCvDocument', () => {
	it('posts {yaml, ops} and returns the new yaml on 200', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { yaml: 'cv:\n  name: Jane\n' }));
		const ops = [{ op: 'set' as const, path: ['cv', 'name'], value: 'Jane' }];

		const result = await patchCvDocument('cv:\n  name: Jo\n', ops, fetchImpl);

		expect(fetchImpl).toHaveBeenCalledWith(
			'/api/documents/patch',
			expect.objectContaining({
				method: 'POST',
				body: JSON.stringify({ yaml: 'cv:\n  name: Jo\n', ops })
			})
		);
		expect(result).toEqual({ ok: true, yaml: 'cv:\n  name: Jane\n' });
	});

	it('surfaces a 400 op error with its op_index', async () => {
		const fetchImpl = vi
			.fn()
			.mockResolvedValue(jsonResponse(400, { error: { op_index: 1, message: 'bad path' } }));

		const result = await patchCvDocument('cv:\n  name: Jo\n', [], fetchImpl);
		expect(result).toEqual({
			ok: false,
			kind: 'op-error',
			error: { op_index: 1, message: 'bad path' }
		});
	});

	it('surfaces a 422 as validation errors', async () => {
		const fetchImpl = vi.fn().mockResolvedValue(
			jsonResponse(422, {
				errors: [{ location: 'cv.name', message: 'bad', yaml_source: 'main_yaml_file', yaml_line: 1 }]
			})
		);

		const result = await patchCvDocument('cv:\n  name: 1\n', [], fetchImpl);
		expect(result.ok).toBe(false);
		if (!result.ok && result.kind === 'validation') {
			expect(result.errors[0].location).toBe('cv.name');
		} else {
			throw new Error('expected a validation result');
		}
	});
});

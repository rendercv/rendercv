import { parseValidationErrors, type ValidationError } from '$lib/api/validate';
import { apiFetch } from '$lib/api/http';
import type { PatchOp } from '$lib/form/patchOps';

/**
 * Client for the two form-sync endpoints being built in parallel (backend
 * contract, fixed for this phase):
 *
 * - `POST /api/documents/parse {yaml}` -> 200 `{data}` | 422 `{errors}`
 * - `POST /api/documents/patch {yaml, ops}` -> 200 `{yaml}` | 400 `{error}` | 422 `{errors}`
 *
 * These endpoints are NOT live yet (the other block is implementing them in
 * parallel) — every unit test in this codebase mocks `fetchImpl` rather than
 * hitting the network; see `formSync.test.ts`.
 */

export type ParseResult =
	| { ok: true; data: Record<string, unknown> }
	| { ok: false; errors: ValidationError[] };

export interface PatchOpError {
	op_index: number;
	message: string;
}

export type PatchResult =
	| { ok: true; yaml: string }
	| { ok: false; kind: 'op-error'; error: PatchOpError }
	| { ok: false; kind: 'validation'; errors: ValidationError[] };

/** Posts a single YAML document (the `cv` document, self-contained with its `cv:` top key) to `/api/documents/parse`. */
export async function parseCvDocument(
	yaml: string,
	fetchImpl: typeof fetch = apiFetch
): Promise<ParseResult> {
	const response = await fetchImpl('/api/documents/parse', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ yaml })
	});

	if (response.status === 200) {
		const body = (await response.json()) as { data: Record<string, unknown> };
		return { ok: true, data: body.data };
	}

	if (response.status === 422) {
		const body = await response.json().catch(() => ({ errors: [] }));
		return { ok: false, errors: parseValidationErrors(body) };
	}

	const text = await response.text().catch(() => '');
	return {
		ok: false,
		errors: [
			{
				location: null,
				message: text || `Parse failed with status ${response.status}`,
				yaml_source: 'main_yaml_file',
				yaml_line: null
			}
		]
	};
}

/** Posts a batch of ops (applied server-side to `yaml`) to `/api/documents/patch`. */
export async function patchCvDocument(
	yaml: string,
	ops: PatchOp[],
	fetchImpl: typeof fetch = apiFetch
): Promise<PatchResult> {
	const response = await fetchImpl('/api/documents/patch', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({ yaml, ops })
	});

	if (response.status === 200) {
		const body = (await response.json()) as { yaml: string };
		return { ok: true, yaml: body.yaml };
	}

	if (response.status === 400) {
		const body = (await response.json().catch(() => null)) as { error?: PatchOpError } | null;
		return {
			ok: false,
			kind: 'op-error',
			error: body?.error ?? { op_index: -1, message: `Patch failed with status 400` }
		};
	}

	if (response.status === 422) {
		const body = await response.json().catch(() => ({ errors: [] }));
		return { ok: false, kind: 'validation', errors: parseValidationErrors(body) };
	}

	const text = await response.text().catch(() => '');
	return {
		ok: false,
		kind: 'op-error',
		error: { op_index: -1, message: text || `Patch failed with status ${response.status}` }
	};
}

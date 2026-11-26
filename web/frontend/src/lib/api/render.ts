import type { CvDocuments } from '$lib/stores/documents';
import { genericSystemError, parseValidationErrors, type ValidationError } from '$lib/api/validate';
import { apiFetch } from '$lib/api/http';

export type { ValidationError } from '$lib/api/validate';

export type RenderResult =
	| { ok: true; blob: Blob }
	| { ok: false; errors: ValidationError[] };

/**
 * Posts the four CV documents to `/api/render` and returns either the PDF
 * bytes as a Blob, or the structured validation errors from a 422 response.
 *
 * Why: this is the one place that knows the request/response shape, so the
 * preview pane and its tests do not need to duplicate fetch/parsing logic.
 */
export async function renderPreview(
	docs: CvDocuments,
	fetchImpl: typeof fetch = apiFetch
): Promise<RenderResult> {
	const response = await fetchImpl('/api/render', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({
			cv_yaml: docs.cv,
			design_yaml: docs.design,
			locale_yaml: docs.locale,
			settings_yaml: docs.settings
		})
	});

	if (response.status === 200) {
		const blob = await response.blob();
		return { ok: true, blob };
	}

	if (response.status === 422) {
		const body = await response.json().catch(() => ({ errors: [] }));
		return { ok: false, errors: parseValidationErrors(body) };
	}

	return { ok: false, errors: [await genericSystemError(response)] };
}

export type ImagesResult =
	| { ok: true; blob: Blob; extension: 'png' | 'zip' }
	| { ok: false; errors: ValidationError[] };

/**
 * Posts the four documents to `/api/render/images` and returns the rendered
 * pages.
 *
 * Why the extension comes back with the blob: the server answers with a
 * bare PNG for a one-page CV and a zip of every page for a longer one, and
 * the caller has to name the downloaded file correctly without guessing.
 * `Content-Type` is the only thing that distinguishes them.
 */
export async function renderImages(
	docs: CvDocuments,
	fetchImpl: typeof fetch = apiFetch
): Promise<ImagesResult> {
	const response = await fetchImpl('/api/render/images', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({
			cv_yaml: docs.cv,
			design_yaml: docs.design,
			locale_yaml: docs.locale,
			settings_yaml: docs.settings
		})
	});

	if (response.status === 200) {
		const blob = await response.blob();
		const isZip = (response.headers.get('content-type') ?? '').includes('zip');
		return { ok: true, blob, extension: isZip ? 'zip' : 'png' };
	}

	if (response.status === 422) {
		const body = await response.json().catch(() => ({ errors: [] }));
		return { ok: false, errors: parseValidationErrors(body) };
	}

	return { ok: false, errors: [await genericSystemError(response)] };
}

export { parseValidationErrors } from '$lib/api/validate';

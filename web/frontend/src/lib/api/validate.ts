import type { CvDocuments } from '$lib/stores/documents';
import { apiFetch } from '$lib/api/http';

/** Which of the four YAML documents a validation error came from. */
export type YamlSource = 'main_yaml_file' | 'design_yaml_file' | 'locale_yaml_file' | 'settings_yaml_file';

/** A single structured validation error, as returned by the API on a 422. */
export interface ValidationError {
	location: string | null;
	message: string;
	yaml_source: YamlSource;
	yaml_line: number | null;
	/**
	 * `'field'` (the default, omitted) is a normal 422 validation error tied
	 * to a document/line. `'system'` is a non-422 failure (a 500, a network
	 * error, an unexpected status) that carries no useful location -- the UI
	 * shows a friendly generic line for these instead of the raw response
	 * body (see {@link genericSystemError}).
	 */
	kind?: 'field' | 'system';
	/** Only set for `kind: 'system'`, when the backend's error body included one (`{error_id, message}`) -- shown in small muted text so a user can reference it in a bug report without seeing the raw payload. */
	errorId?: string | null;
}

export type ValidateResult = { ok: true } | { ok: false; errors: ValidationError[] };

/** Normalizes the `{errors: [...]}` 422 payload into ValidationError[]. */
export function parseValidationErrors(body: unknown): ValidationError[] {
	if (
		typeof body !== 'object' ||
		body === null ||
		!('errors' in body) ||
		!Array.isArray((body as { errors: unknown }).errors)
	) {
		return [];
	}

	return (body as { errors: unknown[] }).errors.map((raw) => {
		const entry = (raw ?? {}) as Record<string, unknown>;
		const yamlSource: YamlSource =
			entry.yaml_source === 'design_yaml_file' ||
			entry.yaml_source === 'locale_yaml_file' ||
			entry.yaml_source === 'settings_yaml_file'
				? entry.yaml_source
				: 'main_yaml_file';
		return {
			location: typeof entry.location === 'string' ? entry.location : 'unknown',
			message: typeof entry.message === 'string' ? entry.message : 'Invalid value.',
			yaml_source: yamlSource,
			yaml_line: typeof entry.yaml_line === 'number' ? entry.yaml_line : null
		};
	});
}

/**
 * Builds the one `ValidationError` shown for a non-422 failure response
 * (a 500 `{error_id, message}` JSON body, a plain-text body, or anything
 * else this app didn't ask for). Always a friendly, fixed message -- never
 * the raw response body -- with the backend's `error_id` carried through
 * when the body happened to be JSON shaped like one, so the UI can show it
 * in small muted text instead of dumping JSON at the user.
 */
export async function genericSystemError(response: Response): Promise<ValidationError> {
	const text = await response.text().catch(() => '');
	let errorId: string | null = null;
	try {
		const parsed: unknown = JSON.parse(text);
		if (parsed && typeof parsed === 'object' && typeof (parsed as { error_id?: unknown }).error_id === 'string') {
			errorId = (parsed as { error_id: string }).error_id;
		}
	} catch {
		// Not JSON (or not the expected shape) -- plain text, no error_id to surface.
	}

	return {
		location: null,
		message: 'Something went wrong — please try again.',
		yaml_source: 'main_yaml_file',
		yaml_line: null,
		kind: 'system',
		errorId
	};
}

/**
 * Posts the four CV documents to `/api/validate` and returns either
 * confirmation the documents are valid, or the structured validation
 * errors from a 422 response.
 *
 * Why a separate call from `/api/render`: this runs on the same debounce
 * as the preview render but is the authoritative source for inline error
 * placement (line/tab), independent of whether a render is also possible
 * (e.g. a document can be schema-valid but still fail to render as a PDF).
 */
export async function validateDocuments(
	docs: CvDocuments,
	fetchImpl: typeof fetch = apiFetch
): Promise<ValidateResult> {
	const response = await fetchImpl('/api/validate', {
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
		return { ok: true };
	}

	if (response.status === 422) {
		const body = await response.json().catch(() => ({ errors: [] }));
		return { ok: false, errors: parseValidationErrors(body) };
	}

	return { ok: false, errors: [await genericSystemError(response)] };
}

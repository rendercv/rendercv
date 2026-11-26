import { DOCUMENT_KEYS, type DocumentKey } from '$lib/stores/documents';
import type { ValidationError, YamlSource } from '$lib/api/validate';

/** Maps a backend `yaml_source` to the editor tab that owns that document. */
export const YAML_SOURCE_TO_DOCUMENT_KEY: Record<YamlSource, DocumentKey> = {
	main_yaml_file: 'cv',
	design_yaml_file: 'design',
	locale_yaml_file: 'locale',
	settings_yaml_file: 'settings'
};

export function documentKeyForError(error: ValidationError): DocumentKey {
	return YAML_SOURCE_TO_DOCUMENT_KEY[error.yaml_source] ?? 'cv';
}

/** Whether a validation error's message identifies a YAML syntax problem. */
export function isSyntaxError(message: string): boolean {
	return message.startsWith('This is not a valid YAML file');
}

export type ErrorCategory = 'syntax' | 'schema';

export function classifyError(error: ValidationError): ErrorCategory {
	return isSyntaxError(error.message) ? 'syntax' : 'schema';
}

/** Groups validation errors by the tab (document) they belong to. */
export function groupErrorsByDocument(
	errors: ValidationError[]
): Record<DocumentKey, ValidationError[]> {
	const grouped = Object.fromEntries(DOCUMENT_KEYS.map((key) => [key, [] as ValidationError[]])) as Record<
		DocumentKey,
		ValidationError[]
	>;
	for (const error of errors) {
		grouped[documentKeyForError(error)].push(error);
	}
	return grouped;
}

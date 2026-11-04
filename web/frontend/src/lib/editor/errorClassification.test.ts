import { describe, it, expect } from 'vitest';
import {
	documentKeyForError,
	classifyError,
	groupErrorsByDocument,
	isSyntaxError
} from './errorClassification';
import type { ValidationError } from '$lib/api/validate';

function error(overrides: Partial<ValidationError>): ValidationError {
	return {
		location: 'cv.name',
		message: 'Field required',
		yaml_source: 'main_yaml_file',
		yaml_line: 1,
		...overrides
	};
}

describe('documentKeyForError', () => {
	it('maps every yaml_source to its tab', () => {
		expect(documentKeyForError(error({ yaml_source: 'main_yaml_file' }))).toBe('cv');
		expect(documentKeyForError(error({ yaml_source: 'design_yaml_file' }))).toBe('design');
		expect(documentKeyForError(error({ yaml_source: 'locale_yaml_file' }))).toBe('locale');
		expect(documentKeyForError(error({ yaml_source: 'settings_yaml_file' }))).toBe('settings');
	});
});

describe('isSyntaxError / classifyError', () => {
	it('recognizes the YAML parse-error message prefix', () => {
		expect(isSyntaxError('This is not a valid YAML file. mapping values are not allowed here')).toBe(true);
		expect(isSyntaxError('This is not a valid phone number.')).toBe(false);
	});

	it('classifies errors as syntax or schema', () => {
		expect(classifyError(error({ message: 'This is not a valid YAML file. bad indent' }))).toBe('syntax');
		expect(classifyError(error({ message: 'This is not a valid phone number.' }))).toBe('schema');
	});
});

describe('groupErrorsByDocument', () => {
	it('buckets errors by tab, including empty tabs', () => {
		const grouped = groupErrorsByDocument([
			error({ yaml_source: 'main_yaml_file', message: 'a' }),
			error({ yaml_source: 'main_yaml_file', message: 'b' }),
			error({ yaml_source: 'settings_yaml_file', message: 'c' })
		]);

		expect(grouped.cv.map((e) => e.message)).toEqual(['a', 'b']);
		expect(grouped.settings.map((e) => e.message)).toEqual(['c']);
		expect(grouped.design).toEqual([]);
		expect(grouped.locale).toEqual([]);
	});
});

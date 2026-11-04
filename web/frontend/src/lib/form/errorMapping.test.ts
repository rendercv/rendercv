import { describe, it, expect } from 'vitest';
import { errorsAtPath, errorsUnderPath, hasUnclaimedErrors } from './errorMapping';
import type { ValidationError } from '$lib/api/validate';

function error(location: string | null, message = 'bad value'): ValidationError {
	return { location, message, yaml_source: 'main_yaml_file', yaml_line: 3 };
}

describe('errorsAtPath', () => {
	it('matches only the exact dotted path', () => {
		const errors = [
			error('cv.sections.Education.0.degree'),
			error('cv.sections.Education.0.institution'),
			error('cv.name')
		];
		expect(errorsAtPath(errors, ['cv', 'sections', 'Education', 0, 'degree'])).toEqual([errors[0]]);
	});
});

describe('errorsUnderPath', () => {
	it('matches the path itself and anything nested under it', () => {
		const errors = [
			error('cv.sections.Education.0.degree'),
			error('cv.sections.Education.0'),
			error('cv.sections.Experience.0.company'),
			error('cv.name')
		];
		const underEntry = errorsUnderPath(errors, ['cv', 'sections', 'Education', 0]);
		expect(underEntry).toEqual([errors[0], errors[1]]);
	});

	it('does not false-positive on a path that is merely a string prefix (Education vs EducationX)', () => {
		const errors = [error('cv.sections.EducationExtra.0.degree')];
		expect(errorsUnderPath(errors, ['cv', 'sections', 'Education'])).toEqual([]);
	});
});

describe('hasUnclaimedErrors', () => {
	it('is true for a null location or one outside cv.*', () => {
		expect(hasUnclaimedErrors([error(null)])).toBe(true);
		expect(hasUnclaimedErrors([error('design.theme')])).toBe(true);
	});

	it('is false once every error is under cv.*', () => {
		expect(hasUnclaimedErrors([error('cv.name'), error('cv.sections.Education.0.degree')])).toBe(false);
	});
});

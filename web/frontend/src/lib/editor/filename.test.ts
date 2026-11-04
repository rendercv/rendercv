import { describe, it, expect } from 'vitest';
import { derivePdfFilename, deriveYamlFilename } from './filename';
import type { CvDocuments } from '$lib/stores/documents';

function docs(overrides: Partial<CvDocuments> = {}): CvDocuments {
	return {
		cv: 'cv:\n  name: John Doe\n  sections: {}\n',
		design: '',
		locale: '',
		settings: 'settings:\n  pdf_title: NAME - CV\n',
		...overrides
	};
}

describe('derivePdfFilename', () => {
	it('substitutes NAME with the CV name and appends .pdf', () => {
		expect(derivePdfFilename(docs())).toBe('John Doe - CV.pdf');
	});

	it('falls back to cv.pdf when settings has no pdf_title', () => {
		expect(derivePdfFilename(docs({ settings: '' }))).toBe('cv.pdf');
	});

	it('falls back to cv.pdf when pdf_title is blank', () => {
		expect(derivePdfFilename(docs({ settings: 'settings:\n  pdf_title: ""\n' }))).toBe('cv.pdf');
	});

	it('uses the literal pdf_title when the cv has no name yet', () => {
		expect(derivePdfFilename(docs({ cv: 'cv:\n  sections: {}\n' }))).toBe('NAME - CV.pdf');
	});

	it('does not duplicate the .pdf extension if already present', () => {
		expect(
			derivePdfFilename(
				docs({ settings: 'settings:\n  pdf_title: My Resume.pdf\n' })
			)
		).toBe('My Resume.pdf');
	});

	it('strips filesystem-unsafe characters', () => {
		expect(
			derivePdfFilename(
				docs({
					cv: 'cv:\n  name: Jane/Doe\n',
					settings: 'settings:\n  pdf_title: NAME - CV\n'
				})
			)
		).toBe('JaneDoe - CV.pdf');
	});
});

describe('deriveYamlFilename', () => {
	it('matches the PDF name so both files sort together', () => {
		expect(deriveYamlFilename(docs())).toBe('John Doe - CV.yaml');
		expect(derivePdfFilename(docs())).toBe('John Doe - CV.pdf');
	});

	it('inherits the PDF fallback', () => {
		expect(deriveYamlFilename(docs({ settings: '' }))).toBe('cv.yaml');
	});
});

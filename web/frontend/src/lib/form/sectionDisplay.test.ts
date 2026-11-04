import { describe, it, expect } from 'vitest';
import { addEntryLabel, displaySectionTitle } from './sectionDisplay';

describe('displaySectionTitle', () => {
	it('capitalizes each word of an all-lowercase or snake_case title', () => {
		expect(displaySectionTitle('education')).toBe('Education');
		expect(displaySectionTitle('professional_experience')).toBe('Professional Experience');
		expect(displaySectionTitle('open_source_projects')).toBe('Open Source Projects');
	});

	it('leaves a title with any uppercase letter alone (apart from underscore spacing)', () => {
		expect(displaySectionTitle('Experience')).toBe('Experience');
		expect(displaySectionTitle('Open Source Projects')).toBe('Open Source Projects');
		expect(displaySectionTitle('My_Custom_Section')).toBe('My Custom Section');
	});

	it('handles an empty string without throwing', () => {
		expect(displaySectionTitle('')).toBe('');
	});
});

describe('addEntryLabel', () => {
	it('singularizes the last word of a plural title and lowercases the phrase', () => {
		expect(addEntryLabel('Education')).toBe('education');
		expect(addEntryLabel('Experience')).toBe('experience');
		expect(addEntryLabel('Publications')).toBe('publication');
		expect(addEntryLabel('Skills')).toBe('skill');
		expect(addEntryLabel('Extracurricular Activities')).toBe('extracurricular activity');
	});

	it('does not mangle a word that only coincidentally ends in a double s', () => {
		expect(addEntryLabel('Awards and Achievements')).toBe('awards and achievement');
	});

	it('falls back to "entry" for a blank title', () => {
		expect(addEntryLabel('   ')).toBe('entry');
	});
});

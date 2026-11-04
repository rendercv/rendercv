import { describe, it, expect } from 'vitest';
import {
	ENTRY_TYPES,
	entrySkeleton,
	entrySummaryText,
	getCvHeaderFields,
	getEntryTypeDescriptors,
	inferEntryType
} from './cvSchema';
import type { JsonSchemaDocument } from './types';
import schemaFixture from './fixtures/schema.snapshot.json';

const schema = schemaFixture as unknown as JsonSchemaDocument;

describe('getCvHeaderFields', () => {
	it('excludes sections (owned by the dedicated SectionsEditor)', () => {
		const fields = getCvHeaderFields(schema);
		expect(fields.some((f) => f.key === 'sections')).toBe(false);
		expect(fields.some((f) => f.key === 'name')).toBe(true);
	});
});

describe('getEntryTypeDescriptors', () => {
	const descriptors = getEntryTypeDescriptors(schema);

	it('returns all 9 entry types with a schema-derived hint', () => {
		expect(descriptors.map((d) => d.type)).toEqual(ENTRY_TYPES as unknown as string[]);
		for (const d of descriptors) {
			expect(d.hint.length).toBeGreaterThan(0);
		}
	});

	it('TextEntry has no fields; every other type resolves its schema fields', () => {
		const text = descriptors.find((d) => d.type === 'TextEntry');
		expect(text?.fields).toEqual([]);

		const education = descriptors.find((d) => d.type === 'EducationEntry');
		expect(education?.fields.map((f) => f.key)).toContain('institution');
	});
});

describe('inferEntryType', () => {
	it('infers each of the 9 types from field presence', () => {
		expect(inferEntryType('Just a line of text')).toBe('TextEntry');
		expect(inferEntryType({ institution: 'MIT', area: 'CS' })).toBe('EducationEntry');
		expect(inferEntryType({ company: 'Acme', position: 'Engineer' })).toBe('ExperienceEntry');
		expect(inferEntryType({ title: 'A paper', authors: ['A'] })).toBe('PublicationEntry');
		expect(inferEntryType({ name: 'Some Project' })).toBe('NormalEntry');
		expect(inferEntryType({ bullet: 'Did a thing' })).toBe('BulletEntry');
		expect(inferEntryType({ number: 'One' })).toBe('NumberedEntry');
		expect(inferEntryType({ reversed_number: 'Five' })).toBe('ReversedNumberedEntry');
		expect(inferEntryType({ label: 'Languages', details: 'English' })).toBe('OneLineEntry');
	});

	it('returns null for unrecognized shapes', () => {
		expect(inferEntryType({ unknown_field: 1 })).toBeNull();
		expect(inferEntryType(42)).toBeNull();
		expect(inferEntryType(null)).toBeNull();
	});

	it('prioritizes institution/company/title+authors/name ahead of the simpler single-field types', () => {
		// An entry could (in principle) carry extra keys beyond its required
		// ones; the priority order must still land on the richer type.
		expect(inferEntryType({ institution: 'MIT', area: 'CS', bullet: 'not this' })).toBe(
			'EducationEntry'
		);
	});
});

describe('entrySkeleton', () => {
	it('builds a value with only the required fields, defaulted by kind', () => {
		const descriptors = getEntryTypeDescriptors(schema);
		const byType = Object.fromEntries(descriptors.map((d) => [d.type, d.fields]));

		expect(entrySkeleton('TextEntry', [])).toBe('');
		expect(entrySkeleton('BulletEntry', byType.BulletEntry)).toEqual({ bullet: '' });
		expect(entrySkeleton('NumberedEntry', byType.NumberedEntry)).toEqual({ number: '' });
		expect(entrySkeleton('ReversedNumberedEntry', byType.ReversedNumberedEntry)).toEqual({
			reversed_number: ''
		});
		expect(entrySkeleton('OneLineEntry', byType.OneLineEntry)).toEqual({ label: '', details: '' });
		expect(entrySkeleton('NormalEntry', byType.NormalEntry)).toEqual({ name: '' });
		expect(entrySkeleton('EducationEntry', byType.EducationEntry)).toEqual({
			institution: '',
			area: ''
		});
		expect(entrySkeleton('ExperienceEntry', byType.ExperienceEntry)).toEqual({
			company: '',
			position: ''
		});
		expect(entrySkeleton('PublicationEntry', byType.PublicationEntry)).toEqual({
			title: '',
			authors: []
		});
	});

	it('a freshly-inferred skeleton round-trips back through inferEntryType', () => {
		for (const type of ENTRY_TYPES) {
			const descriptors = getEntryTypeDescriptors(schema);
			const fields = descriptors.find((d) => d.type === type)?.fields ?? [];
			const skeleton = entrySkeleton(type, fields);
			expect(inferEntryType(skeleton)).toBe(type);
		}
	});
});

describe('entrySummaryText', () => {
	it('reads the identifying field for each entry type', () => {
		expect(entrySummaryText('EducationEntry', { institution: 'MIT' })).toBe('MIT');
		expect(entrySummaryText('ExperienceEntry', { company: 'Acme' })).toBe('Acme');
		expect(entrySummaryText('NormalEntry', { name: 'Side Project' })).toBe('Side Project');
		expect(entrySummaryText('PublicationEntry', { title: 'A Paper' })).toBe('A Paper');
		expect(entrySummaryText('OneLineEntry', { label: 'Languages' })).toBe('Languages');
	});

	it('uses the bare string value for TextEntry', () => {
		expect(entrySummaryText('TextEntry', 'A line of text')).toBe('A line of text');
	});

	it('falls back to a placeholder when the identifying field is empty', () => {
		expect(entrySummaryText('EducationEntry', { institution: '' })).toBe('Untitled entry');
		expect(entrySummaryText('EducationEntry', {})).toBe('Untitled entry');
		expect(entrySummaryText('TextEntry', '')).toBe('Empty entry');
		expect(entrySummaryText('TextEntry', '   ')).toBe('Empty entry');
	});
});

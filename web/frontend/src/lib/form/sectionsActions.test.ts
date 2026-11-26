import { describe, it, expect } from 'vitest';
import {
	buildAddEntryOp,
	buildAddHighlightOp,
	buildAddSectionOp,
	buildDeleteEntryOp,
	buildDeleteHighlightOp,
	buildDeleteSectionOp,
	buildMoveEntryOp,
	buildMoveHighlightOp,
	buildRenameSectionOp,
	buildSetEntryFieldOp,
	buildSetHighlightOp
} from './sectionsActions';
import { getEntryTypeDescriptors } from '$lib/schema/cvSchema';
import type { JsonSchemaDocument } from '$lib/schema/types';
import schemaFixture from '$lib/schema/fixtures/schema.snapshot.json';

const schema = schemaFixture as unknown as JsonSchemaDocument;
const entryDescriptors = getEntryTypeDescriptors(schema);
const fieldsFor = (type: string) => entryDescriptors.find((d) => d.type === type)?.fields ?? [];

describe('section-level ops', () => {
	it('add section: set on the new title with an empty list', () => {
		expect(buildAddSectionOp('Experience')).toEqual({
			op: 'set',
			path: ['cv', 'sections', 'Experience'],
			value: []
		});
	});

	it('delete section: delete on the title', () => {
		expect(buildDeleteSectionOp('Experience')).toEqual({
			op: 'delete',
			path: ['cv', 'sections', 'Experience']
		});
	});

	it('rename section: rebuilds the whole sections mapping, preserving order and entries', () => {
		const sections = {
			Education: [{ institution: 'MIT', area: 'CS' }],
			Experience: [{ company: 'Acme', position: 'Eng' }]
		};
		const op = buildRenameSectionOp(sections, 'Education', 'Academics');
		expect(op).toEqual({
			op: 'set',
			path: ['cv', 'sections'],
			value: {
				Academics: [{ institution: 'MIT', area: 'CS' }],
				Experience: [{ company: 'Acme', position: 'Eng' }]
			}
		});
	});
});

describe('entry-level ops', () => {
	it('add entry: insert at the end with the type skeleton from the schema', () => {
		const op = buildAddEntryOp('Education', 1, 'EducationEntry', fieldsFor('EducationEntry'));
		expect(op).toEqual({
			op: 'insert',
			path: ['cv', 'sections', 'Education'],
			index: 1,
			value: { institution: '', area: '' }
		});
	});

	it('add a TextEntry: skeleton is an empty string', () => {
		const op = buildAddEntryOp('Notes', 0, 'TextEntry', []);
		expect(op).toEqual({ op: 'insert', path: ['cv', 'sections', 'Notes'], index: 0, value: '' });
	});

	it('delete entry: delete by index', () => {
		expect(buildDeleteEntryOp('Education', 2)).toEqual({
			op: 'delete',
			path: ['cv', 'sections', 'Education', 2]
		});
	});

	it('reorder entries: move within the section array', () => {
		expect(buildMoveEntryOp('Education', 0, 2)).toEqual({
			op: 'move',
			path: ['cv', 'sections', 'Education'],
			from_index: 0,
			to_index: 2
		});
	});

	it('editing an entry field: set on that field path', () => {
		expect(buildSetEntryFieldOp('Education', 0, 'degree', 'PhD')).toEqual({
			op: 'set',
			path: ['cv', 'sections', 'Education', 0, 'degree'],
			value: 'PhD'
		});
	});
});

describe('highlight ops', () => {
	it('add highlight: insert at the end of that entry highlights array', () => {
		expect(buildAddHighlightOp('Education', 0, 2)).toEqual({
			op: 'insert',
			path: ['cv', 'sections', 'Education', 0, 'highlights'],
			index: 2,
			value: ''
		});
	});

	it('delete highlight: delete by index within the entry', () => {
		expect(buildDeleteHighlightOp('Education', 0, 1)).toEqual({
			op: 'delete',
			path: ['cv', 'sections', 'Education', 0, 'highlights', 1]
		});
	});

	it('reorder highlights: move within the entry highlights array', () => {
		expect(buildMoveHighlightOp('Education', 0, 2, 0)).toEqual({
			op: 'move',
			path: ['cv', 'sections', 'Education', 0, 'highlights'],
			from_index: 2,
			to_index: 0
		});
	});

	it('editing a highlight: set on that highlight index', () => {
		expect(buildSetHighlightOp('Education', 0, 1, 'Edited text')).toEqual({
			op: 'set',
			path: ['cv', 'sections', 'Education', 0, 'highlights', 1],
			value: 'Edited text'
		});
	});
});

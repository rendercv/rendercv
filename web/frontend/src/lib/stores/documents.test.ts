import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { documents, setDocument, resetDocuments, createDefaultDocuments } from './documents';

describe('documents store', () => {
	beforeEach(() => {
		resetDocuments();
	});

	it('starts with the default CV and settings content', () => {
		const docs = get(documents);
		expect(docs.cv).toBe('cv:\n  name: John Doe\n  sections: {}\n');
		expect(docs.settings).toBe('settings:\n  pdf_title: NAME - CV\n');
		expect(docs.design).toBe('');
		expect(docs.locale).toBe('');
	});

	it('updates a single document without touching the others', () => {
		const before = get(documents);

		setDocument('cv', 'cv:\n  name: Jane Doe\n');

		const after = get(documents);
		expect(after.cv).toBe('cv:\n  name: Jane Doe\n');
		expect(after.design).toBe(before.design);
		expect(after.locale).toBe(before.locale);
		expect(after.settings).toBe(before.settings);
	});

	it('reset restores the defaults after edits', () => {
		setDocument('cv', 'cv:\n  name: Someone Else\n');
		setDocument('design', 'design:\n  theme: sb2nov\n');

		resetDocuments();

		expect(get(documents)).toEqual(createDefaultDocuments());
	});
});

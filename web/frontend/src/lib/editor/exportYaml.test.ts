import { describe, it, expect } from 'vitest';
import { buildRendercvYaml, splitRendercvYaml } from './exportYaml';
import type { CvDocuments } from '$lib/stores/documents';

function docs(overrides: Partial<CvDocuments> = {}): CvDocuments {
	return {
		cv: 'cv:\n  name: John Doe\n  sections: {}\n',
		design: 'design:\n  theme: classic\n',
		locale: 'locale:\n  language: en\n',
		settings: 'settings:\n  pdf_title: NAME - CV\n',
		...overrides
	};
}

describe('buildRendercvYaml', () => {
	it('joins the four documents in the order RenderCV expects', () => {
		const yaml = buildRendercvYaml(docs());

		expect(yaml).toBe(
			'cv:\n  name: John Doe\n  sections: {}\n' +
				'\n' +
				'design:\n  theme: classic\n' +
				'\n' +
				'locale:\n  language: en\n' +
				'\n' +
				'settings:\n  pdf_title: NAME - CV\n'
		);
	});

	it('leaves the user text alone rather than reformatting it', () => {
		// The point of concatenating rather than parsing and re-serialising:
		// comments and key order are the user's, and a round trip through a
		// YAML library would quietly rewrite both.
		const commented =
			'# my notes\ncv:\n  name: John Doe # trailing note\n  sections: {}\n';

		const yaml = buildRendercvYaml(docs({ cv: commented, design: '', locale: '', settings: '' }));

		expect(yaml).toContain('# my notes');
		expect(yaml).toContain('# trailing note');
	});

	it('drops empty documents instead of emitting bare keys', () => {
		// `design`, `locale` and `settings` are optional, and to RenderCV an
		// empty `design:` is not the same as an absent one.
		const yaml = buildRendercvYaml(docs({ design: '', locale: '   \n', settings: '' }));

		expect(yaml).toBe('cv:\n  name: John Doe\n  sections: {}\n');
	});

	it('ends with exactly one newline', () => {
		const yaml = buildRendercvYaml(docs());

		expect(yaml.endsWith('\n')).toBe(true);
		expect(yaml.endsWith('\n\n')).toBe(false);
	});

	it('returns the empty string when there is nothing to export', () => {
		const yaml = buildRendercvYaml(docs({ cv: '', design: '', locale: '', settings: '' }));

		expect(yaml).toBe('');
	});
});

describe('splitRendercvYaml', () => {
	it('is the inverse of buildRendercvYaml', () => {
		// The property that matters: a file this app exported must come back
		// in as the documents that produced it. Export and import are the two
		// halves of one promise -- take your work out, put it back.
		const original = docs();

		const outcome = splitRendercvYaml(buildRendercvYaml(original));

		expect(outcome).toEqual({ ok: true, documents: original });
	});

	it('keeps comments and key order exactly as written', () => {
		const file = ['# my notes', 'cv:', '  name: John Doe # trailing', '  sections: {}', ''].join(
			'\n'
		);

		const outcome = splitRendercvYaml(file);

		expect(outcome.ok).toBe(true);
		if (!outcome.ok) return;
		expect(outcome.documents.cv).toBe(
			'# my notes\ncv:\n  name: John Doe # trailing\n  sections: {}\n'
		);
	});

	it('accepts the sections in any order', () => {
		const file = ['settings:', '  pdf_title: X', 'cv:', '  name: A', ''].join('\n');

		const outcome = splitRendercvYaml(file);

		expect(outcome.ok).toBe(true);
		if (!outcome.ok) return;
		expect(outcome.documents.cv).toBe('cv:\n  name: A\n');
		expect(outcome.documents.settings).toBe('settings:\n  pdf_title: X\n');
	});

	it('is not fooled by an indented key that happens to be called cv', () => {
		// Only column zero starts a section. A nested `cv:` is somebody's
		// data, and treating it as a section boundary would tear a document
		// in half.
		const file = ['cv:', '  sections:', '    cv: []', '  name: A', ''].join('\n');

		const outcome = splitRendercvYaml(file);

		expect(outcome.ok).toBe(true);
		if (!outcome.ok) return;
		expect(outcome.documents.cv).toBe('cv:\n  sections:\n    cv: []\n  name: A\n');
	});

	it('leaves absent sections empty rather than inventing them', () => {
		const outcome = splitRendercvYaml('cv:\n  name: A\n');

		expect(outcome.ok).toBe(true);
		if (!outcome.ok) return;
		expect(outcome.documents.design).toBe('');
		expect(outcome.documents.locale).toBe('');
	});

	it('refuses a file with no cv section', () => {
		const outcome = splitRendercvYaml('settings:\n  pdf_title: X\n');

		expect(outcome).toEqual({
			ok: false,
			reason: 'The file has no "cv:" section, so it is not a RenderCV file.'
		});
	});

	it('refuses a section it has nowhere to put, rather than dropping it', () => {
		// Silently discarding it would lose the user's content on an
		// operation they asked for -- the worst way to fail.
		const outcome = splitRendercvYaml('cv:\n  name: A\nrendercv_settings:\n  x: 1\n');

		expect(outcome.ok).toBe(false);
		if (outcome.ok) return;
		expect(outcome.reason).toContain('rendercv_settings');
	});

	it('refuses a duplicated section', () => {
		const outcome = splitRendercvYaml('cv:\n  name: A\ncv:\n  name: B\n');

		expect(outcome.ok).toBe(false);
		if (outcome.ok) return;
		expect(outcome.reason).toContain('more than once');
	});

	it('refuses a file that does not start with a section', () => {
		const outcome = splitRendercvYaml('Nguyen Minh Quan\nData Scientist\n');

		expect(outcome.ok).toBe(false);
		if (outcome.ok) return;
		expect(outcome.reason).toContain('does not start with');
	});

	it('reads a file saved with Windows line endings', () => {
		const outcome = splitRendercvYaml('cv:\r\n  name: A\r\n');

		expect(outcome.ok).toBe(true);
		if (!outcome.ok) return;
		// A stray carriage return would show up as a control character in the
		// editor, and in the YAML the backend is asked to parse.
		expect(outcome.documents.cv).toBe('cv:\n  name: A\n');
	});
});

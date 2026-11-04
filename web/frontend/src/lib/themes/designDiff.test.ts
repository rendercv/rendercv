import { describe, it, expect } from 'vitest';
import { designOverrides } from './designDiff';

const harvardDefaults = {
	theme: 'harvard',
	page: { size: 'us-letter', top_margin: '0.5in' },
	header: {
		connections: {
			show_icons: false,
			display_urls_instead_of_usernames: false,
			separator: '•'
		}
	},
	sections: { show_time_spans_in: [] as string[] }
};

describe('designOverrides', () => {
	it('finds nothing when the document is the theme defaults', () => {
		expect(designOverrides(structuredClone(harvardDefaults), harvardDefaults)).toEqual([]);
	});

	it('names the stale connection options that made Harvard look broken', () => {
		// The case that prompted this: a Harvard CV carrying `' | '` and
		// full URLs from somewhere else, rendering nothing like Harvard.
		const design = structuredClone(harvardDefaults);
		design.header.connections.separator = ' | ';
		design.header.connections.display_urls_instead_of_usernames = true;

		expect(designOverrides(design, harvardDefaults)).toEqual([
			'header.connections.display_urls_instead_of_usernames',
			'header.connections.separator'
		]);
	});

	it('ignores keys the document leaves out, since those already follow the theme', () => {
		expect(designOverrides({ theme: 'harvard', page: { size: 'us-letter' } }, harvardDefaults)).toEqual(
			[]
		);
	});

	it('never lists the theme name itself', () => {
		expect(designOverrides({ theme: 'classic' }, harvardDefaults)).toEqual([]);
	});

	it('compares lists by content, not identity', () => {
		const design = { sections: { show_time_spans_in: ['Experience'] } };
		expect(designOverrides(design, harvardDefaults)).toEqual(['sections.show_time_spans_in']);
		expect(designOverrides({ sections: { show_time_spans_in: [] } }, harvardDefaults)).toEqual([]);
	});

	it('flags a key the theme does not have at all', () => {
		expect(designOverrides({ page: { not_an_option: 1 } }, harvardDefaults)).toEqual([
			'page.not_an_option'
		]);
	});

	it('treats a document that is not a mapping yet as nothing to compare', () => {
		// Mid-edit YAML can parse to null or a bare string; the indicator
		// should go quiet rather than throw.
		expect(designOverrides(null, harvardDefaults)).toEqual([]);
		expect(designOverrides('design', harvardDefaults)).toEqual([]);
	});
});

import { describe, it, expect } from 'vitest';
import { getVariantFields, listVariantNames, resolveVariantDefName } from './discriminatedUnion';
import type { JsonSchemaDocument } from './types';
import schemaFixture from './fixtures/schema.snapshot.json';

// The fixture is a snapshot of the repository's real `schema.json` (as
// served by the live `GET /api/schema`), copied in for deterministic tests
// per the ui-implementation skill's testing guidance.
const schema = schemaFixture as unknown as JsonSchemaDocument;

const EXPECTED_THEMES: Record<string, string> = {
	classic: 'ClassicTheme',
	ember: 'EmberTheme',
	engineeringclassic: 'EngineeringclassicTheme',
	engineeringresumes: 'EngineeringresumesTheme',
	harvard: 'HarvardTheme',
	ink: 'InkTheme',
	moderncv: 'ModerncvTheme',
	opal: 'OpalTheme',
	sb2nov: 'Sb2novTheme'
};

describe('discriminatedUnion against the real schema', () => {
	it('lists all 9 built-in themes for the design union, in schema order', () => {
		expect(listVariantNames(schema, 'BuiltInDesign')).toEqual(Object.keys(EXPECTED_THEMES));
	});

	it.each(Object.entries(EXPECTED_THEMES))(
		'resolves theme "%s" to its variant def name "%s"',
		(themeName, defName) => {
			expect(resolveVariantDefName(schema, 'BuiltInDesign', themeName)).toBe(defName);
		}
	);

	it.each(Object.keys(EXPECTED_THEMES))(
		'resolves non-empty field descriptors for theme "%s", excluding the discriminator key',
		(themeName) => {
			const fields = getVariantFields(schema, 'BuiltInDesign', themeName, ['theme']);
			expect(fields.length).toBeGreaterThan(0);
			expect(fields.some((f) => f.key === 'theme')).toBe(false);

			// Every built-in theme follows the same top-level grouping (see the
			// phase task: "PAGE, COLORS, TEXT, LINKS, HEADER, ...").
			const keys = fields.map((f) => f.key);
			expect(keys).toContain('page');
			expect(keys).toContain('colors');
		}
	);

	it('resolves the Page group with the expected leaf kinds (enum page size, dimension margins, boolean toggles)', () => {
		const fields = getVariantFields(schema, 'BuiltInDesign', 'classic', ['theme']);
		const page = fields.find((f) => f.key === 'page');
		expect(page?.kind).toBe('object');

		const byKey = Object.fromEntries((page?.fields ?? []).map((f) => [f.key, f]));
		expect(byKey.size.kind).toBe('enum');
		expect(byKey.top_margin.kind).toBe('dimension');
		expect(byKey.show_footer.kind).toBe('boolean');
	});

	it('resolves the Colors group with color-kind leaves', () => {
		const fields = getVariantFields(schema, 'BuiltInDesign', 'classic', ['theme']);
		const colors = fields.find((f) => f.key === 'colors');
		const body = colors?.fields?.find((f) => f.key === 'body');
		expect(body?.kind).toBe('color');
		expect(body?.default).toBe('rgb(0, 0, 0)');
	});

	it('lists all 22 locale languages and resolves the English variant fields with defaults', () => {
		const languages = listVariantNames(schema, 'Locale');
		expect(languages).toContain('english');
		expect(languages.length).toBe(22);

		const fields = getVariantFields(schema, 'Locale', 'english', ['language']);
		const byKey = Object.fromEntries(fields.map((f) => [f.key, f]));
		expect(byKey.month.default).toBe('month');
		expect(byKey.month_names.default).toEqual([
			'January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December'
		]);
	});

	it('throws for an unknown variant name', () => {
		expect(() => resolveVariantDefName(schema, 'BuiltInDesign', 'not-a-theme')).toThrow();
	});
});

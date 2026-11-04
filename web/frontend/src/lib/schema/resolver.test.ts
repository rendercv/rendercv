import { describe, it, expect } from 'vitest';
import { resolveDefFields, resolveObjectFields, deref } from './resolver';
import type { JsonSchemaDocument } from './types';
import schemaFixture from './fixtures/schema.snapshot.json';

// The fixture is a snapshot of the repository's real `schema.json` (as
// served by the live `GET /api/schema`), copied in for deterministic tests
// per the ui-implementation skill's testing guidance.
const schema = schemaFixture as unknown as JsonSchemaDocument;

describe('resolveDefFields against the real schema', () => {
	it('resolves the Cv object into field descriptors with labels and placeholders', () => {
		const fields = resolveDefFields(schema, 'Cv');
		const byKey = Object.fromEntries(fields.map((f) => [f.key, f]));

		expect(byKey.name.kind).toBe('string');
		expect(byKey.name.label).toBe('Name');
		expect(byKey.name.placeholder).toBe('John Doe');
		expect(byKey.name.required).toBe(false);
		expect(byKey.name.nullable).toBe(true);

		expect(byKey.sections).toBeDefined();
	});

	it('resolves nested $ref object arrays (social_networks -> SocialNetwork[])', () => {
		const fields = resolveDefFields(schema, 'Cv');
		const socialNetworks = fields.find((f) => f.key === 'social_networks');
		expect(socialNetworks?.kind).toBe('array');
		expect(socialNetworks?.items?.kind).toBe('object');

		const networkField = socialNetworks?.items?.fields?.find((f) => f.key === 'network');
		expect(networkField?.kind).toBe('enum');
		expect(networkField?.enumValues).toContain('LinkedIn');

		const usernameField = socialNetworks?.items?.fields?.find((f) => f.key === 'username');
		expect(usernameField?.kind).toBe('string');
		expect(usernameField?.required).toBe(true);
	});

	it('resolves EducationEntry with required fields and a date $ref', () => {
		const fields = resolveDefFields(schema, 'EducationEntry');
		const byKey = Object.fromEntries(fields.map((f) => [f.key, f]));

		expect(byKey.institution.required).toBe(true);
		expect(byKey.area.required).toBe(true);
		expect(byKey.degree.required).toBe(false);
		expect(byKey.start_date.kind).toBe('date');
		expect(byKey.highlights.kind).toBe('array');
		expect(byKey.highlights.items?.kind).toBe('markdown');
	});

	it('surfaces a multi-format example placeholder for date/start_date/end_date fields', () => {
		const fields = resolveDefFields(schema, 'EducationEntry');
		const byKey = Object.fromEntries(fields.map((f) => [f.key, f]));

		// Each placeholder shows more than just the first schema example, and
		// (schema depending) is truncated with an "etc." rather than silently
		// dropping the remaining formats.
		expect(byKey.date.placeholder).toContain(', ');
		expect(byKey.date.placeholder).toMatch(/2020-09-24/);
		expect(byKey.start_date.placeholder).toContain(', ');
		expect(byKey.end_date.placeholder).toContain(', ');
	});

	it('resolves PublicationEntry: a required string array (authors) and a url field', () => {
		const fields = resolveDefFields(schema, 'PublicationEntry');
		const byKey = Object.fromEntries(fields.map((f) => [f.key, f]));

		expect(byKey.authors.kind).toBe('array');
		expect(byKey.authors.required).toBe(true);
		expect(byKey.url.kind).toBe('url');
	});

	it('resolves BulletEntry / NumberedEntry / ReversedNumberedEntry / OneLineEntry as single/two-field objects', () => {
		const bullet = resolveDefFields(schema, 'BulletEntry');
		expect(bullet.map((f) => f.key)).toEqual(['bullet']);
		expect(bullet[0].required).toBe(true);

		const numbered = resolveDefFields(schema, 'NumberedEntry');
		expect(numbered.map((f) => f.key)).toEqual(['number']);

		const reversedNumbered = resolveDefFields(schema, 'ReversedNumberedEntry');
		expect(reversedNumbered.map((f) => f.key)).toEqual(['reversed_number']);

		const oneLine = resolveDefFields(schema, 'OneLineEntry');
		expect(oneLine.map((f) => f.key).sort()).toEqual(['details', 'label']);
		expect(oneLine.every((f) => f.required)).toBe(true);
	});

	it('deref follows a $ref to its target node', () => {
		const node = schema.$defs.Section;
		const resolved = deref(schema.$defs, node);
		expect(resolved.anyOf).toBeDefined();
	});

	it('resolveObjectFields returns [] for an object with no properties', () => {
		expect(resolveObjectFields(schema.$defs, {})).toEqual([]);
	});
});

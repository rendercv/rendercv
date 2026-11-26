import { deref, resolveObjectFields } from './resolver';
import type { FieldDescriptor, JsonSchemaDocument } from './types';

/**
 * Resolves the pydantic discriminated-union variants the schema uses for
 * `design` (9 built-in themes, discriminated on `theme`) and `locale` (22
 * languages, discriminated on `language`) — both are `oneOf` unions with a
 * `discriminator.mapping` from the discriminator's literal value straight to
 * the variant's `$defs` entry, so one resolver serves both instead of
 * hand-coding a per-theme or per-language field list.
 */

/** All discriminator values (theme names / language names) a union def declares, in schema declaration order. */
export function listVariantNames(schema: JsonSchemaDocument, unionDefName: string): string[] {
	const node = schema.$defs[unionDefName];
	const mapping = node?.discriminator?.mapping;
	if (!mapping) throw new Error(`"${unionDefName}" has no discriminator mapping.`);
	return Object.keys(mapping);
}

/** The `$defs` entry name for one variant (e.g. `"classic"` -> `"ClassicTheme"`). */
export function resolveVariantDefName(
	schema: JsonSchemaDocument,
	unionDefName: string,
	discriminatorValue: string
): string {
	const node = schema.$defs[unionDefName];
	const mapping = node?.discriminator?.mapping;
	const ref = mapping?.[discriminatorValue];
	if (!ref) {
		throw new Error(`Unknown variant "${discriminatorValue}" for "${unionDefName}".`);
	}
	return ref.replace('#/$defs/', '');
}

/**
 * Resolves one variant's field descriptors, excluding the discriminator key
 * itself (`theme` / `language`) — the caller renders that separately (a
 * dedicated switcher), not as a generic form row.
 */
export function getVariantFields(
	schema: JsonSchemaDocument,
	unionDefName: string,
	discriminatorValue: string,
	excludeKeys: string[] = []
): FieldDescriptor[] {
	const defName = resolveVariantDefName(schema, unionDefName, discriminatorValue);
	const node = schema.$defs[defName];
	if (!node) throw new Error(`Unknown $defs entry "${defName}".`);
	return resolveObjectFields(schema.$defs, deref(schema.$defs, node)).filter(
		(field) => !excludeKeys.includes(field.key)
	);
}

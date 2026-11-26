/**
 * Typed shape the form generator builds from `/api/schema` (JSON Schema
 * Draft-07 of the whole rendercv pydantic model tree).
 *
 * Why: the form must never hand-code a field list that duplicates the
 * pydantic models (see the ui-implementation skill) — every control the
 * form renders is described by one of these descriptors, resolved from the
 * schema's `$defs`/`$ref`/`anyOf` shapes.
 */

/** The raw JSON Schema Draft-07 shape (loosely typed; we only read fields we use). */
export interface JsonSchemaNode {
	$ref?: string;
	type?: string | string[];
	title?: string;
	description?: string | null;
	examples?: unknown[];
	enum?: unknown[];
	const?: unknown;
	default?: unknown;
	format?: string;
	pattern?: string;
	anyOf?: JsonSchemaNode[];
	oneOf?: JsonSchemaNode[];
	items?: JsonSchemaNode;
	properties?: Record<string, JsonSchemaNode>;
	required?: string[];
	additionalProperties?: JsonSchemaNode | boolean;
	/**
	 * Pydantic's discriminated-union marker (e.g. `BuiltInDesign`'s 9 theme
	 * variants, `Locale`'s 22 language variants): maps the discriminator
	 * field's value to the `$defs` entry for that variant.
	 */
	discriminator?: { propertyName: string; mapping: Record<string, string> };
}

export interface JsonSchemaDocument {
	$defs: Record<string, JsonSchemaNode>;
	properties: Record<string, JsonSchemaNode>;
	[key: string]: unknown;
}

/**
 * The kinds of controls the form knows how to render.
 *
 * `markdown` is a multiline string field whose content is passed through the
 * same markdown-to-typst pipeline as the core (e.g. `summary`, `highlights`
 * items, `bullet`) — detected heuristically (see `resolver.ts`), since the
 * JSON Schema itself has no "this is markdown" marker.
 */
export type FieldKind =
	| 'string'
	| 'markdown'
	| 'date'
	| 'url'
	| 'color'
	| 'dimension'
	| 'enum'
	| 'boolean'
	| 'number'
	| 'array'
	| 'object'
	| 'unknown';

export interface FieldDescriptor {
	/** The property key this field is stored under in its parent object. */
	key: string;
	/** Human label, from the schema's `title` (falls back to a titleized key). */
	label: string;
	description?: string;
	/** First example value, used as the input's placeholder (reference UX: placeholders are examples). */
	placeholder?: string;
	required: boolean;
	/** True if the resolved type admits `null` (an `anyOf` branch with `type: null`). */
	nullable: boolean;
	kind: FieldKind;
	/**
	 * The schema's own `default` for this field, if it declares one (most
	 * design/locale leaf fields do). Used for the effective-value overlay:
	 * a field with no explicit override displays this value.
	 */
	default?: unknown;
	/** Only for `kind: 'enum'`. */
	enumValues?: string[];
	/** Only for `kind: 'array'`: the descriptor for one item. */
	items?: FieldDescriptor;
	/** Only for `kind: 'object'`: the resolved child fields. */
	fields?: FieldDescriptor[];
}

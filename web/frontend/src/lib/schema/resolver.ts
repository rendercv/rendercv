import type { FieldDescriptor, FieldKind, JsonSchemaDocument, JsonSchemaNode } from './types';

/** Resolves a `#/$defs/Name` ref against the document's `$defs`. */
export function resolveRef(defs: Record<string, JsonSchemaNode>, ref: string): JsonSchemaNode {
	const name = ref.replace('#/$defs/', '');
	const target = defs[name];
	if (!target) throw new Error(`Unknown $ref "${ref}" (no $defs entry for "${name}")`);
	return target;
}

/** Follows `$ref` until it reaches a node that isn't itself just a `$ref`. */
export function deref(defs: Record<string, JsonSchemaNode>, node: JsonSchemaNode): JsonSchemaNode {
	let current = node;
	// Bounded by $defs size; schema.json has no cyclic $refs at the field level.
	for (let i = 0; i < 50 && current.$ref; i++) {
		current = resolveRef(defs, current.$ref);
	}
	return current;
}

/**
 * Unwraps a nullable union (`anyOf: [X, {type: "null"}]`, however many
 * non-null branches there are) into the "primary" branch plus a flag.
 *
 * Why picking the first non-null branch: rendercv's optional fields are
 * `X | None` unions (one real branch) or `X | Y | None` where the extra
 * branches are alternate literal spellings of the same field (e.g.
 * `end_date: ExactDate | Literal["present"] | None`) — the primary branch's
 * shape is enough to pick a control kind; the literal alternatives remain
 * valid free-text input since the control is a plain text box.
 */
export function unwrapNullable(node: JsonSchemaNode): { inner: JsonSchemaNode; nullable: boolean } {
	const branches = node.anyOf ?? node.oneOf;
	if (!branches || branches.length === 0) return { inner: node, nullable: false };

	const nullable = branches.some((b) => b.type === 'null');
	const nonNull = branches.filter((b) => b.type !== 'null');
	if (nonNull.length === 0) return { inner: node, nullable };
	return { inner: nonNull[0], nullable };
}

const DATE_REFS = new Set(['#/$defs/ExactDate', '#/$defs/ArbitraryDate']);

/** `$ref`s that resolve to a bare `string` type but represent a typst dimension (e.g. `"0.7in"`). */
const DIMENSION_REFS = new Set(['#/$defs/TypstDimension']);

/** Field-name heuristics for the "this optional-string is really markdown" detection. */
const MARKDOWN_KEYS = new Set([
	'summary',
	'highlights',
	'bullet',
	'number',
	'reversed_number',
	'details',
	'label'
]);

function kindForLeaf(
	defs: Record<string, JsonSchemaNode>,
	key: string,
	node: JsonSchemaNode
): FieldKind {
	if (node.$ref && DATE_REFS.has(node.$ref)) return 'date';
	if (node.$ref && DIMENSION_REFS.has(node.$ref)) return 'dimension';
	if (node.enum) return 'enum';
	if (node.format === 'uri') return 'url';
	if (node.format === 'color') return 'color';

	const resolved = deref(defs, node);
	if (resolved.format === 'color') return 'color';
	if (resolved.enum) return 'enum';
	if (resolved.type === 'boolean') return 'boolean';
	if (resolved.type === 'integer' || resolved.type === 'number') return 'number';
	if (resolved.type === 'object' || resolved.properties) return 'object';
	if (resolved.type === 'array' || resolved.items) return 'array';

	// Fallback: a handful of Cv contact fields (email/phone/website) accept
	// either a single value or a list (`str | list[str] | None`), which
	// pydantic emits as a schema with no `type`/`anyOf` at all. Rendering
	// them as a plain string field is a safe default (the single-value case
	// is by far the common one); see the resolver's test file for the known
	// limitation this leaves (no dedicated multi-value control yet).
	return MARKDOWN_KEYS.has(key) || (resolved.description ?? '').toLowerCase().includes('markdown')
		? 'markdown'
		: 'string';
}

function titleize(key: string): string {
	return key
		.split('_')
		.map((word) => (word.length > 0 ? word[0].toUpperCase() + word.slice(1) : word))
		.join(' ');
}

function firstExample(node: JsonSchemaNode): string | undefined {
	const example = node.examples?.[0];
	if (typeof example === 'string') return example;
	if (typeof example === 'number') return String(example);
	return undefined;
}

const MAX_DATE_EXAMPLES = 3;

/**
 * Builds a multi-format placeholder for a `date`/`start_date`/`end_date`
 * field, e.g. "2020-09-24, 2020-09, 2020, etc." Why not just
 * {@link firstExample}: a date field accepts several distinct spellings
 * (`ExactDate`'s YYYY[-MM[-DD]] forms, `ArbitraryDate`'s free text like "Fall
 * 2023", `end_date`'s literal "present") and the schema's own `examples`
 * list enumerates them -- showing only the first flattens that into a single
 * format, which is exactly the placeholder regression this fixes.
 */
function dateExamples(node: JsonSchemaNode, resolved: JsonSchemaNode): string | undefined {
	const examples = (node.examples ?? resolved.examples ?? [])
		.filter((e) => typeof e === 'string' || typeof e === 'number')
		.map((e) => String(e));
	if (examples.length === 0) return undefined;

	const shown = examples.slice(0, MAX_DATE_EXAMPLES);
	return examples.length > shown.length ? `${shown.join(', ')}, etc.` : shown.join(', ');
}

/**
 * Resolves one property's schema node into a {@link FieldDescriptor}.
 *
 * @param defs The document's `$defs` map (for following `$ref`s).
 * @param key The property name in its parent object.
 * @param node The raw (un-dereffed) schema node for this property.
 * @param requiredKeys The parent object's `required` list.
 */
export function resolveField(
	defs: Record<string, JsonSchemaNode>,
	key: string,
	node: JsonSchemaNode,
	requiredKeys: string[] = []
): FieldDescriptor {
	const { inner, nullable } = unwrapNullable(node);
	const resolved = deref(defs, inner);
	const kind = kindForLeaf(defs, key, inner);

	const descriptor: FieldDescriptor = {
		key,
		label: node.title ?? resolved.title ?? titleize(key),
		description: node.description ?? resolved.description ?? undefined,
		placeholder:
			kind === 'date'
				? (dateExamples(node, resolved) ?? firstExample(node) ?? firstExample(resolved))
				: (firstExample(node) ?? firstExample(resolved)),
		required: requiredKeys.includes(key),
		nullable,
		kind,
		default: node.default ?? resolved.default
	};

	if (kind === 'enum') {
		descriptor.enumValues = (resolved.enum ?? []).map((v) => String(v));
	}

	if (kind === 'array') {
		const itemsNode = resolved.items ?? {};
		descriptor.items = resolveField(defs, key, itemsNode, []);
	}

	if (kind === 'object') {
		descriptor.fields = resolveObjectFields(defs, resolved);
	}

	return descriptor;
}

/** Resolves every property of an (already dereffed) object schema node into descriptors, in declaration order. */
export function resolveObjectFields(
	defs: Record<string, JsonSchemaNode>,
	objectNode: JsonSchemaNode
): FieldDescriptor[] {
	const properties = objectNode.properties ?? {};
	const required = objectNode.required ?? [];
	return Object.entries(properties).map(([key, node]) => resolveField(defs, key, node, required));
}

/** Resolves a named `$defs` entry (e.g. `"Cv"`, `"EducationEntry"`) straight to its field descriptors. */
export function resolveDefFields(
	schema: JsonSchemaDocument,
	defName: string
): FieldDescriptor[] {
	const node = schema.$defs[defName];
	if (!node) throw new Error(`Unknown $defs entry "${defName}"`);
	return resolveObjectFields(schema.$defs, deref(schema.$defs, node));
}

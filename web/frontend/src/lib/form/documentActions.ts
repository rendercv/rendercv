import { getAtPath, type PatchOp, type PathSegment } from './patchOps';

/**
 * Generic patch-op builders for the design/locale/settings forms — the
 * counterpart to `cvFieldActions.ts`'s CV-specific `buildSetCvFieldOp`, but
 * parameterized by document top-key since these three tabs all follow the
 * same shape (a single top-level mapping, no dedicated sub-editor like
 * `cv.sections`).
 */

/** Sets `<topKey>.<...path>` to a whole new value (path relative to the document's top key). */
export function buildSetFieldOp(topKey: string, path: PathSegment[], value: unknown): PatchOp {
	return { op: 'set', path: [topKey, ...path], value };
}

/**
 * Deletes an explicit override at `<topKey>.<...path>` — the "reset to
 * default" affordance: the effective value then falls back to whatever the
 * defaults overlay provides for that field.
 */
export function buildResetFieldOp(topKey: string, path: PathSegment[]): PatchOp {
	return { op: 'delete', path: [topKey, ...path] };
}

/**
 * Switches a document's discriminator field (`design.theme` / `locale.language`)
 * to `newValue`.
 *
 * Why branch on blank: the patch contract requires every path element
 * before the last to already exist (`resolve_parent_and_key` in the
 * backend's `documents.py`) — a document that's never been touched has no
 * `design:`/`locale:` mapping at all yet, so the first write must create it
 * (a `set` at the top key with a fresh `{<discriminatorKey>: newValue}`
 * mapping) rather than assume `["<topKey>", "<discriminatorKey>"]` resolves.
 */
export function buildDiscriminatorSwitchOp(
	currentYaml: string,
	topKey: string,
	discriminatorKey: string,
	newValue: string
): PatchOp {
	if (currentYaml.trim() === '') {
		return { op: 'set', path: [topKey], value: { [discriminatorKey]: newValue } };
	}
	return { op: 'set', path: [topKey, discriminatorKey], value: newValue };
}

/**
 * Builds the `set` ops needed to create any missing intermediate container
 * along `path` before the leaf itself can be set — one op per ancestor
 * prefix that doesn't exist yet in `tree`, shallowest first, each creating
 * an empty mapping (or, for the top-key itself, `topKeySeed` if given).
 *
 * Why this is needed at every nesting depth, not just the top key: the
 * patch contract requires every path segment before the last to already
 * exist (`resolve_parent_and_key` in the backend's `documents.py`). The
 * design/locale forms' effective-value overlay means a field several
 * levels deep (e.g. `design.page.top_margin`) can be the very first write
 * to an otherwise-untouched document -- `design` doesn't exist yet, and
 * neither does `design.page`. Prepending one `set` per missing ancestor
 * (applied in order, in the same atomic patch request) creates exactly the
 * scaffolding the final leaf `set` needs, without ever overwriting an
 * ancestor that already has other content.
 *
 * Why `topKeySeed`: `design`/`locale` are pydantic discriminated unions on
 * `theme`/`language` -- a document missing that field entirely fails to
 * resolve which variant to validate against (the core can't even produce a
 * user-friendly error for `design`'s case; it's an unhandled 500). Every
 * write that creates the top key from scratch must seed it with the
 * current discriminator value already set, e.g. `{ theme: "classic" }`,
 * matching the approved "YAML stays minimal, but `theme` is always present
 * once anything is set" semantics.
 */
export function buildEnsurePathOps(
	tree: unknown,
	path: PathSegment[],
	topKeySeed?: Record<string, unknown>
): PatchOp[] {
	const ops: PatchOp[] = [];
	for (let i = 1; i < path.length; i++) {
		const prefix = path.slice(0, i);
		if (getAtPath(tree, prefix) === undefined) {
			const value = prefix.length === 1 && topKeySeed ? topKeySeed : {};
			ops.push({ op: 'set', path: prefix, value });
		}
	}
	return ops;
}

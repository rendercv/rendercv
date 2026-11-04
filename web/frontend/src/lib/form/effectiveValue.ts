import { getAtPath, type PathSegment } from './patchOps';

/**
 * Threaded down through `DynamicField` -> `ObjectFieldset`/`ArrayField` ->
 * `FieldRow` so every leaf can ask "is this path explicitly set?" and emit
 * "reset this path" without each layer needing its own copy of the override
 * tree.
 */
export interface OverrideInfo {
	/** Is `path` (absolute, document-top-key included) explicitly set in the current YAML? */
	isOverridden: (path: PathSegment[]) => boolean;
	/** Deletes the explicit override at `path`, falling back to the defaults overlay. */
	onReset: (path: PathSegment[]) => void;
	/**
	 * Writes an explicit override at `path` directly (a precise per-leaf
	 * `set`, path absolute) — bypasses `DynamicField`'s usual
	 * reconstruct-the-whole-parent-object bubbling, which would otherwise
	 * write every sibling default into the YAML as a spurious override the
	 * moment one nested field changes (violating the "YAML stays minimal"
	 * approved semantics).
	 */
	setPath: (path: PathSegment[], value: unknown) => void;
}

/**
 * The "effective value" overlay (approved semantics, phase 3 task): a
 * design/locale document's YAML stays minimal (just the discriminator plus
 * explicit overrides); the form displays defaults deep-merged with whatever
 * the user explicitly set, so switching themes/languages instantly changes
 * every field the user never touched while explicit overrides survive.
 */

function isPlainObject(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Deep-overlays `override` onto `base`: plain-object keys merge recursively;
 * anything else (arrays, scalars, or a type mismatch) is replaced wholly by
 * `override` when present. `override === undefined` means "nothing to
 * overlay here" and `base` passes through unchanged.
 */
export function deepMerge(base: unknown, override: unknown): unknown {
	if (override === undefined) return base;
	if (isPlainObject(base) && isPlainObject(override)) {
		const merged: Record<string, unknown> = { ...base };
		for (const key of Object.keys(override)) {
			merged[key] = deepMerge(base[key], override[key]);
		}
		return merged;
	}
	return override;
}

/**
 * True if `path` is explicitly present in the (un-merged) override tree —
 * i.e. the user set this exact field, as opposed to it merely inheriting a
 * value from the defaults overlay. Used to decide the muted/emphasized style
 * and whether the "reset to default" affordance shows.
 */
export function isPathOverridden(overrideTree: unknown, path: PathSegment[]): boolean {
	return getAtPath(overrideTree, path) !== undefined;
}

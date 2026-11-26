/**
 * Finds where a design document departs from its theme's defaults.
 *
 * Why: the editor rewrites the whole design block from a theme's defaults
 * when the theme changes, so a value carried in by an import, a paste or an
 * edit made weeks ago keeps overriding the theme silently. A CV named
 * "Harvard" that renders with `|` separators looks like a broken theme; it
 * is really one stale line. Listing the overriding paths lets the editor say
 * so, and offer the reset, before anyone goes hunting for a bug.
 *
 * The comparison is one-sided: only keys the document actually spells out
 * are checked. A key the document leaves out falls back to the theme's
 * default, so it cannot differ from it.
 */

type JsonObject = Record<string, unknown>;

function isPlainObject(value: unknown): value is JsonObject {
	return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function sameValue(left: unknown, right: unknown): boolean {
	if (Array.isArray(left) || Array.isArray(right)) {
		if (!Array.isArray(left) || !Array.isArray(right)) return false;
		if (left.length !== right.length) return false;
		return left.every((item, index) => sameValue(item, right[index]));
	}
	if (isPlainObject(left) && isPlainObject(right)) {
		const leftKeys = Object.keys(left);
		if (leftKeys.length !== Object.keys(right).length) return false;
		return leftKeys.every((key) => key in right && sameValue(left[key], right[key]));
	}
	return left === right;
}

function collectDifferences(
	value: unknown,
	defaults: unknown,
	path: string[],
	out: string[]
): void {
	if (isPlainObject(value) && isPlainObject(defaults)) {
		for (const [key, child] of Object.entries(value)) {
			collectDifferences(child, defaults[key], [...path, key], out);
		}
		return;
	}
	if (!sameValue(value, defaults)) out.push(path.join('.'));
}

/**
 * Lists the dotted paths where `design` overrides `defaults`.
 *
 * Args:
 *   design: The parsed `design:` mapping from the document, or anything
 *     else (missing, a scalar) while the document is mid-edit.
 *   defaults: The theme's `design_defaults` from `GET /api/themes`.
 *
 * Returns:
 *   Paths such as `header.connections.separator`, in document order; empty
 *   when the document matches the theme. `theme` itself is never listed.
 */
export function designOverrides(design: unknown, defaults: JsonObject): string[] {
	if (!isPlainObject(design)) return [];
	const out: string[] = [];
	for (const [key, child] of Object.entries(design)) {
		if (key === 'theme') continue;
		collectDifferences(child, defaults[key], [key], out);
	}
	return out;
}

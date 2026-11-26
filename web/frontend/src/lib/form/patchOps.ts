/**
 * Pure tree operations mirroring the `/api/documents/patch` op contract, so
 * the form can apply an optimistic local update to the parsed document the
 * instant a user edits a field, without waiting for the round trip.
 *
 * Contract (fixed by the backend, see the phase task): paths are arrays of
 * string keys / integer indices INTO THE FULL DOCUMENT (a cv field path
 * starts with `"cv"`).
 */

export type PathSegment = string | number;

export type PatchOp =
	| { op: 'set'; path: PathSegment[]; value: unknown }
	| { op: 'insert'; path: PathSegment[]; index: number; value: unknown }
	| { op: 'delete'; path: PathSegment[] }
	| { op: 'move'; path: PathSegment[]; from_index: number; to_index: number };

function isIndex(segment: PathSegment): segment is number {
	return typeof segment === 'number';
}

/**
 * A shallow copy of a container value, or a fresh empty container if the
 * value isn't one yet (supports "set/insert creates the path").
 *
 * @param preferArray When `value` doesn't already exist, build `[]` instead
 * of the usual `{}` fallback. Needed for `insert`/`move`: an entry's
 * optional array field (e.g. `highlights`, never populated by
 * `entrySkeleton` since it's not required) genuinely does not exist yet the
 * first time a user adds an item to it -- without this, the walk would
 * silently fabricate an empty *object* at that path, and the op below would
 * then reject it for "not pointing to an array".
 */
function cloneContainer(value: unknown, preferArray = false): Record<string, unknown> | unknown[] {
	if (Array.isArray(value)) return [...value];
	if (value !== null && typeof value === 'object') return { ...(value as Record<string, unknown>) };
	return preferArray ? [] : {};
}

function setChild(parent: Record<string, unknown> | unknown[], key: PathSegment, value: unknown): void {
	if (isIndex(key)) (parent as unknown[])[key] = value;
	else (parent as Record<string, unknown>)[key as string] = value;
}

function getChild(parent: unknown, key: PathSegment): unknown {
	if (parent === null || parent === undefined) return undefined;
	return isIndex(key) ? (parent as unknown[])[key] : (parent as Record<string, unknown>)[key as string];
}

/**
 * Clones every container from the root down to (and including) the node
 * living at `path`, wiring the clones together, and returns both the new
 * root and that path's cloned node ready to mutate in place.
 *
 * Why a generic "clone the spine" helper: every op below needs a mutable,
 * copy-on-write path into the tree — either to the *parent* of its target
 * (`set`/`delete`, so they can replace/remove one key) or to the array *at*
 * its target (`insert`/`move`, so they can splice it) — this single walk
 * serves both by choosing what to pass as `path`.
 */
function cloneSpineTo(
	root: unknown,
	path: PathSegment[],
	/** See `cloneContainer`'s `preferArray` doc comment -- passed through only for the final (target) node, e.g. `insert`/`move`'s array target. */
	arrayAtEnd = false
): { rootClone: unknown; node: Record<string, unknown> | unknown[] } {
	const rootClone = cloneContainer(root);
	let originalCursor: unknown = root;
	let cloneCursor: Record<string, unknown> | unknown[] = rootClone;

	path.forEach((segment, i) => {
		const originalChild = getChild(originalCursor, segment);
		const clonedChild = cloneContainer(originalChild, arrayAtEnd && i === path.length - 1);
		setChild(cloneCursor, segment, clonedChild);
		cloneCursor = clonedChild;
		originalCursor = originalChild;
	});

	return { rootClone, node: cloneCursor };
}

/**
 * Applies a single {@link PatchOp} to a document tree, returning a new tree
 * (the input is never mutated — a rejected optimistic update can be
 * discarded by simply dropping the returned value).
 */
export function applyOp(tree: unknown, op: PatchOp): unknown {
	switch (op.op) {
		case 'set': {
			const { rootClone, node } = cloneSpineTo(tree, op.path.slice(0, -1));
			setChild(node, op.path[op.path.length - 1], op.value);
			return rootClone;
		}
		case 'delete': {
			const { rootClone, node } = cloneSpineTo(tree, op.path.slice(0, -1));
			const last = op.path[op.path.length - 1];
			if (Array.isArray(node) && isIndex(last)) node.splice(last, 1);
			else if (!Array.isArray(node)) delete (node as Record<string, unknown>)[last as string];
			return rootClone;
		}
		case 'insert': {
			const { rootClone, node } = cloneSpineTo(tree, op.path, true);
			if (!Array.isArray(node)) {
				throw new Error(`insert path "${pathKey(op.path)}" does not point to an array.`);
			}
			node.splice(op.index, 0, op.value);
			return rootClone;
		}
		case 'move': {
			const { rootClone, node } = cloneSpineTo(tree, op.path, true);
			if (!Array.isArray(node)) {
				throw new Error(`move path "${pathKey(op.path)}" does not point to an array.`);
			}
			const [moved] = node.splice(op.from_index, 1);
			node.splice(op.to_index, 0, moved);
			return rootClone;
		}
		default:
			return tree;
	}
}

/** Reads a value at a path without cloning (helper for tests/callers that just want to inspect the tree). */
export function getAtPath(tree: unknown, path: PathSegment[]): unknown {
	let cursor: unknown = tree;
	for (const segment of path) {
		cursor = getChild(cursor, segment);
	}
	return cursor;
}

/**
 * Collapses consecutive ops so a burst of edits to the same field (e.g. one
 * `set` per keystroke, all coalesced by the sync debounce) becomes a single
 * op before hitting the network — the last `set` to a given path wins,
 * matching what the backend would end up applying anyway.
 */
export function collapseOps(ops: PatchOp[]): PatchOp[] {
	const collapsed: PatchOp[] = [];
	for (const op of ops) {
		const previous = collapsed[collapsed.length - 1];
		if (
			previous &&
			previous.op === 'set' &&
			op.op === 'set' &&
			pathKey(previous.path) === pathKey(op.path)
		) {
			collapsed[collapsed.length - 1] = op;
			continue;
		}
		collapsed.push(op);
	}
	return collapsed;
}

/** Dotted-path key for a path array — matches the API's `location` string format (`"cv.sections.Education.0.degree"`). */
export function pathKey(path: PathSegment[]): string {
	return path.join('.');
}

import type { EntryTypeName } from '$lib/schema/cvSchema';
import { entrySkeleton } from '$lib/schema/cvSchema';
import type { FieldDescriptor } from '$lib/schema/types';
import type { PatchOp, PathSegment } from './patchOps';

/**
 * Pure op-builders for every `cv.sections` edit the form makes. Kept
 * separate from the Svelte components so "editing a field emits the right
 * op" is unit-testable without mounting anything.
 *
 * Why sections need dedicated builders instead of a generic
 * schema-to-op mapper: `cv.sections` is a mapping of arbitrary titles to
 * lists of one of 9 polymorphic entry types (see `cvSchema.ts`) — there is
 * no single JSON Schema node to walk generically the way the header fields
 * (`FieldRow`/`ArrayField`/`ObjectFieldset`) are.
 */

export type SectionsMap = Record<string, unknown[]>;

function sectionPath(title: string): PathSegment[] {
	return ['cv', 'sections', title];
}

/** Adds a brand-new, empty section (a mapping key whose value is `[]`). */
export function buildAddSectionOp(title: string): PatchOp {
	return { op: 'set', path: sectionPath(title), value: [] };
}

export function buildDeleteSectionOp(title: string): PatchOp {
	return { op: 'delete', path: sectionPath(title) };
}

/**
 * Renaming a section is a mapping-key rename, which the patch contract has
 * no dedicated op for (`set`/`delete`/`insert`/`move` all target a single
 * key or an array index, never "this key becomes that key"). Chosen
 * fallback: rebuild the whole `cv.sections` mapping with the new key in the
 * old key's place, as a single `set` on `["cv","sections"]`.
 *
 * Trade-off (documented per the phase task): this loses the *other*
 * sections' relative position information the backend might otherwise
 * preserve internally (e.g. YAML key order via ruamel) only insofar as we
 * are the ones re-asserting the full order here — but since we rebuild the
 * map from the current in-memory order (which already reflects the
 * document), the visible order does not change for the user.
 */
export function buildRenameSectionOp(sections: SectionsMap, fromTitle: string, toTitle: string): PatchOp {
	const rebuilt: SectionsMap = {};
	for (const [title, entries] of Object.entries(sections)) {
		rebuilt[title === fromTitle ? toTitle : title] = entries;
	}
	return { op: 'set', path: ['cv', 'sections'], value: rebuilt };
}

export function buildAddEntryOp(
	sectionTitle: string,
	entryCount: number,
	type: EntryTypeName,
	fields: FieldDescriptor[]
): PatchOp {
	return {
		op: 'insert',
		path: sectionPath(sectionTitle),
		index: entryCount,
		value: entrySkeleton(type, fields)
	};
}

export function buildDeleteEntryOp(sectionTitle: string, index: number): PatchOp {
	return { op: 'delete', path: [...sectionPath(sectionTitle), index] };
}

export function buildMoveEntryOp(sectionTitle: string, fromIndex: number, toIndex: number): PatchOp {
	return { op: 'move', path: sectionPath(sectionTitle), from_index: fromIndex, to_index: toIndex };
}

/** Replaces a whole entry's value in place (used for `TextEntry`, which is a bare string with no field key of its own). */
export function buildSetEntryValueOp(sectionTitle: string, entryIndex: number, value: unknown): PatchOp {
	return { op: 'set', path: [...sectionPath(sectionTitle), entryIndex], value };
}

export function buildSetEntryFieldOp(
	sectionTitle: string,
	entryIndex: number,
	fieldKey: string,
	value: unknown
): PatchOp {
	return { op: 'set', path: [...sectionPath(sectionTitle), entryIndex, fieldKey], value };
}

function highlightsPath(sectionTitle: string, entryIndex: number): PathSegment[] {
	return [...sectionPath(sectionTitle), entryIndex, 'highlights'];
}

export function buildAddHighlightOp(sectionTitle: string, entryIndex: number, count: number): PatchOp {
	return { op: 'insert', path: highlightsPath(sectionTitle, entryIndex), index: count, value: '' };
}

export function buildDeleteHighlightOp(
	sectionTitle: string,
	entryIndex: number,
	highlightIndex: number
): PatchOp {
	return { op: 'delete', path: [...highlightsPath(sectionTitle, entryIndex), highlightIndex] };
}

export function buildMoveHighlightOp(
	sectionTitle: string,
	entryIndex: number,
	fromIndex: number,
	toIndex: number
): PatchOp {
	return {
		op: 'move',
		path: highlightsPath(sectionTitle, entryIndex),
		from_index: fromIndex,
		to_index: toIndex
	};
}

export function buildSetHighlightOp(
	sectionTitle: string,
	entryIndex: number,
	highlightIndex: number,
	value: string
): PatchOp {
	return { op: 'set', path: [...highlightsPath(sectionTitle, entryIndex), highlightIndex], value };
}

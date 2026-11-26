import { resolveDefFields } from './resolver';
import type { FieldDescriptor, JsonSchemaDocument } from './types';

/**
 * The 9 entry shapes a `cv.sections` list item can take (see
 * `rendercv/schema/models/cv/entries.py`'s `ListOfEntries` union). `TextEntry`
 * is not a `$defs` entry of its own — it's the bare-string branch of that
 * union — so it's the one type here whose fields don't come from the schema.
 */
export const ENTRY_TYPES = [
	'EducationEntry',
	'ExperienceEntry',
	'NormalEntry',
	'PublicationEntry',
	'OneLineEntry',
	'BulletEntry',
	'NumberedEntry',
	'ReversedNumberedEntry',
	'TextEntry'
] as const;

export type EntryTypeName = (typeof ENTRY_TYPES)[number];

export interface EntryTypeDescriptor {
	type: EntryTypeName;
	/** A short, human label for the entry-type picker. */
	label: string;
	/** A 1-line hint derived from the schema's required/optional fields. */
	hint: string;
	/** Field descriptors to render for this entry type (empty for TextEntry). */
	fields: FieldDescriptor[];
}

const ENTRY_TYPE_LABELS: Record<EntryTypeName, string> = {
	EducationEntry: 'Education',
	ExperienceEntry: 'Experience',
	NormalEntry: 'Normal (project, award, event)',
	PublicationEntry: 'Publication',
	OneLineEntry: 'One line (label + details)',
	BulletEntry: 'Bullet point',
	NumberedEntry: 'Numbered item',
	ReversedNumberedEntry: 'Reverse-numbered item',
	TextEntry: 'Plain text'
};

/** All fields of the CV's top-level object except `sections`, which the dedicated `SectionsEditor` owns. */
export function getCvHeaderFields(schema: JsonSchemaDocument): FieldDescriptor[] {
	return resolveDefFields(schema, 'Cv').filter((field) => field.key !== 'sections');
}

function hintFor(type: EntryTypeName, fields: FieldDescriptor[]): string {
	if (type === 'TextEntry') return 'A single plain-text line, with no structured fields.';

	const required = fields.filter((f) => f.required).map((f) => f.label);
	const optional = fields.filter((f) => !f.required).map((f) => f.label);
	const requiredPart = required.length > 0 ? `${required.join(' + ')} required` : 'no required fields';
	const optionalPart = optional.length > 0 ? `; optionally ${optional.slice(0, 3).join(', ')}` : '';
	return `${requiredPart}${optionalPart}.`;
}

/** Resolves the field descriptors + a 1-line hint for all 9 entry types, straight from the schema's `$defs`. */
export function getEntryTypeDescriptors(schema: JsonSchemaDocument): EntryTypeDescriptor[] {
	return ENTRY_TYPES.map((type) => {
		const fields = type === 'TextEntry' ? [] : resolveDefFields(schema, type);
		return { type, label: ENTRY_TYPE_LABELS[type], hint: hintFor(type, fields), fields };
	});
}

/**
 * Infers which of the 9 entry types an existing `cv.sections` list item is,
 * from the fields present on it — the same "automatically detected based on
 * their fields" behavior the schema's own `sections` description promises.
 *
 * Why a fixed priority order instead of a more clever match: some fields
 * (e.g. `name`) are common enough across future entry additions that the
 * order must match the core's own discrimination priority; this mirrors it
 * field-by-field rather than re-deriving it from the schema at runtime.
 */
export function inferEntryType(entry: unknown): EntryTypeName | null {
	if (typeof entry === 'string') return 'TextEntry';
	if (entry === null || typeof entry !== 'object') return null;

	const value = entry as Record<string, unknown>;
	if ('institution' in value) return 'EducationEntry';
	if ('company' in value) return 'ExperienceEntry';
	if ('title' in value && 'authors' in value) return 'PublicationEntry';
	if ('name' in value) return 'NormalEntry';
	if ('bullet' in value) return 'BulletEntry';
	if ('number' in value) return 'NumberedEntry';
	if ('reversed_number' in value) return 'ReversedNumberedEntry';
	if ('label' in value && 'details' in value) return 'OneLineEntry';
	return null;
}

/** The field whose value best identifies an entry at a glance, per entry type -- used for the collapsed one-line summary. `null` means the type has no single obvious identifying field (falls back to the entry-type label). */
const ENTRY_SUMMARY_KEY: Partial<Record<EntryTypeName, string>> = {
	EducationEntry: 'institution',
	ExperienceEntry: 'company',
	NormalEntry: 'name',
	PublicationEntry: 'title',
	OneLineEntry: 'label',
	BulletEntry: 'bullet',
	NumberedEntry: 'number',
	ReversedNumberedEntry: 'reversed_number'
};

/**
 * The one-line summary shown for a collapsed `cv.sections` entry (reference
 * UX: institution/company/name/label value). `TextEntry` is the bare string
 * itself; every other type reads its identifying field (see
 * {@link ENTRY_SUMMARY_KEY}) and falls back to a placeholder when that field
 * is still empty, so a freshly-added entry never collapses to blank text.
 */
export function entrySummaryText(type: EntryTypeName, entry: unknown): string {
	if (type === 'TextEntry') {
		const text = typeof entry === 'string' ? entry.trim() : '';
		return text || 'Empty entry';
	}

	const key = ENTRY_SUMMARY_KEY[type];
	const value = key && entry && typeof entry === 'object' ? (entry as Record<string, unknown>)[key] : undefined;
	const text = typeof value === 'string' ? value.trim() : '';
	return text || 'Untitled entry';
}

/**
 * Builds a fresh entry value of the given type, using only its schema's
 * required fields defaulted to an empty value of the right kind.
 *
 * Why derive from field descriptors instead of a hand-written literal per
 * type: the moment a required field is added to an entry model in the core,
 * this stays correct with zero frontend changes.
 */
export function entrySkeleton(type: EntryTypeName, fields: FieldDescriptor[]): unknown {
	if (type === 'TextEntry') return '';

	const skeleton: Record<string, unknown> = {};
	for (const field of fields.filter((f) => f.required)) {
		skeleton[field.key] =
			field.kind === 'array' ? [] : field.kind === 'boolean' ? false : field.kind === 'number' ? null : '';
	}
	return skeleton;
}

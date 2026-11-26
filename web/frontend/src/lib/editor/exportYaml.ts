import {
	DOCUMENT_KEYS,
	type CvDocuments,
	type DocumentKey
} from '$lib/stores/documents';

/**
 * Joins the editor's four documents into a single RenderCV input file.
 *
 * Why concatenation is the whole implementation: each document already
 * carries its own top-level key (`cv:`, `design:`, `locale:`, `settings:`),
 * so putting them one after another produces exactly the shape RenderCV's
 * own CLI reads -- `rendercv render <file>.yaml` accepts the result without
 * any further step. Anything cleverer (parse, merge, re-serialise) would
 * reformat the user's YAML, losing their comments and key order, to produce
 * a file that is no more valid.
 *
 * Empty documents are dropped rather than emitted as bare keys: `design`,
 * `locale` and `settings` are all optional, and an empty `design:` is not
 * the same thing to RenderCV as an absent one.
 *
 * @param docs The editor's four documents.
 * @returns One YAML file, or the empty string when every document is empty.
 */
export function buildRendercvYaml(docs: CvDocuments): string {
	const blocks = DOCUMENT_KEYS.map((key) => docs[key].trim()).filter(
		(block) => block.length > 0
	);
	if (blocks.length === 0) return '';
	// A blank line between blocks, and a trailing newline: this is a text
	// file people will open in an editor, not only feed to a parser.
	return `${blocks.join('\n\n')}\n`;
}

/** What `splitRendercvYaml` made of a file the user chose. */
export type ImportOutcome =
	| { ok: true; documents: CvDocuments }
	| { ok: false; reason: string };

/** Matches a top-level key: no indentation, a name, then a colon. */
const TOP_LEVEL_KEY = /^([A-Za-z_][A-Za-z0-9_-]*):(\s|$)/;

/**
 * Splits a RenderCV input file back into the editor's four documents.
 *
 * The inverse of `buildRendercvYaml`, and text-based for the same reason:
 * slicing the file between its top-level keys hands each tab exactly the
 * bytes the file had, comments and key order included. Parsing the YAML and
 * re-serialising four fragments would reformat everything the user wrote.
 *
 * What it refuses, rather than guessing:
 *   - a file with no `cv:` key, which is not a RenderCV file at all;
 *   - a top-level key that is not one of the four, since the editor has
 *     nowhere to put it and dropping it silently would lose the user's
 *     content;
 *   - text before the first key that is not a comment, which means the file
 *     is something else entirely.
 *
 * Anything indented belongs to the key above it and is never inspected, so
 * a `cv:` appearing as a nested value cannot start a new block.
 *
 * @param text The file's contents.
 * @returns The four documents, or the reason the file was refused.
 */
export function splitRendercvYaml(text: string): ImportOutcome {
	// Files arrive from every operating system; CRLF would otherwise end up
	// inside the documents and show as stray characters in the editor.
	const lines = text.replace(/\r\n?/g, '\n').split('\n');

	const blocks = new Map<DocumentKey, string[]>();
	let current: DocumentKey | null = null;
	const preamble: string[] = [];

	for (const line of lines) {
		const match = TOP_LEVEL_KEY.exec(line);
		if (match) {
			const key = match[1];
			if (!(DOCUMENT_KEYS as string[]).includes(key)) {
				return {
					ok: false,
					reason: `The file has a top-level "${key}:" section, which the editor has nowhere to put.`
				};
			}
			if (blocks.has(key as DocumentKey)) {
				return { ok: false, reason: `The file declares "${key}:" more than once.` };
			}
			current = key as DocumentKey;
			blocks.set(current, [line]);
			continue;
		}
		if (current === null) {
			if (line.trim() !== '' && !line.trimStart().startsWith('#')) {
				return { ok: false, reason: 'The file does not start with a RenderCV section.' };
			}
			preamble.push(line);
			continue;
		}
		blocks.get(current)?.push(line);
	}

	if (!blocks.has('cv')) {
		return { ok: false, reason: 'The file has no "cv:" section, so it is not a RenderCV file.' };
	}

	// A comment header belongs to the document it introduces, which is
	// whichever section the file happens to open with.
	const first = [...blocks.keys()][0];
	if (preamble.some((line) => line.trim() !== '')) {
		blocks.set(first, [...preamble, ...(blocks.get(first) ?? [])]);
	}

	const documents = { cv: '', design: '', locale: '', settings: '' } as CvDocuments;
	for (const key of DOCUMENT_KEYS) {
		const block = blocks.get(key);
		documents[key] = block ? `${block.join('\n').trimEnd()}\n` : '';
	}
	return { ok: true, documents };
}

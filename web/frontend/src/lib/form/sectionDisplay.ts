/**
 * Pure display-string helpers for `cv.sections` titles — kept separate from
 * `SectionsEditor.svelte` so the capitalization/singularization rules are
 * unit-testable without mounting anything (same rationale as
 * `sectionsActions.ts`).
 *
 * Why these exist: `cv.sections` titles are arbitrary user text (the schema
 * has no enum of "known" section names), but the reference UI still shows
 * them as a proper heading ("Education", not "education") and reuses the
 * title in the contextual add button ("+ Add education entry"). Both need a
 * presentation transform the underlying document/store never applies to the
 * title itself (renaming a section still round-trips the user's exact text).
 */

/**
 * Renders a section title the way a heading should read: underscores become
 * spaces, and an all-lowercase title (the common case for a hand-typed
 * snake_case title like `professional_experience`) gets each word
 * capitalized. A title that already contains any uppercase letter is assumed
 * to be deliberately cased (e.g. "Open Source Projects") and is left alone
 * apart from the underscore-to-space swap.
 */
export function displaySectionTitle(title: string): string {
	const spaced = title.includes('_') ? title.replace(/_/g, ' ') : title;
	if (/[A-Z]/.test(spaced)) return spaced;

	return spaced
		.split(' ')
		.map((word) => (word.length > 0 ? word[0].toUpperCase() + word.slice(1) : word))
		.join(' ');
}

/** Singularizes one word with a few common English plural endings -- good enough for section-title nouns, not a general stemmer. */
function singularizeWord(word: string): string {
	if (/ies$/i.test(word) && word.length > 3) return word.slice(0, -3) + 'y';
	if (/(sh|ch|x|z|s)es$/i.test(word) && word.length > 3) return word.slice(0, -2);
	if (/s$/i.test(word) && !/ss$/i.test(word) && word.length > 1) return word.slice(0, -1);
	return word;
}

/**
 * Builds the noun phrase for the section's contextual add button, e.g.
 * "Education" -> "education", "Publications" -> "publication",
 * "Extracurricular Activities" -> "extracurricular activity" -- only the
 * last word (the noun) is singularized; the rest of the phrase is left
 * alone and everything is lowercased to read naturally as "+ Add {…} entry".
 */
export function addEntryLabel(sectionTitle: string): string {
	const words = displaySectionTitle(sectionTitle)
		.trim()
		.split(/\s+/)
		.filter(Boolean);
	if (words.length === 0) return 'entry';

	const lastIndex = words.length - 1;
	return words
		.map((word, index) => (index === lastIndex ? singularizeWord(word) : word).toLowerCase())
		.join(' ');
}

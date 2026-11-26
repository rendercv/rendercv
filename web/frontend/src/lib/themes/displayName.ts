/**
 * How a theme's identifier is written when a person has to read it.
 *
 * Why this exists: `GET /api/themes` returns the identifiers the Python
 * package uses -- `engineeringresumes`, `sb2nov` -- because that is what
 * goes into the YAML's `design.theme` field, and the API must keep
 * returning exactly that. But `engineeringresumes` is not a name, it is a
 * key with the spaces filed off, and putting it in front of a user in the
 * theme switcher was the reason the control read as unfinished next to
 * the reference implementation.
 *
 * Why one module rather than a literal at each call site: the landing
 * page's themes strip already had its own hand-written list of pretty
 * names, so the app was calling the same nine themes by two different
 * sets of names in two places, with nothing keeping them in step. Both
 * now read from here.
 *
 * Only the display text is affected. Every value that crosses into the
 * document, the API or an event stays the raw identifier.
 */

/**
 * The built-in themes, keyed by the identifier the API returns.
 *
 * Mirrors `src/rendercv/schema/models/design/`: `classic_theme.py` plus
 * the eight files under `other_themes/`.
 */
const BUILT_IN_DISPLAY_NAMES: Record<string, string> = {
	classic: 'Classic',
	sb2nov: 'Sb2nov',
	moderncv: 'Moderncv',
	engineeringresumes: 'Engineering Resumes',
	engineeringclassic: 'Engineering Classic',
	harvard: 'Harvard',
	ink: 'Ink',
	opal: 'Opal',
	ember: 'Ember'
};

/** The built-in themes in the order the landing page presents them. */
export const BUILT_IN_THEME_NAMES: string[] = [
	'classic',
	'sb2nov',
	'moderncv',
	'engineeringresumes',
	'engineeringclassic',
	'harvard',
	'ink',
	'opal',
	'ember'
];

/**
 * The human-readable name for a theme identifier.
 *
 * Why unknown identifiers get a computed name instead of being passed
 * through: RenderCV supports custom themes (`rendercv create-theme`), and
 * a deployment that ships one would otherwise be the only place in the UI
 * still showing a bare key. Separators become spaces and the first letter
 * is capitalised, which is a reasonable name for the identifiers a person
 * actually writes and never worse than the raw key.
 *
 * @param name The theme identifier, as returned by `GET /api/themes`.
 * @returns The name to show a reader. Never the empty string for a
 *   non-empty input.
 */
export function themeDisplayName(name: string): string {
	const known = BUILT_IN_DISPLAY_NAMES[name];
	if (known !== undefined) return known;

	const spaced = name.replace(/[_-]+/g, ' ').trim();
	if (spaced === '') return name;
	return spaced.charAt(0).toUpperCase() + spaced.slice(1);
}

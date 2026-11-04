/**
 * The one sentence telling a form user what a text field accepts.
 *
 * Why this needs saying at all: nothing in the UI does. The JSON schema
 * mentions Markdown only in the names of output files (`markdown_path`,
 * `dont_generate_markdown`), never to say that content fields understand
 * it -- so no field description carries it. And the B/I/link buttons in
 * the toolbar are disabled outside YAML mode (`EditorPane`), which if
 * anything suggests the opposite. A user editing through the form has no
 * way to discover that `**bold**` works, or that a `#` heading does not.
 *
 * Kept as one exported constant rather than repeated string literals so
 * the wording cannot drift between the standalone-field and array-field
 * renderings.
 */
export const MARKDOWN_FORMAT_HINT =
	'Supports inline Markdown: **bold**, *italic*, [link](url). Headings, lists and other block formatting are not.';

/** The result of wrapping a text selection with markdown markers. */
export interface WrapResult {
	text: string;
	/** New selection start, inside the markers if nothing was selected before. */
	selectionStart: number;
	/** New selection end. */
	selectionEnd: number;
}

/**
 * Wraps the substring `[selectionStart, selectionEnd)` of `text` with the
 * given markdown markers (`**…**` for bold, `*…*` for italic).
 *
 * Why pure: this is the B/I toolbar's core logic, independent of CodeMirror,
 * so it can be unit-tested without a view/state and reused if the selection
 * source ever changes (e.g. a future form-mode rich text field).
 *
 * @param text Full document text.
 * @param selectionStart Selection start offset.
 * @param selectionEnd Selection end offset (equal to start if collapsed).
 * @param before Marker inserted before the selection (e.g. `"**"`).
 * @param after Marker inserted after the selection (e.g. `"**"`).
 */
export function wrapSelection(
	text: string,
	selectionStart: number,
	selectionEnd: number,
	before: string,
	after: string
): WrapResult {
	const selected = text.slice(selectionStart, selectionEnd);
	const inserted = `${before}${selected}${after}`;
	const newText = text.slice(0, selectionStart) + inserted + text.slice(selectionEnd);

	if (selected.length === 0) {
		// Nothing selected: place the cursor between the markers.
		const cursor = selectionStart + before.length;
		return { text: newText, selectionStart: cursor, selectionEnd: cursor };
	}

	return {
		text: newText,
		selectionStart: selectionStart + before.length,
		selectionEnd: selectionStart + before.length + selected.length
	};
}

/**
 * Wraps a selection as a markdown link: `[selected](url)`, or `[title](url)`
 * with a placeholder title when nothing is selected.
 */
export function wrapAsLink(
	text: string,
	selectionStart: number,
	selectionEnd: number,
	url = 'url',
	placeholderTitle = 'title'
): WrapResult {
	const selected = text.slice(selectionStart, selectionEnd);
	const title = selected.length > 0 ? selected : placeholderTitle;
	const inserted = `[${title}](${url})`;
	const newText = text.slice(0, selectionStart) + inserted + text.slice(selectionEnd);

	// Select the URL placeholder so typing immediately replaces it, matching
	// the reference editor's link-insert behavior.
	const urlStart = selectionStart + title.length + 3; // "[" + title + "]("
	const urlEnd = urlStart + url.length;
	return { text: newText, selectionStart: urlStart, selectionEnd: urlEnd };
}

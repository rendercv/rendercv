<script lang="ts">
	/**
	 * The project's mark, drawn in one place.
	 *
	 * Why a component and not an inline `<svg>` at each call site, which is
	 * what this replaced: there were two, and they had drifted into
	 * different drawings. The landing page's nav showed a document; the
	 * editor's sidebar showed a bird. Nothing failed, nothing warned, and
	 * the two pages of the same app simply stopped agreeing on what it
	 * looks like. A shared component makes that particular drift
	 * impossible.
	 *
	 * The drawing is the landing page's: a page of text with a mark on it.
	 * `src/lib/assets/favicon.svg` carries the same shape, since the
	 * browser tab is a third place the mark appears -- and it is the one
	 * place a file has to be duplicated, because a favicon is fetched as a
	 * standalone file rather than rendered by this component. Change one
	 * and change the other.
	 *
	 * Colour is inherited (`currentColor`), so a caller sets it with a text
	 * colour class and the mark follows the surrounding theme.
	 */
	const { size = 24 }: { size?: number } = $props();
</script>

<svg
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	aria-hidden="true"
	class="shrink-0"
	data-brand-mark
>
	<rect x="3" y="2" width="14" height="20" rx="2" stroke="currentColor" stroke-width="1.6" />
	<path d="M6.5 7h7M6.5 11h7M6.5 15h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
	<path d="M15 15l4 4m0-4l-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
</svg>

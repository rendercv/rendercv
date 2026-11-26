<script lang="ts">
	import CyclerDropdown from './CyclerDropdown.svelte';
	import { themeDisplayName } from '$lib/themes/displayName';

	/**
	 * Tab-bar theme quick-switcher (`‹ [name ˅] ›`), visible on every tab —
	 * matches the reference. Presentation only: the caller (`EditorPane`)
	 * owns the shared design-document sync so the switcher and the Design
	 * form's field views never race each other over the same document.
	 *
	 * `themeNames` holds the identifiers `GET /api/themes` returns, which
	 * are what `design.theme` must be set to; `themeDisplayName` is applied
	 * to the label only, so `onSwitch` still receives `engineeringresumes`
	 * while the reader sees `Engineering Resumes`.
	 */
	let {
		themeNames,
		currentTheme,
		onSwitch
	}: {
		themeNames: string[];
		currentTheme: string;
		onSwitch: (theme: string) => void;
	} = $props();
</script>

<CyclerDropdown
	options={themeNames}
	value={currentTheme}
	onchange={onSwitch}
	format={themeDisplayName}
	ariaLabel="Theme"
	id="theme-switcher"
/>

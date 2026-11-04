<script lang="ts">
	import CyclerDropdown from './CyclerDropdown.svelte';

	/**
	 * `‹ value ›` + dropdown for longer enums (font families, languages) —
	 * too many options for `SegmentedControl` to lay out as buttons.
	 */
	let {
		options,
		value,
		onchange,
		ariaLabel,
		id
	}: {
		options: string[];
		value: string;
		onchange: (value: string) => void;
		ariaLabel: string;
		id?: string;
	} = $props();
</script>

<CyclerDropdown {options} {value} {onchange} {ariaLabel} {id} />

<script lang="ts">
	import { toHexColor } from './color';

	/**
	 * Color swatch (a native `<input type="color">` behind it, for a quick
	 * picker) + a text input holding the schema's raw string form
	 * (hex/rgb/named) as-is — the text input is the source of truth, the
	 * swatch is a convenience.
	 */
	let {
		value,
		placeholder,
		onchange,
		id
	}: {
		value: string;
		placeholder?: string;
		onchange: (value: string) => void;
		id: string;
	} = $props();

	let hexForPicker = $derived(toHexColor(value) ?? '#000000');

	function handleTextChange(e: Event): void {
		onchange((e.currentTarget as HTMLInputElement).value);
	}

	function handlePickerChange(e: Event): void {
		onchange((e.currentTarget as HTMLInputElement).value);
	}
</script>

<div class="flex items-center gap-2">
	<span class="relative h-7 w-7 shrink-0 overflow-hidden rounded-md border border-neutral-300 dark:border-[var(--border-subtle)]">
		<span class="absolute inset-0" style={`background-color: ${value || 'transparent'}`} aria-hidden="true"
		></span>
		<input
			type="color"
			class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
			aria-label="Pick a color"
			value={hexForPicker}
			oninput={handlePickerChange}
		/>
	</span>
	<input
		{id}
		type="text"
		class="w-full rounded-md border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100 dark:placeholder:text-neutral-600"
		{placeholder}
		{value}
		oninput={handleTextChange}
	/>
</div>

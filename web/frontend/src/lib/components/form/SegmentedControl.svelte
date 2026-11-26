<script lang="ts">
	/**
	 * A `role=radiogroup` segmented control for short enums (page size,
	 * alignment, ...) — reference UX calls these out explicitly (A4 / US
	 * Letter). `FieldRow` picks this over `StepperField` when the enum has
	 * few enough options to lay out as buttons without wrapping awkwardly.
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

<div {id} role="radiogroup" aria-label={ariaLabel} class="flex flex-wrap gap-1">
	{#each options as option (option)}
		<button
			type="button"
			role="radio"
			aria-checked={value === option}
			class="rounded-md border px-2 py-1 text-xs font-medium transition-colors"
			class:border-purple-600={value === option}
			class:bg-purple-600={value === option}
			class:text-white={value === option}
			class:border-neutral-300={value !== option}
			class:text-neutral-600={value !== option}
			class:dark:border-[var(--border-subtle)]={value !== option}
			class:dark:text-neutral-300={value !== option}
			onclick={() => onchange(option)}
		>
			{option}
		</button>
	{/each}
</div>

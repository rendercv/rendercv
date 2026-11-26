<script lang="ts">
	import type { EntryTypeDescriptor, EntryTypeName } from '$lib/schema/cvSchema';

	let {
		descriptors,
		onSelect
	}: {
		descriptors: EntryTypeDescriptor[];
		onSelect: (type: EntryTypeName) => void;
	} = $props();
</script>

<div class="flex flex-col gap-2">
	<p class="text-xs text-neutral-500 dark:text-neutral-400">Choose the type of the first entry in this section:</p>
	<div role="radiogroup" aria-label="Entry type" class="grid grid-cols-1 gap-2 sm:grid-cols-2">
		{#each descriptors as d (d.type)}
			<button
				type="button"
				role="radio"
				aria-checked="false"
				class="rounded-md border border-neutral-200 p-2 text-left text-sm transition-colors hover:border-purple-400 dark:border-[var(--border-subtle)] dark:hover:border-purple-500"
				onclick={() => onSelect(d.type)}
			>
				<span class="block font-medium text-neutral-800 dark:text-neutral-200">{d.label}</span>
				<span class="mt-0.5 block text-xs text-neutral-500 dark:text-neutral-400">{d.hint}</span>
			</button>
		{/each}
	</div>
</div>

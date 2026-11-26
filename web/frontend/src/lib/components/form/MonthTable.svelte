<script lang="ts">
	/**
	 * A fixed 12-row table (label column = the English month/abbreviation,
	 * value column = the current language's translation) — used for
	 * `locale.month_names` and `locale.month_abbreviations`. Unlike
	 * `ArrayField`, rows are never added/removed/reordered: the shape is
	 * fixed by the schema (`minItems`/`maxItems: 12`).
	 */
	let {
		label,
		referenceLabels,
		values,
		overridden,
		onReset,
		onChangeIndex
	}: {
		label: string;
		referenceLabels: readonly string[];
		values: string[];
		overridden: boolean;
		onReset: () => void;
		onChangeIndex: (index: number, value: string) => void;
	} = $props();
</script>

<div class="flex flex-col gap-2 border-b border-neutral-100 py-2 last:border-b-0 dark:border-[var(--border-subtle)]">
	<div class="flex items-center gap-1">
		<span
			class="text-sm font-medium"
			class:text-neutral-700={overridden}
			class:dark:text-neutral-300={overridden}
			class:italic={!overridden}
			class:text-neutral-400={!overridden}
			class:dark:text-neutral-400={!overridden}
		>
			{label}
		</span>
		{#if overridden}
			<button
				type="button"
				class="grid h-5 w-5 shrink-0 place-items-center rounded text-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:hover:bg-purple-950"
				aria-label={`Reset ${label} to default`}
				title="Reset to default"
				onclick={onReset}
			>
				↺
			</button>
		{/if}
	</div>

	<div class="grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-2">
		{#each referenceLabels as referenceLabel, i (referenceLabel)}
			<div class="flex items-center gap-2">
				<label for={`month-${label}-${i}`} class="w-24 shrink-0 text-xs text-neutral-500 dark:text-neutral-400">
					{referenceLabel}
				</label>
				<input
					id={`month-${label}-${i}`}
					type="text"
					class="w-full rounded-md border border-neutral-300 bg-white px-2 py-1 text-sm text-neutral-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100"
					value={values[i] ?? ''}
					oninput={(e) => onChangeIndex(i, (e.currentTarget as HTMLInputElement).value)}
				/>
			</div>
		{/each}
	</div>
</div>

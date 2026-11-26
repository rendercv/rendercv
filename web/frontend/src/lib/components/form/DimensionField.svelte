<script lang="ts">
	import { DIMENSION_UNITS, parseDimension, serializeDimension, type DimensionUnit } from '$lib/form/dimension';

	/**
	 * Number input + unit suffix for typst-dimension strings (`"0.7in"`,
	 * `"10pt"`, `"1.25em"`). Parses the incoming string once for display;
	 * every edit re-serializes back to the same string form the schema
	 * expects. Falls back to a plain text box if the value doesn't parse
	 * (e.g. mid-edit or an unusual value) so the user's input is never
	 * silently discarded.
	 */
	let {
		value,
		onchange,
		id
	}: {
		value: string;
		onchange: (value: string) => void;
		id: string;
	} = $props();

	let parsed = $derived(parseDimension(value));

	function handleAmountInput(e: Event): void {
		const amount = Number((e.currentTarget as HTMLInputElement).value);
		const unit = parsed?.unit ?? 'in';
		if (Number.isFinite(amount)) onchange(serializeDimension(amount, unit));
	}

	function handleUnitChange(e: Event): void {
		const unit = (e.currentTarget as HTMLSelectElement).value as DimensionUnit;
		const amount = parsed?.amount ?? 0;
		onchange(serializeDimension(amount, unit));
	}

	function handleRawInput(e: Event): void {
		onchange((e.currentTarget as HTMLInputElement).value);
	}
</script>

{#if parsed}
	<div class="flex items-center gap-1">
		<input
			{id}
			type="number"
			step="0.01"
			class="w-24 rounded-md border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100"
			value={parsed.amount}
			oninput={handleAmountInput}
		/>
		<select
			aria-label="Unit"
			class="rounded-md border border-neutral-300 bg-white px-1.5 py-1.5 text-sm text-neutral-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100"
			value={parsed.unit}
			onchange={handleUnitChange}
		>
			{#each DIMENSION_UNITS as unit (unit)}
				<option value={unit}>{unit}</option>
			{/each}
		</select>
	</div>
{:else}
	<input
		{id}
		type="text"
		class="w-full rounded-md border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100 dark:placeholder:text-neutral-600"
		placeholder="e.g. 0.7in"
		{value}
		oninput={handleRawInput}
	/>
{/if}

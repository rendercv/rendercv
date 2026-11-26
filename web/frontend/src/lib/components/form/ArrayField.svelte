<script lang="ts">
	import type { FieldDescriptor } from '$lib/schema/types';
	import DynamicField from './DynamicField.svelte';
	import { MARKDOWN_FORMAT_HINT } from '$lib/form/markdownHint';

	/**
	 * `+ Add` / per-item delete / drag-handle reorder for a schema-described
	 * array field (native HTML drag, no dnd library — see the phase task).
	 * Up/down buttons duplicate the drag handle's job so reordering stays
	 * keyboard-reachable.
	 *
	 * Why a whole-array `onchange` instead of per-op callbacks: this
	 * component renders generic header-level arrays (`social_networks`,
	 * `custom_connections`) whose backend write is a single `set` replacing
	 * the whole array — unlike `cv.sections` entries/highlights, which get
	 * dedicated `insert`/`delete`/`move` ops from `SectionsEditor` +
	 * `sectionsActions.ts` because those are the ops the phase task calls
	 * out as needing exact op-level tests.
	 */
	let {
		descriptor,
		values,
		onchange,
		path,
		overrideInfo
	}: {
		descriptor: FieldDescriptor;
		values: unknown[];
		onchange: (values: unknown[]) => void;
		/** See `FieldRow`'s doc comment: an array field is treated as one leaf for the override overlay (the whole array resets together). */
		path?: import('$lib/form/patchOps').PathSegment[];
		overrideInfo?: import('$lib/form/effectiveValue').OverrideInfo;
	} = $props();

	let isOverridden = $derived(overrideInfo && path ? overrideInfo.isOverridden(path) : true);
	let showsResetAffordance = $derived(Boolean(overrideInfo && path && isOverridden));

	function reset(): void {
		if (overrideInfo && path) overrideInfo.onReset(path);
	}

	let itemDescriptor: FieldDescriptor = $derived(
		descriptor.items ?? { key: descriptor.key, label: '', required: false, nullable: true, kind: 'string' }
	);

	function defaultItem(): unknown {
		if (itemDescriptor.kind === 'object') return {};
		if (itemDescriptor.kind === 'array') return [];
		return '';
	}

	/** Commits a whole new array value -- see `FieldRow`'s `commit` doc comment for why `setPath` bypasses the usual `onchange` bubble. */
	function commit(next: unknown[]): void {
		if (overrideInfo && path) overrideInfo.setPath(path, next);
		else onchange(next);
	}

	function addItem(): void {
		commit([...values, defaultItem()]);
	}

	function deleteItem(index: number): void {
		commit(values.filter((_, i) => i !== index));
	}

	function moveItem(from: number, to: number): void {
		if (to < 0 || to >= values.length || from === to) return;
		const next = [...values];
		const [moved] = next.splice(from, 1);
		next.splice(to, 0, moved);
		commit(next);
	}

	function itemChange(index: number, itemValue: unknown): void {
		const next = [...values];
		next[index] = itemValue;
		commit(next);
	}

	let dragIndex = $state<number | null>(null);

	const buttonClass =
		'grid h-6 w-6 place-items-center rounded text-neutral-500 hover:bg-neutral-100 disabled:opacity-30 dark:text-neutral-400 dark:hover:bg-[var(--surface-card)]';
</script>

<div class="flex flex-col gap-2 border-b border-neutral-100 py-2 last:border-b-0 dark:border-[var(--border-subtle)]">
	<div class="flex items-center justify-between">
		<span class="flex items-center gap-1">
			<span
				class="text-sm font-medium"
				class:text-neutral-700={isOverridden}
				class:dark:text-neutral-300={isOverridden}
				class:italic={!isOverridden}
				class:text-neutral-400={!isOverridden}
				class:dark:text-neutral-400={!isOverridden}
			>
				{descriptor.label}
			</span>
			{#if showsResetAffordance}
				<button
					type="button"
					class="grid h-5 w-5 shrink-0 place-items-center rounded text-purple-600 hover:bg-purple-50 dark:text-purple-400 dark:hover:bg-purple-950"
					aria-label={`Reset ${descriptor.label} to the theme default`}
					title="Reset to default"
					onclick={reset}
				>
					↺
				</button>
			{/if}
		</span>
		<button
			type="button"
			class="text-sm font-medium text-purple-600 hover:underline dark:text-purple-400"
			onclick={addItem}
		>
			+ Add
		</button>
	</div>

	{#if itemDescriptor.kind === 'markdown'}
		<!-- Once for the whole list: every item is the same kind of field, and
		     repeating this under each bullet would bury the content. -->
		<p class="text-xs text-neutral-400 dark:text-neutral-400">{MARKDOWN_FORMAT_HINT}</p>
	{/if}

	{#if values.length === 0}
		<p class="text-xs text-neutral-400 dark:text-neutral-400">None yet.</p>
	{/if}

	<ul class="flex flex-col gap-2">
		{#each values as item, i (i)}
			<li
				class="flex items-start gap-2 rounded-md border border-neutral-200 p-2 dark:border-[var(--border-subtle)]"
				draggable="true"
				ondragstart={() => (dragIndex = i)}
				ondragover={(e) => e.preventDefault()}
				ondrop={() => {
					if (dragIndex !== null) moveItem(dragIndex, i);
					dragIndex = null;
				}}
			>
				<span
					class="cursor-grab select-none pt-1.5 text-neutral-400 dark:text-neutral-600"
					aria-hidden="true"
					title="Drag to reorder"
				>
					⠿
				</span>
				<div class="min-w-0 flex-1">
					<DynamicField
						descriptor={{ ...itemDescriptor, label: itemDescriptor.label || `${descriptor.label} ${i + 1}` }}
						hideFormatHint
						value={item}
						onchange={(v) => itemChange(i, v)}
					/>
				</div>
				<div class="flex flex-col gap-0.5" role="group" aria-label={`Reorder ${descriptor.label} item ${i + 1}`}>
					<button
						type="button"
						class={buttonClass}
						aria-label={`Move item ${i + 1} up`}
						disabled={i === 0}
						onclick={() => moveItem(i, i - 1)}
					>
						↑
					</button>
					<button
						type="button"
						class={buttonClass}
						aria-label={`Move item ${i + 1} down`}
						disabled={i === values.length - 1}
						onclick={() => moveItem(i, i + 1)}
					>
						↓
					</button>
					<button
						type="button"
						class={buttonClass}
						aria-label={`Delete item ${i + 1}`}
						onclick={() => deleteItem(i)}
					>
						✕
					</button>
				</div>
			</li>
		{/each}
	</ul>
</div>

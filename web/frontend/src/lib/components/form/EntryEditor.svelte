<script lang="ts">
	import type { EntryTypeName } from '$lib/schema/cvSchema';
	import type { FieldDescriptor } from '$lib/schema/types';
	import type { ValidationError } from '$lib/api/validate';
	import type { PatchOp, PathSegment } from '$lib/form/patchOps';
	import {
		buildAddHighlightOp,
		buildDeleteHighlightOp,
		buildMoveHighlightOp,
		buildSetEntryFieldOp,
		buildSetEntryValueOp,
		buildSetHighlightOp
	} from '$lib/form/sectionsActions';
	import { errorsUnderPath } from '$lib/form/errorMapping';
	import DynamicField from './DynamicField.svelte';
	import FieldRow from './FieldRow.svelte';

	/**
	 * Renders one `cv.sections` entry's fields, dispatched from its inferred
	 * type (see `cvSchema.inferEntryType`). `highlights` gets its own
	 * add/delete/reorder/edit UI wired to dedicated ops (not the generic
	 * whole-array `ArrayField`), because the phase task calls out exact
	 * `insert`/`move`/`set` op shapes for it.
	 *
	 * The collapse chevron lives here (not in `SectionsEditor`) because the
	 * reference places it beside the entry's *first field's* label, not in a
	 * standalone header bar -- collapsing swaps that same row for the
	 * one-line summary, so expanded/collapsed read as the same row.
	 */
	let {
		sectionTitle,
		entryIndex,
		type,
		fields,
		value,
		errors,
		submitOp,
		collapsed = false,
		onToggleCollapse,
		summaryText = ''
	}: {
		sectionTitle: string;
		entryIndex: number;
		type: EntryTypeName;
		fields: FieldDescriptor[];
		value: unknown;
		errors: ValidationError[];
		submitOp: (op: PatchOp) => void;
		collapsed?: boolean;
		onToggleCollapse?: () => void;
		summaryText?: string;
	} = $props();

	const entryPath: PathSegment[] = $derived(['cv', 'sections', sectionTitle, entryIndex]);
	const orderedFields = $derived(fields.filter((f) => f.key !== 'highlights'));
	const firstField = $derived(orderedFields[0]);
	const restFields = $derived(orderedFields.slice(1));
	const highlightsField = $derived(fields.find((f) => f.key === 'highlights'));
	const objectValue = $derived((value && typeof value === 'object' ? value : {}) as Record<string, unknown>);
	const highlights = $derived((objectValue.highlights as string[] | undefined) ?? []);

	const textEntryDescriptor: FieldDescriptor = {
		key: 'text',
		label: 'Text',
		required: true,
		nullable: false,
		kind: 'markdown'
	};

	const bodyId = $derived(`entry-body-${sectionTitle.replace(/[^a-zA-Z0-9]+/g, '-')}-${entryIndex}`);

	function fieldErrors(key: string): ValidationError[] {
		return errorsUnderPath(errors, [...entryPath, key]);
	}

	function setField(key: string, fieldValue: unknown): void {
		submitOp(buildSetEntryFieldOp(sectionTitle, entryIndex, key, fieldValue));
	}

	function setTextEntry(entryValue: unknown): void {
		submitOp(buildSetEntryValueOp(sectionTitle, entryIndex, entryValue));
	}

	function addHighlight(): void {
		submitOp(buildAddHighlightOp(sectionTitle, entryIndex, highlights.length));
	}

	function deleteHighlight(index: number): void {
		submitOp(buildDeleteHighlightOp(sectionTitle, entryIndex, index));
	}

	function moveHighlight(from: number, to: number): void {
		if (to < 0 || to >= highlights.length) return;
		submitOp(buildMoveHighlightOp(sectionTitle, entryIndex, from, to));
	}

	function setHighlight(index: number, highlightValue: string): void {
		submitOp(buildSetHighlightOp(sectionTitle, entryIndex, index, highlightValue));
	}

	const iconButtonClass =
		'grid h-6 w-6 shrink-0 place-items-center rounded text-neutral-400 opacity-0 group-hover/highlight:opacity-100 hover:bg-neutral-100 focus-visible:opacity-100 disabled:opacity-30 dark:text-neutral-500 dark:hover:bg-[var(--surface-card)]';
</script>

<div class="flex flex-col gap-1">
	<div class="flex items-start gap-1.5">
		<button
			type="button"
			class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded text-neutral-400 hover:bg-neutral-100 hover:text-neutral-600 dark:text-neutral-500 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-300"
			aria-expanded={!collapsed}
			aria-controls={bodyId}
			aria-label={collapsed ? 'Expand entry' : 'Collapse entry'}
			title={collapsed ? 'Expand' : 'Collapse'}
			onclick={() => onToggleCollapse?.()}
		>
			<span aria-hidden="true">{collapsed ? '›' : '⌄'}</span>
		</button>

		<div class="min-w-0 flex-1">
			{#if collapsed}
				<p class="truncate py-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-300">
					{summaryText}
				</p>
			{:else if type === 'TextEntry'}
				<FieldRow descriptor={textEntryDescriptor} value={typeof value === 'string' ? value : ''} onchange={setTextEntry} />
			{:else if firstField}
				<DynamicField
					descriptor={firstField}
					value={objectValue[firstField.key]}
					errors={fieldErrors(firstField.key)}
					onchange={(fieldValue) => setField(firstField.key, fieldValue)}
				/>
			{/if}
		</div>
	</div>

	{#if !collapsed}
		<div id={bodyId} class="flex flex-col gap-1 pl-[1.625rem]">
			{#each restFields as field (field.key)}
				<DynamicField
					descriptor={field}
					value={objectValue[field.key]}
					errors={fieldErrors(field.key)}
					onchange={(fieldValue) => setField(field.key, fieldValue)}
				/>
			{/each}

			{#if highlightsField}
				<div class="flex flex-col gap-1 border-t border-neutral-100 pt-2 dark:border-[var(--border-subtle)]">
					<div class="flex items-center justify-between">
						<span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">{highlightsField.label}</span>
						<button
							type="button"
							class="text-sm font-medium text-purple-600 hover:underline dark:text-purple-400"
							onclick={addHighlight}
						>
							+ Add
						</button>
					</div>
					{#if highlights.length === 0}
						<p class="text-xs text-neutral-400 dark:text-neutral-400">None yet.</p>
					{/if}
					<ul class="flex flex-col">
						{#each highlights as highlight, hi (hi)}
							<li class="group/highlight flex items-start gap-2 border-b border-neutral-100 py-1.5 last:border-b-0 dark:border-[var(--border-subtle)]">
								<textarea
									rows="1"
									aria-label={`Highlight ${hi + 1}`}
									placeholder={highlightsField.placeholder}
									class="w-full resize-none border-0 bg-transparent p-0 text-sm text-neutral-800 placeholder:text-neutral-400 focus:outline-none focus:ring-0 dark:text-neutral-100 dark:placeholder:text-neutral-600"
									value={highlight}
									oninput={(e) => setHighlight(hi, (e.currentTarget as HTMLTextAreaElement).value)}
								></textarea>
								<div class="flex shrink-0 gap-0.5">
									<button
										type="button"
										class={iconButtonClass}
										aria-label={`Move highlight ${hi + 1} up`}
										disabled={hi === 0}
										onclick={() => moveHighlight(hi, hi - 1)}
									>
										↑
									</button>
									<button
										type="button"
										class={iconButtonClass}
										aria-label={`Move highlight ${hi + 1} down`}
										disabled={hi === highlights.length - 1}
										onclick={() => moveHighlight(hi, hi + 1)}
									>
										↓
									</button>
									<button
										type="button"
										class={iconButtonClass}
										aria-label={`Delete highlight ${hi + 1}`}
										onclick={() => deleteHighlight(hi)}
									>
										✕
									</button>
								</div>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
	{/if}
</div>

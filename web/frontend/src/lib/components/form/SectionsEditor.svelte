<script lang="ts">
	import type { JsonSchemaDocument } from '$lib/schema/types';
	import {
		entrySummaryText,
		getEntryTypeDescriptors,
		inferEntryType,
		type EntryTypeName
	} from '$lib/schema/cvSchema';
	import type { ValidationError } from '$lib/api/validate';
	import type { PatchOp } from '$lib/form/patchOps';
	import { addEntryLabel, displaySectionTitle } from '$lib/form/sectionDisplay';
	import {
		buildAddEntryOp,
		buildAddSectionOp,
		buildDeleteEntryOp,
		buildDeleteSectionOp,
		buildMoveEntryOp,
		buildRenameSectionOp
	} from '$lib/form/sectionsActions';
	import EntryEditor from './EntryEditor.svelte';
	import EntryTypePicker from './EntryTypePicker.svelte';

	/**
	 * `cv.sections` is a mapping of arbitrary titles to lists of one of 9
	 * polymorphic entry types — the one part of the CV schema that isn't a
	 * plain object/array/scalar tree `DynamicField` can walk generically, so
	 * it gets its own component (see the phase task).
	 */
	let {
		schema,
		sections,
		errors,
		submitOp
	}: {
		schema: JsonSchemaDocument;
		sections: Record<string, unknown[]>;
		errors: ValidationError[];
		submitOp: (op: PatchOp) => void;
	} = $props();

	let entryTypeDescriptors = $derived(getEntryTypeDescriptors(schema));
	function fieldsFor(type: EntryTypeName) {
		return entryTypeDescriptors.find((d) => d.type === type)?.fields ?? [];
	}

	let sectionTitles = $derived(Object.keys(sections ?? {}));
	let newSectionTitle = $state('');
	/** Draft rename text per section row (keyed by row index, not title, so an in-progress rename doesn't remount the row). */
	let titleDrafts = $state<Record<number, string>>({});
	/** Which section row (by index) is currently showing its title as an editable input instead of a heading. */
	let editingTitleIndex = $state<number | null>(null);
	/** Collapsed state per entry, keyed by `"<section title>::<entry index>"` -- purely a view concern, not part of the document. */
	let collapsedEntries = $state<Record<string, boolean>>({});
	let dragEntry = $state<{ title: string; index: number } | null>(null);

	function draftFor(index: number, title: string): string {
		return titleDrafts[index] ?? title;
	}

	function onTitleInput(index: number, next: string): void {
		titleDrafts = { ...titleDrafts, [index]: next };
	}

	function startEditingTitle(index: number, title: string): void {
		titleDrafts = { ...titleDrafts, [index]: title };
		editingTitleIndex = index;
	}

	function commitTitle(index: number, fromTitle: string): void {
		const draft = titleDrafts[index];
		if (draft !== undefined) {
			const trimmed = draft.trim();
			if (trimmed && trimmed !== fromTitle && !sectionTitles.includes(trimmed)) {
				submitOp(buildRenameSectionOp(sections, fromTitle, trimmed));
			}
		}
		const rest = { ...titleDrafts };
		delete rest[index];
		titleDrafts = rest;
		editingTitleIndex = null;
	}

	function addSection(): void {
		const title = newSectionTitle.trim();
		if (!title || sectionTitles.includes(title)) return;
		submitOp(buildAddSectionOp(title));
		newSectionTitle = '';
	}

	function deleteSection(title: string): void {
		submitOp(buildDeleteSectionOp(title));
	}

	function sectionType(title: string): EntryTypeName | null {
		const entries = sections[title] ?? [];
		return entries.length > 0 ? inferEntryType(entries[0]) : null;
	}

	function addEntry(title: string, type: EntryTypeName): void {
		const entries = sections[title] ?? [];
		submitOp(buildAddEntryOp(title, entries.length, type, fieldsFor(type)));
	}

	function deleteEntry(title: string, index: number): void {
		submitOp(buildDeleteEntryOp(title, index));
	}

	function moveEntry(title: string, from: number, to: number): void {
		const entries = sections[title] ?? [];
		if (to < 0 || to >= entries.length) return;
		submitOp(buildMoveEntryOp(title, from, to));
	}

	function entryKey(title: string, index: number): string {
		return `${title}::${index}`;
	}

	function isCollapsed(title: string, index: number): boolean {
		return collapsedEntries[entryKey(title, index)] ?? false;
	}

	function toggleCollapsed(title: string, index: number): void {
		const key = entryKey(title, index);
		collapsedEntries = { ...collapsedEntries, [key]: !isCollapsed(title, index) };
	}

	function onDragHandleKeydown(e: KeyboardEvent, title: string, index: number): void {
		if (e.key === 'ArrowUp') {
			e.preventDefault();
			moveEntry(title, index, index - 1);
		} else if (e.key === 'ArrowDown') {
			e.preventDefault();
			moveEntry(title, index, index + 1);
		}
	}

	const inputClass =
		'w-full rounded-md border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100';
</script>

<div class="flex flex-col gap-4">
	{#each sectionTitles as title, si (si)}
		{@const entries = sections[title] ?? []}
		{@const type = sectionType(title)}
		<section class="flex flex-col gap-2" aria-label={`Section: ${title}`}>
			<div class="group/heading flex items-center gap-2 border-b-2 border-neutral-200 pb-1.5 dark:border-[var(--border-subtle)]">
				{#if editingTitleIndex === si}
					<label class="sr-only" for={`section-title-${si}`}>Section title</label>
					<!-- svelte-ignore a11y_autofocus -- deliberate: this input only exists while the user is actively editing this section's title (click-to-edit), so moving focus into it here is expected, not a surprise page-load autofocus. -->
					<input
						id={`section-title-${si}`}
						class={`${inputClass} flex-1 text-lg font-bold`}
						value={draftFor(si, title)}
						autofocus
						oninput={(e) => onTitleInput(si, (e.currentTarget as HTMLInputElement).value)}
						onblur={() => commitTitle(si, title)}
						onkeydown={(e) => {
							if (e.key === 'Enter') (e.currentTarget as HTMLInputElement).blur();
							if (e.key === 'Escape') {
								const rest = { ...titleDrafts };
								delete rest[si];
								titleDrafts = rest;
								editingTitleIndex = null;
							}
						}}
					/>
				{:else}
					<h2 class="min-w-0 flex-1 truncate text-lg font-bold">
						<button
							type="button"
							class="w-full truncate text-left text-neutral-900 hover:text-purple-600 dark:text-neutral-100 dark:hover:text-purple-400"
							aria-label={`Edit section title: ${displaySectionTitle(title)}`}
							onclick={() => startEditingTitle(si, title)}
						>
							{displaySectionTitle(title)}
						</button>
					</h2>
				{/if}
				<button
					type="button"
					class="shrink-0 rounded px-1.5 py-1 text-neutral-400 opacity-0 hover:bg-neutral-100 hover:text-neutral-700 focus-visible:opacity-100 group-hover/heading:opacity-100 dark:text-neutral-500 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-200"
					aria-label={`Delete section ${displaySectionTitle(title)}`}
					title="Delete section"
					onclick={() => deleteSection(title)}
				>
					⋯
				</button>
			</div>

			{#if entries.length === 0}
				<EntryTypePicker descriptors={entryTypeDescriptors} onSelect={(t) => addEntry(title, t)} />
			{:else}
				<ul class="flex flex-col gap-1">
					{#each entries as entry, ei (ei)}
						{@const entryType = inferEntryType(entry) ?? type ?? 'TextEntry'}
						<li
							class="group/entry relative flex items-start gap-1 rounded-md py-1 pl-6 pr-7 hover:bg-neutral-50 dark:hover:bg-neutral-900/40"
							class:opacity-60={dragEntry !== null && dragEntry.title === title && dragEntry.index === ei}
							ondragover={(e) => e.preventDefault()}
							ondrop={() => {
								if (dragEntry && dragEntry.title === title) moveEntry(title, dragEntry.index, ei);
								dragEntry = null;
							}}
						>
							<button
								type="button"
								class="absolute left-0 top-1.5 grid h-6 w-6 cursor-grab place-items-center rounded text-neutral-400 opacity-0 hover:bg-neutral-100 focus-visible:opacity-100 group-hover/entry:opacity-100 active:cursor-grabbing dark:text-neutral-500 dark:hover:bg-[var(--surface-card)]"
								aria-label={`Reorder entry ${ei + 1} of ${entries.length} (drag, or press Arrow Up / Arrow Down while focused)`}
								title="Drag to reorder, or use Arrow Up / Arrow Down"
								draggable="true"
								ondragstart={() => (dragEntry = { title, index: ei })}
								ondragend={() => (dragEntry = null)}
								onkeydown={(e) => onDragHandleKeydown(e, title, ei)}
							>
								<span aria-hidden="true">⋮⋮</span>
							</button>

							<div class="min-w-0 flex-1">
								<EntryEditor
									sectionTitle={title}
									entryIndex={ei}
									type={entryType}
									fields={fieldsFor(entryType)}
									value={entry}
									{errors}
									{submitOp}
									collapsed={isCollapsed(title, ei)}
									onToggleCollapse={() => toggleCollapsed(title, ei)}
									summaryText={entrySummaryText(entryType, entry)}
								/>
							</div>

							<button
								type="button"
								class="absolute right-0 top-1.5 grid h-6 w-6 place-items-center rounded text-neutral-400 opacity-0 hover:bg-red-50 hover:text-red-600 focus-visible:opacity-100 group-hover/entry:opacity-100 dark:text-neutral-500 dark:hover:bg-red-950 dark:hover:text-red-400"
								aria-label={`Remove entry ${ei + 1}`}
								title="Remove entry"
								onclick={() => deleteEntry(title, ei)}
							>
								<span aria-hidden="true">✕</span>
							</button>
						</li>
					{/each}
				</ul>
				<button
					type="button"
					class="mt-1 w-full rounded-md border border-dashed border-neutral-300 py-1.5 text-sm font-medium text-neutral-500 hover:border-purple-400 hover:text-purple-600 dark:border-[var(--border-subtle)] dark:text-neutral-400 dark:hover:border-purple-500 dark:hover:text-purple-400"
					onclick={() => addEntry(title, type ?? 'TextEntry')}
				>
					+ Add {addEntryLabel(title)} entry
				</button>
			{/if}
		</section>
	{/each}

	<div class="flex items-center gap-2">
		<label class="sr-only" for="new-section-title">New section title</label>
		<input
			id="new-section-title"
			class={inputClass}
			placeholder="New section title (e.g. Experience)"
			bind:value={newSectionTitle}
			onkeydown={(e) => {
				if (e.key === 'Enter') addSection();
			}}
		/>
		<button
			type="button"
			class="whitespace-nowrap rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 dark:border-[var(--border-subtle)] dark:text-neutral-200 dark:hover:bg-[var(--surface-card)]"
			onclick={addSection}
		>
			+ Add section
		</button>
	</div>
</div>

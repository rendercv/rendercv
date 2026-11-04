<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { documents } from '$lib/stores/documents';
	import { fetchSchema } from '$lib/schema/client';
	import { getCvHeaderFields } from '$lib/schema/cvSchema';
	import type { JsonSchemaDocument } from '$lib/schema/types';
	import { createFormSync } from '$lib/form/formSync';
	import { buildSetCvFieldOp } from '$lib/form/cvFieldActions';
	import { errorsAtPath } from '$lib/form/errorMapping';
	import type { ValidationError } from '$lib/api/validate';
	import DynamicField from './DynamicField.svelte';
	import SectionsEditor from './SectionsEditor.svelte';

	/**
	 * The CV tab's form view: schema-driven header fields (name, headline,
	 * contact info, social networks, custom connections) plus the dedicated
	 * `SectionsEditor` for `cv.sections`. Two-way sync with the YAML view
	 * goes through `createFormSync`, which reads/writes the same
	 * `documents` store the YAML editor does (see the ui-implementation
	 * skill's "one store, two views" rule) — this component owns no CV data
	 * of its own.
	 */
	let { errors = [] }: { errors?: ValidationError[] } = $props();

	const sync = createFormSync(documents);
	const syncState = sync.state;

	let schema = $state<JsonSchemaDocument | null>(null);
	let schemaError = $state<string | null>(null);

	onMount(() => {
		void sync.activate();
		fetchSchema()
			.then((loaded) => {
				schema = loaded;
			})
			.catch((e: unknown) => {
				schemaError = e instanceof Error ? e.message : 'Could not load the form schema.';
			});
	});

	onDestroy(() => {
		sync.deactivate();
		sync.destroy();
	});

	let headerFields = $derived(schema ? getCvHeaderFields(schema) : []);
	let cvData = $derived((($syncState.data?.cv as Record<string, unknown> | undefined) ?? {}) as Record<
		string,
		unknown
	>);
	let sections = $derived((cvData.sections ?? {}) as Record<string, unknown[]>);

	function setHeaderField(key: string, value: unknown): void {
		sync.submitOp(buildSetCvFieldOp(key, value));
	}
</script>

<div class="relative flex h-full flex-col gap-4 overflow-auto p-1">
	{#if $syncState.toast}
		<div
			role="alert"
			class="flex items-center justify-between gap-3 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200"
		>
			<span>Couldn't save that change: {$syncState.toast}</span>
			<button type="button" class="shrink-0 font-medium underline" onclick={() => sync.dismissToast()}>
				Dismiss
			</button>
		</div>
	{/if}

	{#if $syncState.status === 'error'}
		<p class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
			This document has a YAML error the form can't display. Switch to YAML to fix it, or see the
			error bar below.
		</p>
	{:else if !schema}
		<p class="text-sm text-neutral-500 dark:text-neutral-400">{schemaError ?? 'Loading form…'}</p>
	{:else}
		<section
			aria-label="CV header fields"
			class="rounded-md border border-neutral-200 px-3 dark:border-[var(--border-subtle)]"
		>
			{#each headerFields as field (field.key)}
				<DynamicField
					descriptor={field}
					value={cvData[field.key]}
					errors={errorsAtPath(errors, ['cv', field.key])}
					onchange={(value) => setHeaderField(field.key, value)}
				/>
			{/each}
		</section>

		<SectionsEditor {schema} {sections} {errors} submitOp={sync.submitOp} />
	{/if}
</div>

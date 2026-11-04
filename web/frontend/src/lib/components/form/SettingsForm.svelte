<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { documents } from '$lib/stores/documents';
	import { fetchSchema } from '$lib/schema/client';
	import { resolveDefFields } from '$lib/schema/resolver';
	import { createFormSync } from '$lib/form/formSync';
	import { buildSetFieldOp } from '$lib/form/documentActions';
	import { errorsAtPath } from '$lib/form/errorMapping';
	import type { ValidationError } from '$lib/api/validate';
	import type { JsonSchemaDocument } from '$lib/schema/types';
	import DynamicField from './DynamicField.svelte';

	/**
	 * The Settings tab's form view: `current_date`, `bold_keywords`,
	 * `pdf_title` -- `render_command` is deliberately never surfaced (it's
	 * server-internal render-time overrides, not something the CV author
	 * edits; see the phase task).
	 */
	let { errors = [] }: { errors?: ValidationError[] } = $props();

	const sync = createFormSync(documents, { documentKey: 'settings' });
	const syncState = sync.state;

	let schema = $state<JsonSchemaDocument | null>(null);
	let schemaError = $state<string | null>(null);

	const HIDDEN_KEYS = new Set(['render_command']);

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

	let fields = $derived(
		schema ? resolveDefFields(schema, 'Settings').filter((f) => !HIDDEN_KEYS.has(f.key)) : []
	);
	let settingsData = $derived(
		(($syncState.data?.settings as Record<string, unknown> | undefined) ?? {}) as Record<string, unknown>
	);

	function setField(key: string, value: unknown): void {
		sync.submitOp(buildSetFieldOp('settings', [key], value));
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
			This document has a YAML error the form can't display. Switch to YAML to fix it.
		</p>
	{:else if !schema}
		<p class="text-sm text-neutral-500 dark:text-neutral-400">{schemaError ?? 'Loading form…'}</p>
	{:else}
		<section
			aria-label="Settings fields"
			class="rounded-md border border-neutral-200 px-3 dark:border-[var(--border-subtle)]"
		>
			{#each fields as field (field.key)}
				<DynamicField
					descriptor={field}
					value={settingsData[field.key]}
					errors={errorsAtPath(errors, ['settings', field.key])}
					onchange={(value) => setField(field.key, value)}
				/>
			{/each}
		</section>
	{/if}
</div>

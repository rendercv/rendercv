<script lang="ts">
	import { onMount } from 'svelte';
	import type { Readable } from 'svelte/store';
	import { fetchSchema } from '$lib/schema/client';
	import { fetchThemes, type ThemeInfo } from '$lib/api/themes';
	import { getVariantFields } from '$lib/schema/discriminatedUnion';
	import { deepMerge, isPathOverridden, type OverrideInfo } from '$lib/form/effectiveValue';
	import { buildEnsurePathOps } from '$lib/form/documentActions';
	import { errorsAtPath } from '$lib/form/errorMapping';
	import type { ValidationError } from '$lib/api/validate';
	import type { FormSyncState, FormSyncController } from '$lib/form/formSync';
	import type { JsonSchemaDocument } from '$lib/schema/types';
	import type { PathSegment } from '$lib/form/patchOps';
	import DynamicField from './DynamicField.svelte';

	/**
	 * The Design tab's form view. Per the approved semantics (phase 3 task):
	 * the design YAML stays minimal (just `theme` plus explicit overrides);
	 * this form displays EFFECTIVE values — the current theme's defaults
	 * (from `/api/themes`) deep-merged with whatever the parsed YAML
	 * explicitly sets — with muted styling for inherited defaults and a "↺"
	 * reset affordance on anything explicitly overridden.
	 *
	 * Why `syncState`/`submitOp` are props, not an owned `createFormSync`
	 * instance: the tab-bar `ThemeSwitcher` (visible on every tab, not just
	 * this form) needs the same design document sync — `EditorPane` owns one
	 * shared controller so both consumers see the same state and never race
	 * each other with independent parse/patch cycles.
	 */
	let {
		syncState,
		submitOp,
		errors = []
	}: {
		syncState: Readable<FormSyncState>;
		submitOp: FormSyncController['submitOp'];
		errors?: ValidationError[];
	} = $props();

	let schema = $state<JsonSchemaDocument | null>(null);
	let themes = $state<ThemeInfo[] | null>(null);
	let loadError = $state<string | null>(null);

	onMount(() => {
		Promise.all([fetchSchema(), fetchThemes()])
			.then(([loadedSchema, loadedThemes]) => {
				schema = loadedSchema;
				themes = loadedThemes;
			})
			.catch((e: unknown) => {
				loadError = e instanceof Error ? e.message : 'Could not load the design form.';
			});
	});

	// `syncState.data` is the whole parsed document (`{design: {...}}`, or
	// `{}` for a still-blank document) -- see `ParseResponse`'s contract.
	let parsedTree = $derived($syncState.data ?? {});
	let designOverrides = $derived(
		(parsedTree as Record<string, unknown>).design as Record<string, unknown> | undefined
	);
	let currentTheme = $derived((designOverrides?.theme as string | undefined) ?? 'classic');
	let themeDefaults = $derived(
		themes?.find((t) => t.name === currentTheme)?.design_defaults ?? {}
	);
	let effectiveDesign = $derived(
		deepMerge(themeDefaults, designOverrides ?? {}) as Record<string, unknown>
	);
	let fields = $derived(schema ? getVariantFields(schema, 'BuiltInDesign', currentTheme, ['theme']) : []);

	const overrideInfo: OverrideInfo = {
		isOverridden: (path: PathSegment[]) => isPathOverridden(parsedTree, path),
		onReset: (path: PathSegment[]) => submitOp({ op: 'delete', path }),
		setPath: (path: PathSegment[], value: unknown) => {
			// A field several levels deep can be the first-ever write to an
			// otherwise untouched design document -- create any missing
			// intermediate container first (see `buildEnsurePathOps`'s doc
			// comment; the top key is seeded with the current theme, since a
			// `design:` mapping without `theme` fails discrimination), then
			// the leaf `set` itself, as one atomic patch.
			for (const ensureOp of buildEnsurePathOps(parsedTree, path, { theme: currentTheme })) {
				submitOp(ensureOp);
			}
			submitOp({ op: 'set', path, value });
		}
	};
</script>

<div class="relative flex h-full flex-col gap-4 overflow-auto p-1">
	{#if $syncState.toast}
		<div
			role="alert"
			class="flex items-center justify-between gap-3 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200"
		>
			<span>Couldn't save that change: {$syncState.toast}</span>
		</div>
	{/if}

	{#if $syncState.status === 'error'}
		<p class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
			This document has a YAML error the form can't display. Switch to YAML to fix it.
		</p>
	{:else if !schema || !themes}
		<p class="text-sm text-neutral-500 dark:text-neutral-400">{loadError ?? 'Loading form…'}</p>
	{:else}
		<section
			aria-label="Design theme"
			class="rounded-md border border-neutral-200 px-3 py-1 dark:border-[var(--border-subtle)]"
		>
			<div class="flex items-center justify-between py-2 text-sm">
				<span class="font-medium text-neutral-700 dark:text-neutral-300">Theme</span>
				<span class="font-medium text-neutral-900 dark:text-neutral-100">{currentTheme}</span>
			</div>
			<p class="pb-2 text-xs text-neutral-400 dark:text-neutral-400">
				Use the theme switcher in the tab bar above to change it.
			</p>
		</section>

		{#each fields as field (field.key)}
			<DynamicField
				descriptor={field}
				value={effectiveDesign[field.key]}
				errors={errorsAtPath(errors, ['design', field.key])}
				onchange={(v) => overrideInfo.setPath(['design', field.key], v)}
				path={['design', field.key]}
				{overrideInfo}
			/>
		{/each}
	{/if}
</div>

<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { documents } from '$lib/stores/documents';
	import { fetchSchema } from '$lib/schema/client';
	import { getVariantFields, listVariantNames } from '$lib/schema/discriminatedUnion';
	import { createFormSync } from '$lib/form/formSync';
	import { isPathOverridden, type OverrideInfo } from '$lib/form/effectiveValue';
	import { buildDiscriminatorSwitchOp, buildEnsurePathOps } from '$lib/form/documentActions';
	import { errorsAtPath } from '$lib/form/errorMapping';
	import { ENGLISH_MONTH_ABBREVIATIONS, ENGLISH_MONTH_NAMES } from '$lib/form/months';
	import type { ValidationError } from '$lib/api/validate';
	import type { FieldDescriptor, JsonSchemaDocument } from '$lib/schema/types';
	import type { PathSegment } from '$lib/form/patchOps';
	import DynamicField from './DynamicField.svelte';
	import StepperField from './StepperField.svelte';
	import MonthTable from './MonthTable.svelte';

	/**
	 * The Locale tab's form view: the `language` switcher (a discriminated
	 * union, same shape as `design.theme`), the label/translation fields
	 * (last_updated, month/months, year/years, present, phrases), and the
	 * two fixed 12-row MONTH NAMES / MONTH ABBREVIATIONS tables. Effective
	 * values overlay the current language variant's own schema defaults
	 * (each locale variant carries its own translated defaults — no
	 * `/api/themes`-equivalent endpoint needed here) with whatever the YAML
	 * explicitly sets.
	 */
	let { errors = [] }: { errors?: ValidationError[] } = $props();

	const sync = createFormSync(documents, { documentKey: 'locale' });
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

	let parsedTree = $derived($syncState.data ?? {});
	let localeOverrides = $derived(
		(parsedTree as Record<string, unknown>).locale as Record<string, unknown> | undefined
	);
	let currentLanguage = $derived((localeOverrides?.language as string | undefined) ?? 'english');
	let languageNames = $derived(schema ? listVariantNames(schema, 'Locale') : []);

	let allVariantFields = $derived(
		schema ? getVariantFields(schema, 'Locale', currentLanguage, ['language']) : []
	);
	let labelFields = $derived(
		allVariantFields.filter((f) => f.key !== 'month_names' && f.key !== 'month_abbreviations')
	);
	let monthNamesField = $derived(allVariantFields.find((f) => f.key === 'month_names'));
	let monthAbbreviationsField = $derived(allVariantFields.find((f) => f.key === 'month_abbreviations'));

	function defaultsOf(fields: FieldDescriptor[]): Record<string, unknown> {
		const result: Record<string, unknown> = {};
		for (const field of fields) result[field.key] = field.default;
		return result;
	}

	let effectiveLocale = $derived({
		...defaultsOf(allVariantFields),
		...(localeOverrides ?? {})
	} as Record<string, unknown>);

	let monthNamesValues = $derived((effectiveLocale.month_names as string[] | undefined) ?? []);
	let monthAbbreviationsValues = $derived(
		(effectiveLocale.month_abbreviations as string[] | undefined) ?? []
	);

	const overrideInfo: OverrideInfo = {
		isOverridden: (path: PathSegment[]) => isPathOverridden(parsedTree, path),
		onReset: (path: PathSegment[]) => sync.submitOp({ op: 'delete', path }),
		setPath: (path: PathSegment[], value: unknown) => {
			// See `DesignForm`'s identical comment: a field can be the
			// first-ever write to an otherwise untouched locale document, and
			// `locale:` needs `language` set for the same discriminator reason.
			for (const ensureOp of buildEnsurePathOps(parsedTree, path, { language: currentLanguage })) {
				sync.submitOp(ensureOp);
			}
			sync.submitOp({ op: 'set', path, value });
		}
	};

	function switchLanguage(language: string): void {
		sync.submitOp(buildDiscriminatorSwitchOp(get(documents).locale, 'locale', 'language', language));
	}

	function commitMonthArray(key: 'month_names' | 'month_abbreviations', index: number, value: string): void {
		const current = key === 'month_names' ? monthNamesValues : monthAbbreviationsValues;
		const next = [...current];
		next[index] = value;
		overrideInfo.setPath(['locale', key], next);
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
			aria-label="Locale language"
			class="rounded-md border border-neutral-200 px-3 py-1 dark:border-[var(--border-subtle)]"
		>
			<div class="flex items-center justify-between py-2">
				<label for="locale-language" class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
					Language
				</label>
				<StepperField
					id="locale-language"
					options={languageNames}
					value={currentLanguage}
					ariaLabel="Language"
					onchange={switchLanguage}
				/>
			</div>
		</section>

		<section
			aria-label="Locale labels"
			class="rounded-md border border-neutral-200 px-3 dark:border-[var(--border-subtle)]"
		>
			{#each labelFields as field (field.key)}
				<DynamicField
					descriptor={field}
					value={effectiveLocale[field.key]}
					errors={errorsAtPath(errors, ['locale', field.key])}
					onchange={(v) => overrideInfo.setPath(['locale', field.key], v)}
					path={['locale', field.key]}
					{overrideInfo}
				/>
			{/each}
		</section>

		{#if monthNamesField}
			<section
				aria-label="Month names"
				class="rounded-md border border-neutral-200 px-3 dark:border-[var(--border-subtle)]"
			>
				<MonthTable
					label="Month names"
					referenceLabels={ENGLISH_MONTH_NAMES}
					values={monthNamesValues}
					overridden={overrideInfo.isOverridden(['locale', 'month_names'])}
					onReset={() => overrideInfo.onReset(['locale', 'month_names'])}
					onChangeIndex={(index, value) => commitMonthArray('month_names', index, value)}
				/>
			</section>
		{/if}

		{#if monthAbbreviationsField}
			<section
				aria-label="Month abbreviations"
				class="rounded-md border border-neutral-200 px-3 dark:border-[var(--border-subtle)]"
			>
				<MonthTable
					label="Month abbreviations"
					referenceLabels={ENGLISH_MONTH_ABBREVIATIONS}
					values={monthAbbreviationsValues}
					overridden={overrideInfo.isOverridden(['locale', 'month_abbreviations'])}
					onReset={() => overrideInfo.onReset(['locale', 'month_abbreviations'])}
					onChangeIndex={(index, value) => commitMonthArray('month_abbreviations', index, value)}
				/>
			</section>
		{/if}
	{/if}
</div>

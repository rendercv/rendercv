<script lang="ts">
	import type { FieldDescriptor } from '$lib/schema/types';
	import type { ValidationError } from '$lib/api/validate';
	import type { PathSegment } from '$lib/form/patchOps';
	import type { OverrideInfo } from '$lib/form/effectiveValue';
	import SegmentedControl from './SegmentedControl.svelte';
	import StepperField from './StepperField.svelte';
	import ColorField from './ColorField.svelte';
	import DimensionField from './DimensionField.svelte';
	import { MARKDOWN_FORMAT_HINT } from '$lib/form/markdownHint';

	/**
	 * `SegmentedControl` fits without wrapping for a short enum (the
	 * reference's A4/US Letter picker); anything longer (font families, the
	 * 22 locale languages) gets `StepperField`'s cycle-plus-dropdown instead.
	 */
	const SEGMENTED_CONTROL_MAX_OPTIONS = 4;

	let {
		descriptor,
		value,
		errors = [],
		onchange,
		path,
		overrideInfo,
		hideFormatHint
	}: {
		descriptor: FieldDescriptor;
		value: unknown;
		errors?: ValidationError[];
		onchange: (value: unknown) => void;
		/**
		 * This field's full path from the document root (e.g.
		 * `['design', 'page', 'top_margin']`). Only meaningful together with
		 * `overrideInfo` — the design/locale forms' effective-value overlay
		 * (approved semantics, phase 3): omitted, this field never shows the
		 * muted/emphasized distinction or the reset affordance (the CV form's
		 * fields have no theme-style defaults to overlay).
		 */
		path?: PathSegment[];
		overrideInfo?: OverrideInfo;
		/**
		 * Set by `ArrayField` on its items: an array of markdown fields shows
		 * the formatting hint once, above the list, instead of repeating it
		 * under every bullet.
		 */
		hideFormatHint?: boolean;
	} = $props();

	const instanceId = Math.random().toString(36).slice(2, 8);
	let fieldId = $derived(`field-${descriptor.key}-${instanceId}`);

	/** Undefined `overrideInfo`/`path` means "no overlay in play" -- always show the normal (emphasized) style, no reset button. */
	let isOverridden = $derived(overrideInfo && path ? overrideInfo.isOverridden(path) : true);
	let showsResetAffordance = $derived(Boolean(overrideInfo && path && isOverridden));

	function reset(): void {
		if (overrideInfo && path) overrideInfo.onReset(path);
	}

	/**
	 * Commits a new value for this field. When `overrideInfo`/`path` are
	 * given (design/locale forms), this writes a precise per-leaf `set` op
	 * at this field's own absolute path instead of the normal `onchange`
	 * bubble — see `OverrideInfo.setPath`'s doc comment.
	 */
	function commit(next: unknown): void {
		if (overrideInfo && path) overrideInfo.setPath(path, next);
		else onchange(next);
	}

	function handleTextInput(e: Event): void {
		const target = e.currentTarget as HTMLInputElement | HTMLTextAreaElement;
		commit(target.value);
	}

	function handleNumberInput(e: Event): void {
		const target = e.currentTarget as HTMLInputElement;
		commit(target.value === '' ? null : Number(target.value));
	}

	function toggleBoolean(): void {
		commit(!value);
	}

	const inputClass =
		'w-full rounded-md border border-neutral-300 bg-white px-2 py-1.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)] dark:text-neutral-100 dark:placeholder:text-neutral-600';
</script>

<div
	class="flex flex-col gap-1 border-b border-neutral-100 py-2 last:border-b-0 dark:border-[var(--border-subtle)] sm:flex-row sm:items-start sm:gap-4"
>
	<div class="flex w-full shrink-0 items-center gap-1 sm:w-40">
		<label
			for={fieldId}
			class="pt-1.5 text-sm font-medium sm:pt-0"
			class:text-neutral-700={isOverridden}
			class:dark:text-neutral-300={isOverridden}
			class:italic={!isOverridden}
			class:text-neutral-400={!isOverridden}
			class:dark:text-neutral-400={!isOverridden}
		>
			{descriptor.label}
			{#if descriptor.required}
				<span class="text-red-500" aria-hidden="true"> *</span>
			{/if}
		</label>
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
	</div>

	<div class="flex min-w-0 flex-1 flex-col gap-1">
		{#if descriptor.kind === 'boolean'}
			<button
				type="button"
				id={fieldId}
				role="switch"
				aria-checked={Boolean(value)}
				aria-label={descriptor.label}
				class="relative h-5 w-9 rounded-full transition-colors"
				class:bg-purple-600={Boolean(value)}
				class:bg-neutral-300={!value}
				onclick={toggleBoolean}
			>
				<span
					class="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-[left]"
					style={`left: ${value ? '1.25rem' : '0.125rem'}`}
				></span>
			</button>
		{:else if descriptor.kind === 'enum' && (descriptor.enumValues?.length ?? 0) <= SEGMENTED_CONTROL_MAX_OPTIONS}
			<SegmentedControl
				id={fieldId}
				options={descriptor.enumValues ?? []}
				value={typeof value === 'string' ? value : (descriptor.enumValues?.[0] ?? '')}
				ariaLabel={descriptor.label}
				onchange={(option) => commit(option)}
			/>
		{:else if descriptor.kind === 'enum'}
			<StepperField
				id={fieldId}
				options={descriptor.enumValues ?? []}
				value={typeof value === 'string' ? value : (descriptor.enumValues?.[0] ?? '')}
				ariaLabel={descriptor.label}
				onchange={(option) => commit(option)}
			/>
		{:else if descriptor.kind === 'color'}
			<ColorField
				id={fieldId}
				value={typeof value === 'string' ? value : ''}
				placeholder={descriptor.placeholder}
				onchange={(v) => commit(v)}
			/>
		{:else if descriptor.kind === 'dimension'}
			<DimensionField id={fieldId} value={typeof value === 'string' ? value : ''} onchange={(v) => commit(v)} />
		{:else if descriptor.kind === 'markdown'}
			<textarea
				id={fieldId}
				rows="3"
				class={inputClass}
				placeholder={descriptor.placeholder}
				value={typeof value === 'string' ? value : ''}
				oninput={handleTextInput}
			></textarea>
		{:else if descriptor.kind === 'number'}
			<input
				id={fieldId}
				type="number"
				class={inputClass}
				placeholder={descriptor.placeholder}
				value={typeof value === 'number' ? value : ''}
				oninput={handleNumberInput}
			/>
		{:else}
			<input
				id={fieldId}
				type={descriptor.kind === 'url' ? 'url' : 'text'}
				class={inputClass}
				placeholder={descriptor.placeholder}
				value={typeof value === 'string' ? value : ''}
				oninput={handleTextInput}
			/>
		{/if}

		{#if descriptor.description}
			<p class="text-xs text-neutral-400 dark:text-neutral-400">{descriptor.description}</p>
		{/if}

		{#if descriptor.kind === 'markdown' && !hideFormatHint}
			<p class="text-xs text-neutral-400 dark:text-neutral-400">{MARKDOWN_FORMAT_HINT}</p>
		{/if}

		{#if errors.length > 0}
			<p role="alert" class="text-xs font-medium text-red-600 dark:text-red-400">
				{errors[0].message}
			</p>
		{/if}
	</div>
</div>

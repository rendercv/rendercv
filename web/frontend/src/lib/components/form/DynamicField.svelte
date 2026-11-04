<script lang="ts">
	import type { FieldDescriptor } from '$lib/schema/types';
	import type { ValidationError } from '$lib/api/validate';
	import type { PathSegment } from '$lib/form/patchOps';
	import type { OverrideInfo } from '$lib/form/effectiveValue';
	import FieldRow from './FieldRow.svelte';
	import ArrayField from './ArrayField.svelte';
	import ObjectFieldset from './ObjectFieldset.svelte';

	/**
	 * Dispatches one resolved {@link FieldDescriptor} to the right control,
	 * recursively for arrays/objects — the generic half of "the form is
	 * generated from `/api/schema`" (the other half is `SectionsEditor`,
	 * which owns the one part of the CV schema that isn't a plain
	 * object/array/scalar tree: the polymorphic `sections` mapping).
	 */
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
		/** See `FieldRow`'s doc comment: threaded through unchanged for the effective-value overlay. */
		path?: PathSegment[];
		overrideInfo?: OverrideInfo;
		/** See `FieldRow`: set by `ArrayField` so the hint shows once per list. */
		hideFormatHint?: boolean;
	} = $props();
</script>

{#if descriptor.kind === 'array'}
	<ArrayField
		{descriptor}
		values={(value as unknown[] | null | undefined) ?? []}
		{onchange}
		{path}
		{overrideInfo}
	/>
{:else if descriptor.kind === 'object'}
	<ObjectFieldset
		{descriptor}
		value={(value as Record<string, unknown> | null | undefined) ?? {}}
		onFieldChange={(key, fieldValue) =>
			onchange({ ...((value as Record<string, unknown> | null | undefined) ?? {}), [key]: fieldValue })}
		{path}
		{overrideInfo}
	/>
{:else}
	<FieldRow {descriptor} {value} {errors} {onchange} {path} {overrideInfo} {hideFormatHint} />
{/if}

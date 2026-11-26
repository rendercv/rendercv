<script lang="ts">
	import type { FieldDescriptor } from '$lib/schema/types';
	import type { ValidationError } from '$lib/api/validate';
	import type { PathSegment } from '$lib/form/patchOps';
	import type { OverrideInfo } from '$lib/form/effectiveValue';
	import DynamicField from './DynamicField.svelte';

	let {
		descriptor,
		value,
		onFieldChange,
		errorsForField = () => [],
		path = [],
		overrideInfo
	}: {
		descriptor: FieldDescriptor;
		value: Record<string, unknown>;
		onFieldChange: (key: string, value: unknown) => void;
		errorsForField?: (key: string) => ValidationError[];
		/** This object field's own path from the document root; children extend it with their own key. */
		path?: PathSegment[];
		overrideInfo?: OverrideInfo;
	} = $props();
</script>

<fieldset class="flex flex-col gap-0 rounded-md border border-neutral-200 p-2 dark:border-[var(--border-subtle)]">
	{#if descriptor.label}
		<legend class="px-1 text-sm font-medium text-neutral-700 dark:text-neutral-300">
			{descriptor.label}
		</legend>
	{/if}
	{#each descriptor.fields ?? [] as field (field.key)}
		<DynamicField
			descriptor={field}
			value={value?.[field.key]}
			errors={errorsForField(field.key)}
			onchange={(fieldValue) => onFieldChange(field.key, fieldValue)}
			path={[...path, field.key]}
			{overrideInfo}
		/>
	{/each}
</fieldset>

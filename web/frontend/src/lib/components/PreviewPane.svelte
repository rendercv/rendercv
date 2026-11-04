<script lang="ts">
	import type { Readable } from 'svelte/store';
	import type { PreviewState } from '$lib/preview/renderController';
	import type { ValidationError } from '$lib/api/validate';
	import { DOCUMENT_KEYS, DOCUMENT_LABELS, type DocumentKey } from '$lib/stores/documents';
	import { groupErrorsByDocument, classifyError } from '$lib/editor/errorClassification';

	let {
		previewState,
		errors = [],
		zoom = 100,
		onErrorClick
	}: {
		previewState: Readable<PreviewState>;
		errors?: ValidationError[];
		zoom?: number;
		onErrorClick?: (error: ValidationError) => void;
	} = $props();

	let errorDismissed = $state(false);
	let lastErrorCount = $state(0);

	// Re-surface the error bar whenever a new batch of errors arrives, even
	// if the user had dismissed a previous batch.
	$effect(() => {
		const count = errors.length;
		if (count > 0 && count !== lastErrorCount) {
			errorDismissed = false;
		}
		lastErrorCount = count;
	});

	/**
	 * System-kind errors (a 500, a network failure, anything that isn't the
	 * structured 422 shape -- see `genericSystemError`) get a single friendly
	 * banner line instead of being grouped by document/tab: they carry no
	 * useful yaml_source/line, so treating them like a field error would
	 * either mislabel them under "CV" or (worse) show their raw message.
	 */
	let systemErrors = $derived(errors.filter((e) => e.kind === 'system'));
	let fieldErrors = $derived(errors.filter((e) => e.kind !== 'system'));

	let errorsByTab = $derived(groupErrorsByDocument(fieldErrors));
	let tabsWithErrors = $derived(DOCUMENT_KEYS.filter((key) => errorsByTab[key].length > 0));

	function categoryIcon(error: ValidationError): string {
		return classifyError(error) === 'syntax' ? '⛔' : '⚠';
	}

	function categoryLabel(error: ValidationError): string {
		return classifyError(error) === 'syntax' ? 'YAML syntax error' : 'Validation error';
	}

	const scalePercent = $derived(100 / (zoom / 100));
</script>

<section
	class="flex h-full flex-col bg-neutral-50 dark:bg-[var(--surface-sidebar)]"
	aria-label="PDF preview"
	aria-busy={$previewState.status === 'pending' && !$previewState.hasRenderedOnce}
>
	{#if errors.length > 0 && !errorDismissed}
		<div
			class="flex items-start justify-between gap-3 border-b border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200"
			role="alert"
		>
			<div class="space-y-2">
				{#if systemErrors.length > 0}
					<div>
						<p class="font-medium">Something went wrong — please try again.</p>
						{#if systemErrors[0].errorId}
							<p class="text-xs text-red-400 dark:text-red-500">Error ID: {systemErrors[0].errorId}</p>
						{/if}
					</div>
				{/if}
				{#each tabsWithErrors as tabKey (tabKey)}
					<div>
						<div class="text-xs font-semibold uppercase tracking-wide text-red-600 dark:text-red-300">
							{DOCUMENT_LABELS[tabKey]}
						</div>
						<ul class="space-y-1">
							{#each errorsByTab[tabKey] as error, index (index)}
								<li>
									<button
										type="button"
										class="text-left underline-offset-2 hover:underline"
										title={categoryLabel(error)}
										onclick={() => onErrorClick?.(error)}
									>
										<span aria-hidden="true">{categoryIcon(error)}</span>
										<span class="sr-only">{categoryLabel(error)}:</span>
										{#if error.location}<span class="font-medium">{error.location}</span>{/if}
										{#if error.yaml_line !== null}
											<span> (line {error.yaml_line})</span>
										{/if}: {error.message}
									</button>
								</li>
							{/each}
						</ul>
					</div>
				{/each}
			</div>
			<button
				type="button"
				class="shrink-0 rounded px-2 py-0.5 text-red-700 hover:bg-red-100 dark:text-red-200 dark:hover:bg-red-900"
				aria-label="Dismiss errors"
				onclick={() => (errorDismissed = true)}
			>
				✕
			</button>
		</div>
	{/if}

	<div class="relative flex-1 overflow-auto">
		{#if $previewState.status === 'pending' && !$previewState.hasRenderedOnce}
			<div class="absolute inset-0 flex flex-col gap-3 p-6" aria-hidden="true">
				<div class="h-8 w-2/3 animate-pulse rounded bg-neutral-200 dark:bg-[var(--surface-card)]"></div>
				<div class="h-full w-full animate-pulse rounded bg-neutral-200 dark:bg-[var(--surface-card)]"></div>
			</div>
			<span class="sr-only" role="status">Rendering preview…</span>
		{:else if $previewState.url}
			<div
				style={`transform: scale(${zoom / 100}); transform-origin: top left; width: ${scalePercent}%; height: ${scalePercent}%;`}
			>
				<iframe title="CV PDF preview" src={$previewState.url} class="h-full w-full border-0"
				></iframe>
			</div>
		{:else}
			<div class="flex h-full items-center justify-center text-sm text-neutral-500 dark:text-neutral-400">
				Nothing to preview yet.
			</div>
		{/if}
	</div>
</section>

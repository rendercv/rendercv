<script lang="ts">
	import type { Readable } from 'svelte/store';
	import type { AutosaveState } from '$lib/persistence/autosave';

	let { state, onRetry = undefined }: { state: Readable<AutosaveState>; onRetry?: () => void } = $props();

	const LABELS: Record<AutosaveState['status'], string> = {
		saved: 'Saved',
		saving: 'Saving…',
		retrying: 'Save failed — retrying',
		error: 'Save failed',
		conflict: 'Save paused'
	};
</script>

<div class="flex items-center gap-2 text-sm text-neutral-500 dark:text-neutral-400" aria-live="polite">
	<span
		class="h-1.5 w-1.5 rounded-full"
		class:bg-emerald-500={$state.status === 'saved'}
		class:bg-amber-500={$state.status === 'saving' || $state.status === 'retrying'}
		class:bg-red-500={$state.status === 'error' || $state.status === 'conflict'}
		aria-hidden="true"
	></span>
	<span>{$state.permanentError ?? LABELS[$state.status]}</span>
	{#if $state.status === 'error' && !$state.permanentError && onRetry}
		<button
			type="button"
			class="ml-1 rounded border border-neutral-300 px-1.5 py-0.5 text-xs font-medium hover:bg-neutral-100 dark:border-[var(--border-subtle)] dark:hover:bg-[var(--surface-card)]"
			onclick={onRetry}
		>
			Retry
		</button>
	{/if}
</div>

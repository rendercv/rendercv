<script lang="ts">
	import {
		DEFAULT_SPLIT_RATIO,
		MIN_SPLIT_RATIO,
		MAX_SPLIT_RATIO,
		ratioFromDrag,
		stepSplitRatio
	} from '$lib/layout/splitRatio';

	/**
	 * The vertical drag divider between the editor pane and the PDF preview
	 * pane (Phase 5 wave 3, user's explicit #1 request). Pointer-drag and
	 * keyboard both call `onChange` with a new clamped ratio; the parent
	 * (`+page.svelte`) owns the actual value (backed by `$lib/stores/
	 * splitRatio.ts`) and re-renders the two panes' `flex-basis`.
	 *
	 * Deliberately dependency-free on the math side -- everything numeric
	 * routes through `$lib/layout/splitRatio.ts`, which is what's unit-tested.
	 */
	let {
		ratio,
		onChange
	}: {
		ratio: number;
		onChange: (next: number) => void;
	} = $props();

	let dragging = $state(false);
	let handleEl: HTMLDivElement | undefined = $state();
	let dragStartX = 0;
	let dragStartRatio = 0;
	let containerWidth = 0;

	function startDrag(event: PointerEvent): void {
		if (event.button !== 0 && event.pointerType === 'mouse') return;
		event.preventDefault();
		dragging = true;
		dragStartX = event.clientX;
		dragStartRatio = ratio;
		// The divider's parent is the flex row both panes live in -- its
		// width is what a percentage delta is computed against.
		const parent = handleEl?.parentElement;
		containerWidth = parent?.getBoundingClientRect().width ?? 0;
	}

	function onPointerMove(event: PointerEvent): void {
		if (!dragging) return;
		const delta = event.clientX - dragStartX;
		onChange(ratioFromDrag(dragStartRatio, delta, containerWidth));
	}

	function endDrag(): void {
		dragging = false;
	}

	function resetToDefault(): void {
		onChange(DEFAULT_SPLIT_RATIO);
	}

	function onKeydown(event: KeyboardEvent): void {
		switch (event.key) {
			case 'ArrowLeft':
				event.preventDefault();
				onChange(stepSplitRatio(ratio, 'decrease'));
				break;
			case 'ArrowRight':
				event.preventDefault();
				onChange(stepSplitRatio(ratio, 'increase'));
				break;
			case 'Home':
				event.preventDefault();
				onChange(MIN_SPLIT_RATIO);
				break;
			case 'End':
				event.preventDefault();
				onChange(MAX_SPLIT_RATIO);
				break;
			default:
				break;
		}
	}
</script>

<svelte:window
	onpointermove={dragging ? onPointerMove : undefined}
	onpointerup={dragging ? endDrag : undefined}
	onpointercancel={dragging ? endDrag : undefined}
/>

<!--
	This is the WAI-ARIA "resizable separator" (window-splitter) pattern:
	`role="separator"` with `tabindex`, a keydown handler, and
	`aria-value*` is exactly what the APG documents for this widget, even
	though svelte's generic a11y linter flags `separator` as a
	"non-interactive" role (its allowlist doesn't special-case the
	resizable variant of it).
-->
<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
	bind:this={handleEl}
	role="separator"
	aria-orientation="vertical"
	aria-label="Resize editor and preview panes"
	aria-valuenow={Math.round(ratio)}
	aria-valuemin={MIN_SPLIT_RATIO}
	aria-valuemax={MAX_SPLIT_RATIO}
	aria-valuetext={`Editor ${Math.round(ratio)}%, preview ${Math.round(100 - ratio)}%`}
	tabindex="0"
	class="group relative z-10 flex w-2.5 shrink-0 cursor-col-resize touch-none items-center justify-center outline-none select-none"
	class:select-none={dragging}
	onpointerdown={startDrag}
	ondblclick={resetToDefault}
	onkeydown={onKeydown}
	data-dragging={dragging}
>
	<div
		class="h-full w-px bg-neutral-200 transition-colors group-hover:bg-purple-300 group-focus-visible:bg-purple-400 dark:bg-[var(--border-subtle)] dark:group-hover:bg-purple-700"
		class:bg-purple-400={dragging}
	></div>
	<div
		class="absolute h-10 w-1.5 rounded-full bg-neutral-300 transition-colors group-hover:bg-purple-400 group-focus-visible:bg-purple-500 dark:bg-neutral-600 dark:group-hover:bg-purple-500"
		class:bg-purple-500={dragging}
		class:dark:bg-purple-500={dragging}
		aria-hidden="true"
	></div>

	{#if dragging}
		<!--
			Classic iframe-drag bug: the PDF preview is an `<iframe>` with its
			own document, so as soon as the pointer physically moves over it
			mid-drag, that document (not this one) starts receiving pointer
			events, which silently stalls the resize the instant the divider
			crosses into preview-pane territory. A full-viewport transparent
			shield -- present only while `dragging` -- keeps every pointermove
			landing on `<svelte:window>`'s listener instead.
		-->
		<div class="fixed inset-0 z-50 cursor-col-resize" aria-hidden="true" data-testid="splitter-drag-shield"></div>
	{/if}
</div>

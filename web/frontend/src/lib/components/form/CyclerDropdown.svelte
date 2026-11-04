<script lang="ts">
	/**
	 * `‹ value ›` cycler + dropdown, shared by the tab bar's theme switcher and
	 * the form's `StepperField` (font family, and any other "longer enum")
	 * — matches the reference's `<` `>` steppers-with-a-dropdown pattern in
	 * one place instead of two near-identical implementations.
	 *
	 * Keyboard: `‹`/`›` cycle with wraparound; the value button opens a
	 * listbox (checkmark on the current option); ArrowUp/ArrowDown move the
	 * highlight, Enter selects, Escape closes and returns focus to the
	 * trigger.
	 *
	 * Why the value button has a fixed width rather than a minimum: the
	 * options it cycles through are wildly different lengths (`ink` against
	 * `Engineering Resumes`), and a button sized to its content moves the
	 * `›` next to it every time the value changes. Cycling means pressing
	 * `›` repeatedly, so the control was walking out from under the
	 * pointer — the second press landed on whatever had slid into that
	 * spot. A minimum width is not enough -- it is a floor, not a ceiling,
	 * so the longest labels still pushed past it (the regression test
	 * caught exactly that, 1.8px of drift on `Engineering Resumes`). The
	 * width is fixed and long labels truncate, so both arrows hold still
	 * whatever the options are named.
	 *
	 * Why the arrows are inline SVG rather than the `‹` `›` characters they
	 * started as: a glyph is drawn by whichever font resolves it, so its
	 * weight and vertical centring were at the mercy of font fallback, and
	 * the chevron (`˅`, a modifier letter) sat visibly off the baseline.
	 */
	let {
		options,
		value,
		onchange,
		ariaLabel,
		id,
		format = (option: string) => option
	}: {
		options: string[];
		value: string;
		onchange: (value: string) => void;
		ariaLabel: string;
		id?: string;
		/**
		 * Turns an option into the text shown for it. Values handed to
		 * `onchange` are always the raw option, never the formatted label.
		 */
		format?: (option: string) => string;
	} = $props();

	let open = $state(false);
	let highlighted = $state(0);
	let triggerEl: HTMLButtonElement | undefined = $state();
	let optionEls: (HTMLLIElement | undefined)[] = $state([]);

	function indexOfValue(): number {
		const i = options.indexOf(value);
		return i === -1 ? 0 : i;
	}

	function cycle(delta: number): void {
		if (options.length === 0) return;
		const current = indexOfValue();
		const next = (current + delta + options.length) % options.length;
		onchange(options[next]);
	}

	function openDropdown(): void {
		highlighted = indexOfValue();
		open = true;
	}

	function closeDropdown(returnFocus: boolean): void {
		open = false;
		if (returnFocus) triggerEl?.focus();
	}

	function selectHighlighted(): void {
		const option = options[highlighted];
		if (option !== undefined) onchange(option);
		closeDropdown(true);
	}

	function handleListKeydown(e: KeyboardEvent): void {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			highlighted = (highlighted + 1) % options.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			highlighted = (highlighted - 1 + options.length) % options.length;
		} else if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			selectHighlighted();
		} else if (e.key === 'Escape') {
			e.preventDefault();
			closeDropdown(true);
		} else if (e.key === 'Tab') {
			closeDropdown(false);
		}
	}

	$effect(() => {
		if (open) optionEls[highlighted]?.focus();
	});
</script>

<div class="inline-flex items-center gap-1">
	<button
		type="button"
		class="grid h-8 w-8 shrink-0 place-items-center rounded-md text-neutral-600 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
		aria-label={`Previous ${ariaLabel}`}
		onclick={() => cycle(-1)}
	>
		<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
			<path
				d="M10 3.5L5.5 8l4.5 4.5"
				stroke="currentColor"
				stroke-width="1.6"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>
	</button>

	<div class="relative">
		<button
			bind:this={triggerEl}
			type="button"
			{id}
			class="flex h-8 w-48 items-center justify-between gap-2 rounded-md border border-neutral-300 px-3 text-sm font-medium text-neutral-800 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 dark:border-[var(--border-subtle)] dark:text-neutral-100 dark:hover:bg-[var(--surface-card)]"
			aria-haspopup="listbox"
			aria-expanded={open}
			aria-label={ariaLabel}
			onclick={() => (open ? closeDropdown(false) : openDropdown())}
		>
			<span class="truncate">{format(value)}</span>
			<svg
				width="14"
				height="14"
				viewBox="0 0 16 16"
				fill="none"
				aria-hidden="true"
				class="shrink-0 text-neutral-500 dark:text-neutral-400"
			>
				<path
					d="M4 6l4 4 4-4"
					stroke="currentColor"
					stroke-width="1.6"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>

		{#if open}
			<button
				type="button"
				class="fixed inset-0 z-10 cursor-default"
				aria-label="Close dropdown"
				tabindex="-1"
				onclick={() => closeDropdown(false)}
			></button>
			<ul
				role="listbox"
				aria-label={ariaLabel}
				class="absolute left-0 top-full z-20 mt-1 max-h-64 min-w-full overflow-auto rounded-md border border-neutral-200 bg-white py-1 shadow-lg dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)]"
				onkeydown={handleListKeydown}
			>
				{#each options as option, i (option)}
					<li
						bind:this={optionEls[i]}
						role="option"
						aria-selected={option === value}
						tabindex="-1"
						class="flex cursor-pointer items-center gap-2 whitespace-nowrap px-3 py-1.5 text-sm text-neutral-700 outline-none hover:bg-purple-50 focus:bg-purple-100 dark:text-neutral-200 dark:hover:bg-[var(--surface-card)] dark:focus:bg-neutral-800"
						onclick={() => {
							onchange(option);
							closeDropdown(true);
						}}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								onchange(option);
								closeDropdown(true);
							}
						}}
						onmouseenter={() => (highlighted = i)}
					>
						<span class="w-3" aria-hidden="true">{option === value ? '✓' : ''}</span>
						<span>{format(option)}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<button
		type="button"
		class="grid h-8 w-8 shrink-0 place-items-center rounded-md text-neutral-600 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
		aria-label={`Next ${ariaLabel}`}
		onclick={() => cycle(1)}
	>
		<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
			<path
				d="M6 3.5L10.5 8 6 12.5"
				stroke="currentColor"
				stroke-width="1.6"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>
	</button>
</div>

<svelte:window
	onkeydown={(e) => {
		if (open && e.key === 'Escape') closeDropdown(true);
	}}
/>

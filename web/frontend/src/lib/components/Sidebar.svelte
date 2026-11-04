<script lang="ts">
	import { tick } from 'svelte';
	import type { Readable } from 'svelte/store';
	import type { CvSummary } from '$lib/api/cvs';
	import type { ActiveCvMeta } from '$lib/stores/cvSession';
	import { formatRelativeTime } from '$lib/app/relativeTime';
	import { listVersions, type CvVersionSummary } from '$lib/api/cvs';
	import type { AuthStatus } from '$lib/api/auth';
	import BrandMark from '$lib/components/BrandMark.svelte';
	import AccountMenu from '$lib/components/AccountMenu.svelte';

	let {
		cvs,
		activeCv,
		collapsed = $bindable(false),
		onSwitch,
		onCreate,
		onImportFile,
		onRename,
		onDuplicate,
		onDelete,
		onRestore,
		authStatus,
		onSignOut,
		onDeleteAccount
	}: {
		cvs: Readable<CvSummary[]>;
		activeCv: Readable<ActiveCvMeta | null>;
		collapsed?: boolean;
		onSwitch: (id: number) => void;
		onCreate: () => void;
		onImportFile: (file: File) => Promise<string | null>;
		onRename: (id: number, name: string) => void;
		onDuplicate: (id: number) => void;
		onDelete: (id: number) => void;
		onRestore: (id: number, versionId: number) => void;
		authStatus: Readable<AuthStatus>;
		onSignOut: () => void;
		onDeleteAccount: () => void;
	} = $props();

	let fileInputEl: HTMLInputElement | undefined = $state();
	// The reason the last import was refused, shown until the next attempt.
	// Kept here rather than in a toast: the button is where the user is
	// looking, and a file they chose by mistake deserves an answer that
	// stays on screen while they find the right one.
	let importError = $state<string | null>(null);
	let importing = $state(false);

	async function handleFileChosen(event: Event): Promise<void> {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		// Reset immediately so choosing the same file twice fires `change`
		// again -- otherwise a user who fixes their file and picks it once
		// more gets no response at all.
		input.value = '';
		if (!file) return;

		importing = true;
		importError = null;
		try {
			importError = await onImportFile(file);
		} finally {
			importing = false;
		}
	}

	let menuOpenId = $state<number | null>(null);
	let renamingId = $state<number | null>(null);
	let renameValue = $state('');
	let renameInputEl: HTMLInputElement | undefined = $state();
	let confirmDeleteId = $state<number | null>(null);
	let historyId = $state<number | null>(null);
	let historyVersions = $state<CvVersionSummary[] | null>(null);
	let historyLoading = $state(false);

	// Where the open CV's popovers (menu, history, delete confirmation) sit.
	// They are `position: fixed` because the CV list scrolls: an absolutely
	// positioned popover under the last CVs was clipped by the list's
	// `overflow-y: auto` and ended up hidden behind the account footer, so
	// those CVs could not be renamed or deleted at all.
	let popoverAnchor = $state<DOMRect | null>(null);

	const MENU_HEIGHT: number = 160;
	const HISTORY_HEIGHT: number = 260;
	const CONFIRM_HEIGHT: number = 120;

	/**
	 * Compute fixed-position CSS for a popover anchored to the ⋯ button.
	 *
	 * Why:
	 *     Opens below the button when there is room, and flips above it
	 *     otherwise, so the last CVs in a long list still get a usable menu.
	 *
	 * Args:
	 *     anchor: Bounding rect of the ⋯ button that opened the popover.
	 *     height: Expected popover height used to decide whether it fits below.
	 *
	 * Returns:
	 *     Inline style string for the popover element.
	 */
	function popoverStyle(anchor: DOMRect | null, height: number): string {
		if (!anchor) return '';
		const right: number = window.innerWidth - anchor.right;
		const roomBelow: number = window.innerHeight - anchor.bottom;
		if (roomBelow < height + 8 && anchor.top > roomBelow) {
			return `right: ${right}px; bottom: ${window.innerHeight - anchor.top + 4}px;`;
		}
		return `right: ${right}px; top: ${anchor.bottom + 4}px;`;
	}

	function toggleMenu(id: number, event: MouseEvent): void {
		if (menuOpenId === id) {
			menuOpenId = null;
			return;
		}
		popoverAnchor = (event.currentTarget as HTMLElement).getBoundingClientRect();
		historyId = null;
		confirmDeleteId = null;
		menuOpenId = id;
	}

	function closeMenu(): void {
		menuOpenId = null;
	}

	function closeAllPopovers(): void {
		closeMenu();
		if (historyId !== null) closeHistory();
		confirmDeleteId = null;
	}

	async function startRename(cv: CvSummary): Promise<void> {
		closeMenu();
		renamingId = cv.id;
		renameValue = cv.name;
		await tick();
		renameInputEl?.focus();
		renameInputEl?.select();
	}

	function commitRename(id: number): void {
		if (renamingId !== id) return;
		const name = renameValue.trim();
		renamingId = null;
		if (name !== '') onRename(id, name);
	}

	function cancelRename(): void {
		renamingId = null;
	}

	function askDelete(id: number): void {
		closeMenu();
		confirmDeleteId = id;
	}

	function confirmDelete(): void {
		if (confirmDeleteId !== null) onDelete(confirmDeleteId);
		confirmDeleteId = null;
	}

	function cancelDelete(): void {
		confirmDeleteId = null;
	}

	async function openHistory(id: number): Promise<void> {
		closeMenu();
		historyId = id;
		historyVersions = null;
		historyLoading = true;
		try {
			historyVersions = (await listVersions(id)) ?? [];
		} finally {
			historyLoading = false;
		}
	}

	function closeHistory(): void {
		historyId = null;
		historyVersions = null;
	}

	function restoreVersion(id: number, versionId: number): void {
		onRestore(id, versionId);
		closeHistory();
	}

	function duplicate(id: number): void {
		closeMenu();
		onDuplicate(id);
	}
</script>

<aside
	class="flex h-full flex-col border-r border-neutral-200 bg-neutral-50 transition-[width] duration-150 dark:border-[var(--border-subtle)] dark:bg-[var(--surface-sidebar)]"
	class:w-64={!collapsed}
	class:w-12={collapsed}
	aria-label="CV list"
>
	<!--
		Brand row: a simple bird-ish mark + wordmark (adapted from the
		landing page's own mark, `LandingNav.svelte` -- not a copy of the
		real rendercv.com logo asset). The sidebar's own collapse toggle
		lives in the editor toolbar now (`EditorPane`'s sidebar-collapse
		button), so collapsed state just narrows this rail to the mark alone.
	-->
	<div class="flex items-center p-2" class:justify-center={collapsed}>
		<span class="flex items-center gap-2 px-1 text-neutral-800 dark:text-neutral-100">
			<span class="text-purple-500 dark:text-purple-400"><BrandMark size={20} /></span>
			{#if !collapsed}
				<span class="text-sm font-semibold tracking-tight">RenderCV</span>
			{/if}
		</span>
	</div>

	{#if !collapsed}
		<div class="px-2 pb-2">
			<button
				type="button"
				class="flex w-full items-center gap-1.5 rounded-md px-2 py-2 text-left text-sm font-medium text-neutral-700 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 dark:text-neutral-200 dark:hover:bg-[var(--surface-card)]"
				onclick={onCreate}
			>
				<span class="text-purple-500 dark:text-purple-400">+</span> Create new CV
			</button>
			<!--
				Import sits beside "Create new CV" because that is what it is: a
				second way to bring a CV into the workspace. It never touches the
				CV that is open, so choosing the wrong file costs a spare CV in
				the list rather than the work in front of you.
			-->
			<button
				type="button"
				disabled={importing}
				class="flex w-full items-center gap-1.5 rounded-md px-2 py-2 text-left text-sm font-medium text-neutral-700 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 disabled:opacity-50 dark:text-neutral-200 dark:hover:bg-[var(--surface-card)]"
				onclick={() => fileInputEl?.click()}
			>
				<span class="text-purple-500 dark:text-purple-400">↑</span>
				{importing ? 'Importing…' : 'Import CV'}
			</button>
			<input
				bind:this={fileInputEl}
				type="file"
				accept=".yaml,.yml,text/yaml,application/yaml"
				aria-label="YAML file to import"
				class="sr-only"
				onchange={handleFileChosen}
			/>
			{#if importError}
				<p
					role="alert"
					class="mt-1 rounded-md bg-red-50 px-2 py-1.5 text-xs text-red-800 dark:bg-red-950 dark:text-red-200"
				>
					{importError}
				</p>
			{/if}
		</div>

		<div class="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-neutral-400 dark:text-neutral-500">
			CVs
		</div>

		<!-- Popovers are fixed to the viewport, so scrolling the list would
		     leave them floating beside the wrong CV: close them instead. -->
		<nav class="flex-1 overflow-y-auto px-2" aria-label="Saved CVs" onscroll={closeAllPopovers}>
			<ul class="space-y-0.5">
				{#each $cvs as cv (cv.id)}
					{@const active = $activeCv?.id === cv.id}
					<li class="relative">
						{#if renamingId === cv.id}
							<input
								bind:this={renameInputEl}
								bind:value={renameValue}
								aria-label={`Rename ${cv.name}`}
								class="w-full rounded-md border border-purple-400 bg-white px-2 py-1.5 text-sm text-neutral-900 outline-none dark:bg-[var(--surface-card)] dark:text-neutral-100"
								onblur={() => commitRename(cv.id)}
								onkeydown={(e) => {
									if (e.key === 'Enter') {
										e.preventDefault();
										commitRename(cv.id);
									} else if (e.key === 'Escape') {
										e.preventDefault();
										cancelRename();
									}
								}}
							/>
						{:else}
							<div class="flex items-center gap-1">
								<button
									type="button"
									class="min-w-0 flex-1 truncate rounded-md px-2 py-1.5 text-left text-sm font-medium"
									class:bg-purple-100={active}
									class:text-purple-800={active}
									class:dark:bg-purple-950={active}
									class:dark:text-purple-200={active}
									class:text-neutral-700={!active}
									class:hover:bg-neutral-100={!active}
									class:dark:text-neutral-200={!active}
									class:dark:hover:bg-[var(--surface-card)]={!active}
									aria-current={active ? 'true' : undefined}
									onclick={() => onSwitch(cv.id)}
								>
									<span class="block truncate">{cv.name}</span>
									<span class="block truncate text-xs font-normal text-neutral-500 dark:text-neutral-400">
										{formatRelativeTime(cv.updatedAt)}
									</span>
								</button>

								<button
									type="button"
									class="grid h-7 w-7 shrink-0 place-items-center rounded-md text-neutral-500 hover:bg-neutral-200 dark:text-neutral-400 dark:hover:bg-[var(--surface-card)]"
									aria-label={`More actions for ${cv.name}`}
									aria-haspopup="menu"
									aria-expanded={menuOpenId === cv.id}
									onclick={(e) => toggleMenu(cv.id, e)}
								>
									⋯
								</button>
							</div>

							{#if menuOpenId === cv.id}
								<button
									type="button"
									class="fixed inset-0 z-40 cursor-default"
									aria-label="Close menu"
									tabindex="-1"
									onclick={closeMenu}
								></button>
								<ul
									role="menu"
									aria-label={`Actions for ${cv.name}`}
									style={popoverStyle(popoverAnchor, MENU_HEIGHT)}
									class="fixed z-50 w-40 rounded-md border border-neutral-200 bg-white py-1 text-sm shadow-lg dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)]"
								>
									<li role="none">
										<button
											role="menuitem"
											type="button"
											class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-[var(--surface-card)]"
											onclick={() => startRename(cv)}
										>
											Rename
										</button>
									</li>
									<li role="none">
										<button
											role="menuitem"
											type="button"
											class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-[var(--surface-card)]"
											onclick={() => duplicate(cv.id)}
										>
											Duplicate
										</button>
									</li>
									<li role="none">
										<button
											role="menuitem"
											type="button"
											class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-[var(--surface-card)]"
											onclick={() => openHistory(cv.id)}
										>
											History…
										</button>
									</li>
									<li role="none">
										<button
											role="menuitem"
											type="button"
											class="w-full px-3 py-1.5 text-left text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
											onclick={() => askDelete(cv.id)}
										>
											Delete
										</button>
									</li>
								</ul>
							{/if}

							{#if historyId === cv.id}
								<div
									style={popoverStyle(popoverAnchor, HISTORY_HEIGHT)}
									class="fixed z-50 w-56 rounded-md border border-neutral-200 bg-white p-2 text-sm shadow-lg dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)]"
								>
									<div class="mb-1 flex items-center justify-between">
										<span class="font-medium text-neutral-700 dark:text-neutral-200">History</span>
										<button
											type="button"
											class="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
											aria-label="Close history"
											onclick={closeHistory}
										>
											✕
										</button>
									</div>
									{#if historyLoading}
										<p class="text-neutral-500 dark:text-neutral-400">Loading…</p>
									{:else if !historyVersions || historyVersions.length === 0}
										<p class="text-neutral-500 dark:text-neutral-400">No saved versions yet.</p>
									{:else}
										<ul class="max-h-48 space-y-0.5 overflow-y-auto">
											{#each historyVersions as version (version.id)}
												<li>
													<button
														type="button"
														class="w-full rounded px-2 py-1 text-left hover:bg-neutral-100 dark:hover:bg-[var(--surface-card)]"
														onclick={() => restoreVersion(cv.id, version.id)}
													>
														{formatRelativeTime(version.createdAt)}
													</button>
												</li>
											{/each}
										</ul>
									{/if}
								</div>
							{/if}

							{#if confirmDeleteId === cv.id}
								<div
									role="alertdialog"
									aria-label={`Delete ${cv.name}?`}
									style={popoverStyle(popoverAnchor, CONFIRM_HEIGHT)}
									class="fixed z-50 w-56 rounded-md border border-neutral-200 bg-white p-3 text-sm shadow-lg dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)]"
								>
									<p class="mb-2 text-neutral-700 dark:text-neutral-200">Delete "{cv.name}"? This cannot be undone.</p>
									<div class="flex justify-end gap-2">
										<button
											type="button"
											class="rounded-md border border-neutral-300 px-2.5 py-1 dark:border-[var(--border-subtle)]"
											onclick={cancelDelete}
										>
											Cancel
										</button>
										<button
											type="button"
											class="rounded-md bg-red-600 px-2.5 py-1 font-medium text-white hover:bg-red-700"
											onclick={confirmDelete}
										>
											Delete
										</button>
									</div>
								</div>
							{/if}
						{/if}
					</li>
				{/each}
			</ul>
		</nav>

		<AccountMenu status={authStatus} {onSignOut} {onDeleteAccount} />

		<div class="flex items-center gap-1 border-t border-neutral-200 p-2 dark:border-[var(--border-subtle)]">
			<a
				href="/"
				class="flex flex-1 items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 dark:text-neutral-400 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-200"
			>
				<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
					<circle cx="12" cy="12" r="9" />
					<path d="M12 16v-4.5M12 8.5h.01" stroke-linecap="round" />
				</svg>
				About
			</a>
			<a
				href="https://github.com/rendercv/rendercv"
				target="_blank"
				rel="noopener noreferrer"
				class="flex flex-1 items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 dark:text-neutral-400 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-200"
			>
				<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor" aria-hidden="true">
					<path
						d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55 0-.27-.01-1.16-.02-2.11-3.2.7-3.87-1.36-3.87-1.36-.52-1.34-1.28-1.69-1.28-1.69-1.04-.72.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.43-2.69 5.41-5.25 5.69.42.36.78 1.08.78 2.17 0 1.57-.01 2.83-.01 3.22 0 .3.2.66.79.55A10.52 10.52 0 0 0 23.5 12c0-6.35-5.15-11.5-11.5-11.5Z"
					/>
				</svg>
				GitHub
			</a>
		</div>
	{/if}
</aside>

<svelte:window
	onresize={closeAllPopovers}
	onkeydown={(e) => {
		if (e.key !== 'Escape') return;
		if (menuOpenId !== null) closeMenu();
		if (historyId !== null) closeHistory();
		if (confirmDeleteId !== null) cancelDelete();
	}}
/>

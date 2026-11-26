<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { get, type Readable } from 'svelte/store';
	import { DOCUMENT_KEYS, DOCUMENT_LABELS, type DocumentKey } from '$lib/stores/documents';
	import type { PreviewState } from '$lib/preview/renderController';
	import type { ValidationError } from '$lib/api/validate';
	import { groupErrorsByDocument } from '$lib/editor/errorClassification';
	import {
		deriveImageFilename,
		derivePdfFilename,
		deriveYamlFilename
	} from '$lib/editor/filename';
	import { renderImages } from '$lib/api/render';
	import { buildRendercvYaml } from '$lib/editor/exportYaml';
	import { documents } from '$lib/stores/documents';
	import { theme } from '$lib/stores/theme';
	import { fetchThemes, type ThemeInfo } from '$lib/api/themes';
	import { createFormSync } from '$lib/form/formSync';
	import { buildDiscriminatorSwitchOp } from '$lib/form/documentActions';
	import { designOverrides } from '$lib/themes/designDiff';
	import { createThemeMemory } from '$lib/themes/themeMemory';
	import { activeCv } from '$lib/stores/cvSession';
	import { themeDisplayName } from '$lib/themes/displayName';
	import YamlEditor from '$lib/components/YamlEditor.svelte';
	import CvForm from '$lib/components/form/CvForm.svelte';
	import DesignForm from '$lib/components/form/DesignForm.svelte';
	import LocaleForm from '$lib/components/form/LocaleForm.svelte';
	import SettingsForm from '$lib/components/form/SettingsForm.svelte';
	import ThemeSwitcher from '$lib/components/form/ThemeSwitcher.svelte';
	import AutosaveStatus from '$lib/components/AutosaveStatus.svelte';
	import type { AutosaveState } from '$lib/persistence/autosave';

	let {
		previewState,
		errors = [],
		zoom = $bindable(100),
		yamlMode = $bindable(true),
		sidebarCollapsed = $bindable(false),
		autosaveState,
		onResolveConflict = () => {},
		onRetrySave = () => {}
	}: {
		previewState: Readable<PreviewState>;
		errors?: ValidationError[];
		zoom?: number;
		yamlMode?: boolean;
		sidebarCollapsed?: boolean;
		autosaveState: Readable<AutosaveState>;
		onResolveConflict?: (action: 'reload' | 'overwrite') => void;
		onRetrySave?: () => void;
	} = $props();

	let activeTab = $state<DocumentKey>('cv');
	let yamlEditor: ReturnType<typeof YamlEditor> | undefined = $state();
	let canUndo = $state(false);
	let canRedo = $state(false);
	let downloadMenuOpen = $state(false);
	// Images are rendered on demand rather than kept alongside the preview:
	// a PNG page is roughly ten times a PDF's size, and almost nobody asks
	// for one. The label says so, because the wait is otherwise unexplained.
	let renderingImages = $state(false);
	let imageError = $state<string | null>(null);

	let errorsByTab = $derived(groupErrorsByDocument(errors));

	// The theme switcher is visible on every tab (reference UX), so its
	// design-document sync is owned here rather than by `DesignForm` --
	// otherwise two independent parse/patch controllers for the same
	// document would race each other the moment both are mounted.
	const designSync = createFormSync(documents, { documentKey: 'design' });
	const designSyncState = designSync.state;

	// The full list, not just the names: switching a theme rewrites the
	// design document from that theme's defaults, which arrive here.
	let themes = $state<ThemeInfo[]>([]);
	let themeNames = $derived(themes.length ? themes.map((t) => t.name) : ['classic']);

	onMount(() => {
		void designSync.activate();
		fetchThemes()
			.then((loaded) => {
				themes = loaded;
			})
			.catch(() => {
				// The switcher just keeps its single-item fallback list; the
				// Design form's own load-error message covers the user-visible case.
			});
	});

	onDestroy(() => {
		designSync.deactivate();
		designSync.destroy();
	});

	let currentTheme = $derived(
		(($designSyncState.data?.design as Record<string, unknown> | undefined)?.theme as string | undefined) ??
			'classic'
	);

	/**
	 * Switches theme by rewriting the whole design document.
	 *
	 * Why not by patching the `theme:` line, which is what this did: the
	 * starter design document now spells out every option at the starting
	 * theme's values (see `rendercv_web/defaults.py`). Those explicit values
	 * win over whatever theme is named, so changing only the name produced a
	 * byte-identical PDF -- the switcher looked like it worked and changed
	 * nothing. Replacing the block puts the new theme's own values in.
	 *
	 * Design edits do not go with it: the design being left is stored for
	 * its theme, on the server, and arriving at a theme puts back the design
	 * it had when the user last left it -- from either device
	 * (`themeMemory`). Only a theme never left before arrives at its
	 * defaults. Without this a CV tuned to one page under Harvard came back
	 * from a round trip through another theme on two.
	 *
	 * Falls back to the old single-key patch when the theme list has not
	 * loaded -- an offline switcher that renames the theme is still better
	 * than one that does nothing.
	 */
	async function switchTheme(theme: string): Promise<void> {
		const defaults = themes.find((candidate) => candidate.name === theme)?.design_defaults;
		if (!defaults) {
			designSync.submitOp(
				buildDiscriminatorSwitchOp(get(documents).design, 'design', 'theme', theme)
			);
			return;
		}

		const ticket = ++switchTicket;
		const cvId = get(activeCv)?.id ?? null;
		const fromTheme = currentTheme;
		const outcome = await themeMemory.switchTheme({
			cvId,
			fromTheme,
			fromDesign: $designSyncState.data?.design,
			toTheme: theme,
			toDefaults: defaults
		});
		// A later click, or opening another CV, while this was on the wire
		// has made this switch stale; applying it would undo the newer one.
		if (ticket !== switchTicket || (get(activeCv)?.id ?? null) !== cvId) return;

		designSync.submitOp({ op: 'set', path: ['design'], value: outcome.design });
		themeMemoryNotice = outcome.rememberFailed
			? `Couldn't save your ${themeDisplayName(fromTheme)} design to your account. It is kept in this tab only, so your other device won't see it.`
			: null;
	}

	const themeMemory = createThemeMemory();
	let switchTicket = 0;
	let themeMemoryNotice = $state<string | null>(null);

	let currentThemeDefaults = $derived(
		themes.find((candidate) => candidate.name === currentTheme)?.design_defaults
	);

	/**
	 * Design options that override the current theme's defaults.
	 *
	 * Why shown at all: a stale value (an imported `separator: ' | '`, say)
	 * makes a theme look broken while the YAML is doing exactly what it
	 * says. Naming the overrides next to the switcher points at the cause
	 * instead of the theme. Empty until the theme list has loaded.
	 */
	let overrides = $derived(
		currentThemeDefaults ? designOverrides($designSyncState.data?.design, currentThemeDefaults) : []
	);

	let confirmingReset = $state(false);

	/**
	 * Puts the current theme's defaults back, discarding every design edit.
	 *
	 * Why behind a confirmation: it is the same whole-block rewrite as a
	 * theme switch, so every customised option goes at once. Undo and the
	 * version history can bring them back, but the user should choose it.
	 */
	function resetThemeDefaults(): void {
		confirmingReset = false;
		if (!currentThemeDefaults) return;
		designSync.submitOp({ op: 'set', path: ['design'], value: currentThemeDefaults });
	}

	// Whenever the error set changes, refresh gutter markers in all four
	// documents so a tab a user hasn't opened yet is already annotated.
	$effect(() => {
		errors; // eslint-disable-line @typescript-eslint/no-unused-expressions -- track dependency
		yamlEditor?.refreshAllDiagnostics();
	});

	function errorsForTab(key: DocumentKey): ValidationError[] {
		return errorsByTab[key];
	}

	function zoomOut(): void {
		zoom = Math.max(50, zoom - 10);
	}

	function zoomIn(): void {
		zoom = Math.min(200, zoom + 10);
	}

	function resetZoom(): void {
		zoom = 100;
	}

	function download(url: string | null): void {
		if (!url) return;
		const link = document.createElement('a');
		link.href = url;
		link.download = derivePdfFilename($documents);
		link.click();
	}

	function toggleDownloadMenu(): void {
		downloadMenuOpen = !downloadMenuOpen;
	}

	function closeDownloadMenu(): void {
		downloadMenuOpen = false;
	}

	function downloadFromMenu(): void {
		download($previewState.url);
		closeDownloadMenu();
	}

	function saveBlob(blob: Blob, filename: string): void {
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = filename;
		link.click();
		URL.revokeObjectURL(url);
	}

	async function downloadImagesFromMenu(): Promise<void> {
		renderingImages = true;
		imageError = null;
		closeDownloadMenu();
		try {
			const result = await renderImages($documents);
			if (!result.ok) {
				imageError = result.errors[0]?.message ?? 'The images could not be rendered.';
				return;
			}
			saveBlob(result.blob, deriveImageFilename($documents, result.extension));
		} finally {
			renderingImages = false;
		}
	}

	function downloadYamlFromMenu(): void {
		// Built from the editor's live documents rather than refetched: what
		// the user sees is what they get, including edits the autosave has
		// not written yet.
		const blob = new Blob([buildRendercvYaml($documents)], { type: 'application/yaml' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = deriveYamlFilename($documents);
		link.click();
		// The blob would otherwise be held for the life of the document; the
		// click has already read it by the time this runs.
		URL.revokeObjectURL(url);
		closeDownloadMenu();
	}

	function toggleSidebar(): void {
		sidebarCollapsed = !sidebarCollapsed;
	}

	/** Active tab reads as a solid pill that swaps light/dark with the theme (white-on-navy in dark mode, dark-on-white in light) -- the reference's tab bar. */
	function tabClass(key: DocumentKey): string {
		const base = 'relative rounded-md px-3 py-1.5 text-sm font-medium transition-colors';
		return activeTab === key
			? `${base} bg-neutral-900 text-white dark:bg-white dark:text-neutral-900`
			: `${base} text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]`;
	}

	/** Called by the preview pane's error bar: switches to the error's tab and moves the cursor there. */
	export function goToError(error: ValidationError): void {
		const key = errorsByTab
			? (Object.keys(errorsByTab) as DocumentKey[]).find((k) => errorsByTab[k].includes(error))
			: undefined;
		if (key) activeTab = key;
		yamlMode = true;
		if (error.yaml_line !== null) {
			// Wait a tick so the editor has switched to the right document first.
			queueMicrotask(() => yamlEditor?.goToLine(error.yaml_line as number));
		}
	}
</script>

<section class="flex h-full flex-col" aria-label="CV editor">
	<!--
		Toolbar row -- left to right, matching the reference's chrome
		ordering: sidebar-collapse, undo/redo, a divider, the markdown B/I/
		link group, a flex gap, then the autosave indicator, YAML toggle,
		zoom controls, download (with its format-menu caret), and the
		light/dark toggle pinned at the far right.
	-->
	<div class="flex flex-wrap items-center justify-between gap-x-2 gap-y-1 border-b border-neutral-200 px-3 py-1.5 dark:border-[var(--border-subtle)]">
		<div class="flex items-center gap-2">
			<button
				type="button"
				class="grid h-6 w-6 shrink-0 place-items-center rounded text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
				aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
				aria-expanded={!sidebarCollapsed}
				onclick={toggleSidebar}
			>
				<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
					<rect x="3" y="4" width="18" height="16" rx="2" />
					<path d="M9 4v16" />
				</svg>
			</button>

			<div class="flex items-center gap-1.5" role="group" aria-label="Undo/redo">
				<button
					type="button"
					class="history-btn"
					aria-label="Undo"
					title="Undo"
					disabled={!yamlMode || !canUndo}
					onclick={() => yamlEditor?.undoActive()}
				>
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<path d="M9 14 4 9l5-5" />
						<path d="M4 9h11a5 5 0 0 1 5 5v6" />
					</svg>
				</button>
				<button
					type="button"
					class="history-btn"
					aria-label="Redo"
					title="Redo"
					disabled={!yamlMode || !canRedo}
					onclick={() => yamlEditor?.redoActive()}
				>
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<path d="m15 14 5-5-5-5" />
						<path d="M20 9H9a5 5 0 0 0-5 5v6" />
					</svg>
				</button>
			</div>

			<div class="h-4 w-px bg-neutral-300 dark:bg-[var(--border-subtle)]"></div>

			<div class="flex items-center gap-0.5" role="group" aria-label="Markdown formatting">
				<button
					type="button"
					class="grid h-6 w-6 place-items-center rounded text-sm font-bold text-neutral-600 hover:bg-neutral-100 disabled:opacity-40 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
					aria-label="Bold"
					disabled={!yamlMode}
					onclick={() => yamlEditor?.wrapBold()}
				>
					B
				</button>
				<button
					type="button"
					class="grid h-6 w-6 place-items-center rounded text-sm italic text-neutral-600 hover:bg-neutral-100 disabled:opacity-40 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
					aria-label="Italic"
					disabled={!yamlMode}
					onclick={() => yamlEditor?.wrapItalic()}
				>
					I
				</button>
				<button
					type="button"
					class="grid h-6 w-6 place-items-center rounded text-sm text-neutral-600 hover:bg-neutral-100 disabled:opacity-40 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
					aria-label="Insert link"
					disabled={!yamlMode}
					onclick={() => yamlEditor?.wrapLink()}
				>
					🔗
				</button>
			</div>
		</div>

		<!--
			Everything from the autosave indicator onward, grouped so the
			outer row's `justify-between` + `flex-wrap` can drop this whole
			cluster to its own line on a narrow pane instead of letting any
			single control overflow past the pane's edge (where it would sit
			underneath -- and be pointer-shadowed by -- the preview iframe).
		-->
		<div class="flex flex-wrap items-center justify-end gap-x-3 gap-y-1">
			<AutosaveStatus state={autosaveState} onRetry={onRetrySave} />

			<label class="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-300">
				<span>YAML</span>
				<button
					type="button"
					role="switch"
					aria-checked={yamlMode}
					aria-label="Toggle YAML editor"
					class="relative h-5 w-9 rounded-full transition-colors"
					class:bg-purple-600={yamlMode}
					class:bg-neutral-300={!yamlMode}
					onclick={() => (yamlMode = !yamlMode)}
				>
					<span
						class="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-[left]"
						style={`left: ${yamlMode ? '1.25rem' : '0.125rem'}`}
					></span>
				</button>
			</label>

			<div class="flex items-center gap-1" role="group" aria-label="Zoom controls">
				<button
					type="button"
					class="grid h-6 w-6 place-items-center rounded text-neutral-600 hover:bg-neutral-100 disabled:opacity-40 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
					aria-label="Zoom out"
					disabled={zoom <= 50}
					onclick={zoomOut}
				>
					−
				</button>
				<button
					type="button"
					class="w-12 text-center text-sm tabular-nums"
					aria-label="Reset zoom to 100%"
					onclick={resetZoom}
				>
					{zoom}%
				</button>
				<button
					type="button"
					class="grid h-6 w-6 place-items-center rounded text-neutral-600 hover:bg-neutral-100 disabled:opacity-40 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
					aria-label="Zoom in"
					disabled={zoom >= 200}
					onclick={zoomIn}
				>
					+
				</button>
			</div>

			<!--
				One button, two choices. It used to be a split control whose left
				half downloaded the PDF and whose right half opened a menu that
				offered the PDF again -- so the same action sat in two places and
				the YAML, the one people would not think to look for, was the
				half that was hidden. Naming the button for the question rather
				than for one answer puts both formats at the same depth.
			-->
			<div class="relative flex items-center">
				<button
					type="button"
					class="flex items-center gap-1.5 whitespace-nowrap rounded-md border border-neutral-300 px-3 py-1 text-sm font-medium text-neutral-700 hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-40 dark:border-[var(--border-subtle)] dark:text-neutral-200 dark:hover:bg-[var(--surface-card)]"
					disabled={!$previewState.url}
					aria-haspopup="menu"
					aria-expanded={downloadMenuOpen}
					onclick={toggleDownloadMenu}
				>
					{renderingImages ? 'Rendering…' : 'Download'}
					<span aria-hidden="true">▾</span>
				</button>

				{#if downloadMenuOpen}
					<button
						type="button"
						class="fixed inset-0 z-10 cursor-default"
						aria-label="Close menu"
						tabindex="-1"
						onclick={closeDownloadMenu}
					></button>
					<ul
						role="menu"
						aria-label="Download options"
						class="absolute right-0 top-full z-20 mt-1 w-40 rounded-md border border-neutral-200 bg-white py-1 text-sm shadow-lg dark:border-[var(--border-subtle)] dark:bg-[var(--surface-card)]"
					>
						<li role="none">
							<button
								role="menuitem"
								type="button"
								class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-neutral-800"
								onclick={downloadFromMenu}
							>
								PDF
							</button>
						</li>
						<li role="none">
							<!-- The PDF is the output; this is the source. Only the YAML
							can be edited again, here or by RenderCV's own CLI, which
							makes it the one worth keeping a copy of. -->
							<button
								role="menuitem"
								type="button"
								class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-neutral-800"
								onclick={downloadYamlFromMenu}
							>
								YAML
							</button>
						</li>
						<li role="none">
							<!-- Rendered on request, not alongside the preview: this is a
							second Typst compilation, and a multi-page CV arrives zipped
							because dropping the pages after the first would look like
							success. -->
							<button
								role="menuitem"
								type="button"
								class="w-full px-3 py-1.5 text-left hover:bg-neutral-100 dark:hover:bg-neutral-800"
								onclick={downloadImagesFromMenu}
							>
								Image
							</button>
						</li>
					</ul>
				{/if}

				{#if imageError}
					<p
						role="alert"
						class="absolute right-0 top-full z-20 mt-1 w-64 rounded-md bg-red-50 px-2 py-1.5 text-xs text-red-800 shadow-lg dark:bg-red-950 dark:text-red-200"
					>
						{imageError}
					</p>
				{/if}
			</div>

			<button
				type="button"
				class="grid h-7 w-7 place-items-center rounded-md text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)]"
				aria-label={$theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
				title={$theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
				onclick={() => theme.toggle()}
			>
				{#if $theme === 'dark'}
					<!-- Sun icon: shown in dark mode, click switches to light. -->
					<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
						<circle cx="12" cy="12" r="4" />
						<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
					</svg>
				{:else}
					<!-- Moon icon: shown in light mode, click switches to dark. -->
					<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
						<path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 1020.354 15.354z" />
					</svg>
				{/if}
			</button>
		</div>
	</div>

	<!-- Tab row: the four document tabs, plus the theme quick-switcher. -->
	<div
		class="flex flex-wrap items-center justify-between gap-y-1 border-b border-neutral-200 px-3 py-2 dark:border-[var(--border-subtle)]"
	>
		<div role="tablist" aria-label="CV sections" class="flex gap-1">
			{#each DOCUMENT_KEYS as key (key)}
				<button
					type="button"
					role="tab"
					id={`tab-${key}`}
					aria-selected={activeTab === key}
					aria-controls={`panel-${key}`}
					tabindex={activeTab === key ? 0 : -1}
					class={tabClass(key)}
					onclick={() => (activeTab = key)}
				>
					{DOCUMENT_LABELS[key]}
					{#if errorsForTab(key).length > 0}
						<span
							class="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-red-500"
							aria-label={`${errorsForTab(key).length} error(s) in ${DOCUMENT_LABELS[key]}`}
						></span>
					{/if}
				</button>
			{/each}
		</div>

		<div class="flex items-center gap-2">
			<ThemeSwitcher {themeNames} {currentTheme} onSwitch={switchTheme} />
			{#if currentThemeDefaults}
				<button
					type="button"
					data-testid="reset-theme-defaults"
					class="relative rounded-md border border-neutral-300 px-2 py-1 text-xs font-medium text-neutral-700 hover:bg-neutral-100 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent dark:border-[var(--border-subtle)] dark:text-neutral-200 dark:hover:bg-white/5"
					disabled={overrides.length === 0}
					title={overrides.length
						? `Customised (${overrides.length}): ${overrides.join(', ')}`
						: `Design matches the ${themeDisplayName(currentTheme)} defaults`}
					aria-label={overrides.length
						? `Reset design to ${themeDisplayName(currentTheme)} defaults (${overrides.length} customised option(s))`
						: `Design matches the ${themeDisplayName(currentTheme)} defaults`}
					onclick={() => (confirmingReset = true)}
				>
					Reset
					{#if overrides.length > 0}
						<span
							class="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-amber-500"
							aria-hidden="true"
						></span>
					{/if}
				</button>
			{/if}
		</div>
	</div>

	{#if themeMemoryNotice}
		<div
			role="status"
			data-testid="theme-memory-notice"
			class="flex items-start justify-between gap-3 border-b border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100"
		>
			<p>{themeMemoryNotice}</p>
			<button
				type="button"
				class="shrink-0 rounded-md border border-amber-400 px-2 py-0.5 text-xs font-medium hover:bg-amber-100 dark:hover:bg-amber-900"
				onclick={() => (themeMemoryNotice = null)}
			>
				Dismiss
			</button>
		</div>
	{/if}

	{#if confirmingReset && overrides.length > 0}
		<div
			role="alertdialog"
			aria-labelledby="reset-theme-title"
			class="border-b border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100"
		>
			<p id="reset-theme-title" class="font-medium">
				Reset design to {themeDisplayName(currentTheme)} defaults?
			</p>
			<p class="mt-0.5">
				{overrides.length} option(s) differ from the theme and will be replaced:
			</p>
			<ul class="mt-1 max-h-24 list-inside list-disc overflow-auto font-mono text-xs">
				{#each overrides as path (path)}
					<li>{path}</li>
				{/each}
			</ul>
			<div class="mt-2 flex items-center gap-2">
				<button
					type="button"
					class="rounded-md bg-amber-600 px-2.5 py-1 font-medium text-white hover:bg-amber-700"
					onclick={resetThemeDefaults}
				>
					Reset
				</button>
				<button
					type="button"
					class="rounded-md border border-amber-400 px-2.5 py-1 font-medium hover:bg-amber-100 dark:hover:bg-amber-900"
					onclick={() => (confirmingReset = false)}
				>
					Cancel
				</button>
			</div>
		</div>
	{/if}

	{#if $autosaveState.status === 'conflict'}
		<div
			role="alert"
			class="flex items-center justify-between gap-3 border-b border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100"
		>
			<span>CV này đã thay đổi ở nơi khác.</span>
			<div class="flex items-center gap-2">
				<button
					type="button"
					class="rounded-md border border-amber-400 px-2.5 py-1 font-medium hover:bg-amber-100 dark:hover:bg-amber-900"
					onclick={() => onResolveConflict?.('reload')}
				>
					Tải bản mới
				</button>
				<button
					type="button"
					class="rounded-md bg-amber-600 px-2.5 py-1 font-medium text-white hover:bg-amber-700"
					onclick={() => onResolveConflict?.('overwrite')}
				>
					Ghi đè
				</button>
			</div>
		</div>
	{:else if $autosaveState.status === 'error'}
		<div
			role="alert"
			class="flex items-center justify-between gap-3 border-b border-red-300 bg-red-50 px-3 py-2 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100"
		>
			<span>Could not save your changes.</span>
			<button
				type="button"
				class="rounded-md border border-red-400 px-2.5 py-1 font-medium hover:bg-red-100 dark:hover:bg-red-900"
				onclick={() => onRetrySave?.()}
			>
				Retry
			</button>
		</div>
	{/if}

	<div class="flex-1 overflow-auto p-3">
		<div
			id={`panel-${activeTab}`}
			role="tabpanel"
			aria-labelledby={`tab-${activeTab}`}
			class="h-full"
		>
			{#if yamlMode}
				<div class="h-full w-full rounded-md border border-neutral-200 bg-white dark:border-[var(--border-subtle)] dark:bg-[var(--surface)]">
					<YamlEditor
						bind:this={yamlEditor}
						activeKey={activeTab}
						errorsForKey={errorsForTab}
						bind:canUndo
						bind:canRedo
					/>
				</div>
			{:else if activeTab === 'cv'}
				<CvForm errors={errorsForTab('cv')} />
			{:else if activeTab === 'design'}
				<DesignForm syncState={designSyncState} submitOp={designSync.submitOp} errors={errorsForTab('design')} />
			{:else if activeTab === 'locale'}
				<LocaleForm errors={errorsForTab('locale')} />
			{:else}
				<SettingsForm errors={errorsForTab('settings')} />
			{/if}
		</div>
	</div>
</section>

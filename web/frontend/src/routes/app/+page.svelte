<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { get } from 'svelte/store';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import SignInGate from '$lib/components/SignInGate.svelte';
	import EditorPane from '$lib/components/EditorPane.svelte';
	import PreviewPane from '$lib/components/PreviewPane.svelte';
	import Splitter from '$lib/components/Splitter.svelte';
	import { splitRatio } from '$lib/stores/splitRatio';
	import { createRenderController } from '$lib/preview/renderController';
	import { createWasmRenderEngineIfSupported } from '$lib/wasm/clientRenderEngine';
	import { isWasmPreviewEnabled } from '$lib/wasm/featureFlag';
	import { createValidateController } from '$lib/preview/validateController';
	import { documents } from '$lib/stores/documents';
	import { cvs, activeCv, bootstrapping } from '$lib/stores/cvSession';
	import { createAutosaveController } from '$lib/persistence/autosave';
	import { createPreferenceWriter } from '$lib/persistence/preferenceWriter';
	import { theme } from '$lib/stores/theme';
	import { auth } from '$lib/stores/auth';
	import { bootstrapApp } from '$lib/app/bootstrap';
	import { createCvSessionActions } from '$lib/app/cvSessionActions';
	import { splitRendercvYaml } from '$lib/editor/exportYaml';
	import { listCvs, createCv, getCv } from '$lib/api/cvs';
	import { getPreferences } from '$lib/api/preferences';
	import type { ValidationError } from '$lib/api/validate';

	// Both controllers are created `startPaused: true` -- they do not
	// subscribe to `documents` (and so cannot fire a debounced network call)
	// until `activate()` is called, which happens in `onMount` right after
	// bootstrap has seeded `documents` with the real CV. Why this matters:
	// subscribing eagerly (the pre-Phase-4c behavior) reacts to whatever
	// `documents` holds the instant the component is created -- the
	// placeholder default content, since bootstrap is still an in-flight
	// `fetch`. That fires a real `/api/render` + `/api/validate` round trip
	// for content nobody will ever see, which (a) can complete and set
	// `previewState.url` to a blob *before* bootstrap ever replaces the
	// store, so a naive "the preview iframe has a blob: src" readiness
	// check is satisfied by stale content instead of the loaded CV, and (b)
	// adds avoidable backend load (a real Typst compile) that compounded
	// under parallel e2e workers into cross-test flakiness once every
	// `page.goto('/')` started paying for a full bootstrap round trip too
	// (confirmed by artificially delaying bootstrap -- see the phase notes).
	// Gated on the flag at *creation*, not just at selection: the engine's
	// constructor immediately boots its worker, which downloads Pyodide from
	// the CDN plus the rendercv wheel, the fonts and the typst compiler wasm
	// (tens of MB) before anything asks it to render. Constructing it
	// unconditionally would bill every visitor for a cold start whose result
	// `clientEngineUsable()` can never select while the flag is off -- the
	// opposite of this feature's "never costs anyone who hasn't opted in"
	// contract. Flipping the flag therefore takes effect on the next load,
	// which is how it is already documented and driven.
	const clientRenderEngine = isWasmPreviewEnabled() ? createWasmRenderEngineIfSupported() : null;

	const renderController = createRenderController(documents, {
		startPaused: true,
		clientRenderEngine: clientRenderEngine ?? undefined
	});
	const previewState = renderController.state;

	const validateController = createValidateController(documents, { startPaused: true });
	const validationState = validateController.state;

	// `autosave`/`cvSessionActions` are safe to create (and subscribe)
	// eagerly: both no-op until `setBaseline`/an explicit action call gives
	// them a CV id -- see `autosave.ts`'s `isDirty()` guard.
	const autosave = createAutosaveController(documents, activeCv);
	const autosaveState = autosave.state;

	const cvActions = createCvSessionActions({ cvs, activeCv, documents }, autosave);

	const prefWriter = createPreferenceWriter();

	// Account state, for the gate below and the sidebar's footer strip.
	const authStatus = auth.status;

	// Whether this visitor may open the editor at all. `null` while the
	// answer is still in flight, so the first paint shows neither the
	// editor nor the gate -- flashing "sign in" at someone who is signed
	// in would be worse than a moment of nothing.
	let signedIn = $state<boolean | null>(null);

	// Validate is the authoritative source for inline error placement (it
	// always includes yaml_source); if it hasn't reported anything wrong yet
	// but the render itself still failed (e.g. Typst/PDF generation
	// disabled), fall back to the render's own errors so nothing is missed.
	let errors = $derived<ValidationError[]>(
		$validationState.errors.length > 0 ? $validationState.errors : $previewState.errors
	);

	let editorPane: ReturnType<typeof EditorPane> | undefined = $state();
	let zoom = $state(100);
	let yamlMode = $state(true);
	let sidebarCollapsed = $state(false);
	let bootstrapReady = $state(false);
	let bootstrapError = $state<string | null>(null);

	function handleErrorClick(error: ValidationError): void {
		editorPane?.goToError(error);
	}

	function handleResolveConflict(action: 'reload' | 'overwrite'): void {
		const conflict = $autosaveState.conflict;
		if (action === 'reload' && conflict) {
			documents.set(conflict.documents);
		}
		autosave.resolveConflict(action);
	}

	function handleRetrySave(): void {
		autosave.retryNow();
	}

	async function handleSwitch(id: number): Promise<void> {
		await cvActions.switchTo(id);
	}

	async function handleCreate(): Promise<void> {
		await cvActions.createNew();
	}

	async function handleImportFile(file: File): Promise<string | null> {
		// Resolves to a message rather than throwing: the sidebar has to show
		// the user why their file was refused, and every refusal here is an
		// ordinary answer about the file, not a fault in the app.
		const outcome = splitRendercvYaml(await file.text());
		if (!outcome.ok) return outcome.reason;
		// The filename without its extension: the closest thing the file
		// carries to a name, and better than another "Untitled CV".
		await cvActions.importFrom(file.name.replace(/\.[^.]+$/, ''), outcome.documents);
		return null;
	}

	async function handleRename(id: number, name: string): Promise<void> {
		await cvActions.rename(id, name);
	}

	async function handleDuplicate(id: number): Promise<void> {
		await cvActions.duplicate(id);
	}

	async function handleDelete(id: number): Promise<void> {
		await cvActions.remove(id);
	}

	async function handleRestore(id: number, versionId: number): Promise<void> {
		await cvActions.restore(id, versionId);
	}

	function handleBeforeUnload(): void {
		autosave.flushBeforeUnload();
	}

	async function handleSignOut(): Promise<void> {
		// Flush first: signing out swaps this browser back to a fresh
		// anonymous session, and an autosave still on the wire would then be
		// writing as a user who no longer owns the CV.
		await autosave.flush();
		await auth.signOut();
		window.location.reload();
	}

	async function handleDeleteAccount(): Promise<void> {
		// Flush first, for the same reason signing out does: an autosave
		// still on the wire would otherwise arrive after the account is
		// gone and fail against a row that no longer exists.
		await autosave.flush();
		const deleted = await auth.deleteAccount();
		// Back to the landing page on success -- there is no account left
		// to show the editor to. On failure the editor stays as it was,
		// still signed in, which is the truth.
		if (deleted) window.location.href = '/';
	}

	onMount(() => {
		void (async () => {
			// Awaited before bootstrap, not alongside it: `/api/cvs` and
			// `/api/preferences` refuse callers without an account, so
			// loading first would spend two round trips to arrive at 401 and
			// then report it as "Failed to load your CVs" -- an error message
			// about the wrong thing entirely.
			await auth.refresh();
			signedIn = get(authStatus).authenticated;
			if (!signedIn) {
				// Nothing is loading, so the loading state has to end here or
				// the gate would never get to render.
				bootstrapping.set(false);
				return;
			}

			try {
				const preferences = await getPreferences();
				const result = await bootstrapApp({ listCvs, createCv, getCv, getPreferences: async () => preferences });

				cvs.set(result.cvsList);
				cvActions.loadInto(result.cv);

				// Only now does `documents` hold the real CV -- safe to let the
				// render/validate controllers start reacting to it (see the
				// comment where they're created).
				renderController.activate();
				validateController.activate();

				if (preferences.zoom) {
					const parsed = Number(preferences.zoom);
					if (Number.isFinite(parsed)) zoom = parsed;
				}
				if (preferences.yaml_mode !== undefined) yamlMode = preferences.yaml_mode !== 'false';
				if (preferences.sidebar_collapsed !== undefined) sidebarCollapsed = preferences.sidebar_collapsed === 'true';
				theme.applyPersistedPreference(preferences.ui_theme);
				splitRatio.applyPersistedPreference(preferences.split_ratio);

				if (preferences.last_cv_id !== String(result.cv.id)) {
					prefWriter.write('last_cv_id', String(result.cv.id));
				}
			} catch (error) {
				bootstrapError = error instanceof Error ? error.message : 'Failed to load your CVs.';
			} finally {
				bootstrapReady = true;
				bootstrapping.set(false);
			}
		})();
	});

	// Reactive preference writes -- guarded so the initial bootstrap read-back
	// (which sets these local variables from the server) never immediately
	// re-writes the same value back.
	$effect(() => {
		const id = $activeCv?.id;
		if (bootstrapReady && id !== undefined) prefWriter.write('last_cv_id', String(id));
	});
	$effect(() => {
		if (bootstrapReady) prefWriter.write('zoom', String(zoom));
	});
	$effect(() => {
		if (bootstrapReady) prefWriter.write('yaml_mode', String(yamlMode));
	});
	$effect(() => {
		if (bootstrapReady) prefWriter.write('sidebar_collapsed', String(sidebarCollapsed));
	});

	onDestroy(() => {
		// Owned here (created above), so it must be torn down here: nothing else
		// terminates the worker, and its Pyodide heap would outlive every
		// unmount -- SPA navigation away and back, or an HMR remount, would
		// leave a stack of live workers behind.
		clientRenderEngine?.dispose();
		renderController.destroy();
		validateController.destroy();
		autosave.destroy();
		prefWriter.destroy();
		splitRatio.destroy();
	});
</script>

<svelte:head>
	<title>RenderCV Editor</title>
</svelte:head>

<svelte:window onbeforeunload={handleBeforeUnload} />

<div
	class="flex h-screen w-screen overflow-hidden bg-white text-neutral-900 dark:bg-[var(--surface)] dark:text-neutral-100"
	data-app-ready={bootstrapReady && !bootstrapError ? 'true' : 'false'}
>
	{#if signedIn === false}
		<SignInGate providerAvailable={$authStatus.providerAvailable} />
	{:else if $bootstrapping}
		<div class="flex flex-1 items-center justify-center" role="status" aria-live="polite">
			<span class="text-sm text-neutral-500 dark:text-neutral-400">Loading your CVs…</span>
		</div>
	{:else if bootstrapError}
		<div class="flex flex-1 items-center justify-center" role="alert">
			<span class="text-sm text-red-600 dark:text-red-400">{bootstrapError}</span>
		</div>
	{:else}
		<Sidebar
			{cvs}
			{activeCv}
			bind:collapsed={sidebarCollapsed}
			onSwitch={handleSwitch}
			onCreate={handleCreate}
			onImportFile={handleImportFile}
			onRename={handleRename}
			onDuplicate={handleDuplicate}
			onDelete={handleDelete}
			onRestore={handleRestore}
			{authStatus}
			onSignOut={handleSignOut}
			onDeleteAccount={handleDeleteAccount}
		/>
		<main class="flex flex-1 overflow-hidden">
			<div class="min-w-0 shrink-0" style={`flex-basis: ${$splitRatio}%`}>
				<EditorPane
					bind:this={editorPane}
					{previewState}
					{errors}
					bind:zoom
					bind:yamlMode
					bind:sidebarCollapsed
					{autosaveState}
					onResolveConflict={handleResolveConflict}
					onRetrySave={handleRetrySave}
				/>
			</div>
			<Splitter ratio={$splitRatio} onChange={(next) => splitRatio.set(next)} />
			<div class="min-w-0 flex-1">
				<PreviewPane {previewState} {errors} {zoom} onErrorClick={handleErrorClick} />
			</div>
		</main>
	{/if}
</div>

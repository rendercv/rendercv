<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { Compartment } from '@codemirror/state';
	import { EditorView, keymap, lineNumbers, highlightActiveLine } from '@codemirror/view';
	import {
		defaultKeymap,
		history,
		historyKeymap,
		insertNewlineKeepIndent,
		undo,
		redo,
		undoDepth,
		redoDepth
	} from '@codemirror/commands';
	import { yaml } from '@codemirror/lang-yaml';
	import { indentUnit, HighlightStyle, syntaxHighlighting } from '@codemirror/language';
	import { tags as t } from '@lezer/highlight';
	import { linter, lintGutter, type Diagnostic } from '@codemirror/lint';
	import { documents, setDocument, type DocumentKey } from '$lib/stores/documents';
	import { theme, type ThemeMode } from '$lib/stores/theme';
	import type { ValidationError } from '$lib/api/validate';
	import {
		DocumentEditorRegistry,
		externalDocUpdate,
		isSyncTransaction,
		lineDiagnostic
	} from '$lib/editor/documentEditors';
	import { wrapSelection, wrapAsLink } from '$lib/editor/markdownToolbar';

	let {
		activeKey,
		errorsForKey = () => [],
		canUndo = $bindable(false),
		canRedo = $bindable(false)
	}: {
		activeKey: DocumentKey;
		/** Returns the validation errors that belong to a given document. */
		errorsForKey?: (key: DocumentKey) => ValidationError[];
		canUndo?: boolean;
		canRedo?: boolean;
	} = $props();

	let container: HTMLDivElement | undefined = $state();
	let view: EditorView | undefined;
	let registry: DocumentEditorRegistry | undefined;
	let unsubscribeStore: (() => void) | undefined;
	let unsubscribeTheme: (() => void) | undefined;

	const baseTheme = EditorView.theme({
		'&': {
			height: '100%',
			fontSize: '13px',
			backgroundColor: 'transparent'
		},
		'.cm-scroller': { fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace', overflow: 'auto' },
		'.cm-content': { padding: '0.5rem 0' },
		'&.cm-focused': { outline: 'none' },
		'.cm-gutters': { backgroundColor: 'transparent', border: 'none' }
	});

	/**
	 * Dark-mode-only overrides, swapped in/out via `themeCompartment` (see
	 * `applyThemeMode` below) so the light theme (`baseTheme` above) stays
	 * exactly as it was before dark mode existed. CodeMirror's own defaults
	 * (black cursor, light gutter/selection colors) are unreadable on a dark
	 * background -- the base text color itself needs no override here since
	 * it's inherited from the app root's `dark:text-neutral-100` (see
	 * `+page.svelte`).
	 */
	const darkTheme = EditorView.theme(
		{
			'.cm-gutters': { color: '#8a8f98' },
			'.cm-activeLine': { backgroundColor: 'rgba(255, 255, 255, 0.06)' },
			'.cm-activeLineGutter': { backgroundColor: 'rgba(255, 255, 255, 0.08)' },
			'.cm-cursor, .cm-dropCursor': { borderLeftColor: '#e5e5e5' },
			'&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
				backgroundColor: 'rgba(168, 85, 247, 0.35) !important'
			},
			'.cm-matchingBracket, .cm-nonmatchingBracket': {
				backgroundColor: 'rgba(168, 85, 247, 0.25)',
				color: 'inherit'
			}
		},
		{ dark: true }
	);

	/**
	 * Dark-mode token colors for YAML (Phase 5 wave 3 -- reference dark
	 * screenshots show keys in light blue and string/plain-scalar values in
	 * amber/orange, not the plain untinted text the editor had before this).
	 * Left as dark-only, same as `darkTheme` above: this codebase's light
	 * mode has never applied a `HighlightStyle` to the YAML editor (the
	 * grammar tags were there via `@lezer/yaml`, nothing consumed them) --
	 * this task's brief is explicit that light mode stays untouched, so
	 * rather than guess at a light palette that was never designed, only
	 * dark mode gets one.
	 *
	 * Tag source: `@lezer/yaml`'s own `styleTags` map -- `Key/Literal` and
	 * `Key/QuotedLiteral` are tagged `tags.definition(tags.propertyName)`
	 * (a key), `QuotedLiteral` is `tags.string`, and a bare/unquoted scalar
	 * (the common case: `name: John Doe`) is `tags.content`.
	 */
	const darkHighlightStyle = HighlightStyle.define([
		{ tag: t.propertyName, color: '#7dd3fc' }, // keys -- light blue
		{ tag: t.string, color: '#fbbf24' }, // quoted values -- amber
		{ tag: t.content, color: '#fbbf24' }, // plain (unquoted) scalar values -- amber
		{ tag: t.number, color: '#fbbf24' },
		{ tag: t.bool, color: '#c4b5fd' },
		{ tag: t.labelName, color: '#c4b5fd' }, // anchors/aliases
		{ tag: t.typeName, color: '#c4b5fd' }, // tags (!!str, custom tags)
		{ tag: t.keyword, color: '#c4b5fd' }, // directive names
		{ tag: t.comment, color: '#64748b', fontStyle: 'italic' },
		{ tag: t.meta, color: '#8a8f98' }
	]);

	/**
	 * One compartment, shared across all four documents' EditorStates (see
	 * `applyThemeMode`), so a theme change reconfigures every document in
	 * place instead of needing a fresh `extensionsFor` call.
	 */
	const themeCompartment = new Compartment();

	function themeExtension(mode: ThemeMode) {
		return mode === 'dark' ? [darkTheme, syntaxHighlighting(darkHighlightStyle)] : [];
	}

	/** Reconfigures every document's stored state (and the live view) to the given mode's theme extension. */
	function applyThemeMode(mode: ThemeMode): void {
		if (!registry) return;
		const effect = themeCompartment.reconfigure(themeExtension(mode));
		for (const key of ['cv', 'design', 'locale', 'settings'] as DocumentKey[]) {
			// The active key's state is kept live inside `view` (and mirrored
			// back into the registry by the update listener below) -- reconfigure
			// it through the view so it doesn't fight that mirroring.
			if (key === activeKey) continue;
			const state = registry.get(key);
			registry.set(key, state.update({ effects: effect }).state);
		}
		view?.dispatch({ effects: themeCompartment.reconfigure(themeExtension(mode)) });
	}

	function extensionsFor(key: DocumentKey) {
		return [
			lineNumbers(),
			highlightActiveLine(),
			history(),
			indentUnit.of('  '),
			yaml(),
			linter(null),
			lintGutter(),
			baseTheme,
			themeCompartment.of(themeExtension($theme)),
			// Plain "keep current indent" on Enter rather than the default
			// language-aware auto-indent: predictable for hand-edited YAML,
			// and matches the reference editor's plain-text feel.
			keymap.of([{ key: 'Enter', run: insertNewlineKeepIndent }, ...defaultKeymap, ...historyKeymap]),
			EditorView.updateListener.of((update) => {
				registry?.set(key, update.state);
				if (key === activeKey) {
					canUndo = undoDepth(update.state) > 0;
					canRedo = redoDepth(update.state) > 0;
				}
				if (update.docChanged) {
					const echo = update.transactions.some(isSyncTransaction);
					if (!echo) {
						setDocument(key, update.state.doc.toString());
					}
				}
			})
		];
	}

	function diagnosticsFor(key: DocumentKey): Diagnostic[] {
		const state = registry?.get(key);
		if (!state) return [];
		const out: Diagnostic[] = [];
		for (const error of errorsForKey(key)) {
			if (error.yaml_line === null) continue;
			const diagnostic = lineDiagnostic(state, error.yaml_line, error.message, 'error');
			if (diagnostic) out.push(diagnostic);
		}
		return out;
	}

	function refreshDiagnostics(key: DocumentKey): void {
		if (!registry) return;
		registry.setDiagnostics(key, diagnosticsFor(key));
	}

	onMount(() => {
		registry = new DocumentEditorRegistry($documents, extensionsFor);
		for (const key of ['cv', 'design', 'locale', 'settings'] as DocumentKey[]) {
			refreshDiagnostics(key);
		}

		view = new EditorView({
			state: registry.get(activeKey),
			parent: container
		});
		canUndo = undoDepth(view.state) > 0;
		canRedo = redoDepth(view.state) > 0;

		unsubscribeStore = documents.subscribe((docs) => {
			if (!registry) return;
			for (const key of ['cv', 'design', 'locale', 'settings'] as DocumentKey[]) {
				if (key === activeKey && view) {
					const spec = externalDocUpdate(view.state, docs[key]);
					if (spec) view.dispatch(spec);
				} else {
					registry.syncFromStore(key, docs[key]);
				}
			}
		});

		// The first call fires synchronously with the mode `extensionsFor`
		// already applied at construction -- a harmless no-op reconfigure.
		unsubscribeTheme = theme.subscribe((mode) => applyThemeMode(mode));
	});

	onDestroy(() => {
		unsubscribeStore?.();
		unsubscribeTheme?.();
		view?.destroy();
	});

	// Switch the live view's EditorState when the active tab changes, without
	// losing the outgoing tab's cursor/scroll/undo history (kept in registry).
	$effect(() => {
		const key = activeKey;
		if (!view || !registry) return;
		refreshDiagnostics(key);
		view.setState(registry.get(key));
		canUndo = undoDepth(view.state) > 0;
		canRedo = redoDepth(view.state) > 0;
	});

	/** Re-applies diagnostics whenever the caller's error set changes. */
	export function refreshAllDiagnostics(): void {
		if (!registry) return;
		for (const key of ['cv', 'design', 'locale', 'settings'] as DocumentKey[]) {
			refreshDiagnostics(key);
		}
		if (view) view.setState(registry.get(activeKey));
	}

	export function undoActive(): void {
		if (!view) return;
		undo(view);
	}

	export function redoActive(): void {
		if (!view) return;
		redo(view);
	}

	function applyWrap(result: { text: string; selectionStart: number; selectionEnd: number }): void {
		if (!view) return;
		view.dispatch({
			changes: { from: 0, to: view.state.doc.length, insert: result.text },
			selection: { anchor: result.selectionStart, head: result.selectionEnd }
		});
		view.focus();
	}

	export function wrapBold(): void {
		if (!view) return;
		const { from, to } = view.state.selection.main;
		applyWrap(wrapSelection(view.state.doc.toString(), from, to, '**', '**'));
	}

	export function wrapItalic(): void {
		if (!view) return;
		const { from, to } = view.state.selection.main;
		applyWrap(wrapSelection(view.state.doc.toString(), from, to, '*', '*'));
	}

	export function wrapLink(): void {
		if (!view) return;
		const { from, to } = view.state.selection.main;
		applyWrap(wrapAsLink(view.state.doc.toString(), from, to));
	}

	/** Switches focus to a line (1-indexed) in this document's editor. Caller switches the active tab first. */
	export function goToLine(line: number): void {
		if (!view) return;
		if (line < 1 || line > view.state.doc.lines) return;
		const { from } = view.state.doc.line(line);
		view.dispatch({ selection: { anchor: from }, scrollIntoView: true });
		view.focus();
	}
</script>

<div class="h-full w-full" bind:this={container}></div>

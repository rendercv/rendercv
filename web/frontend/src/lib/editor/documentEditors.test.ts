import { describe, it, expect } from 'vitest';
import { EditorState } from '@codemirror/state';
import { history, undo, redo, undoDepth } from '@codemirror/commands';
import { diagnosticCount } from '@codemirror/lint';
import {
	DocumentEditorRegistry,
	externalDocUpdate,
	isSyncTransaction,
	lineDiagnostic,
	syncAnnotation
} from './documentEditors';
import { linter, lintGutter } from '@codemirror/lint';
import type { CvDocuments } from '$lib/stores/documents';

function baseDocs(): CvDocuments {
	return {
		cv: 'cv:\n  name: John Doe\n',
		design: 'design:\n  theme: classic\n',
		locale: '',
		settings: ''
	};
}

// Mirrors the extensions every real document editor gets: undo history +
// the lint state field (so setDiagnostics has somewhere to write).
function extensions() {
	return [history(), linter(null), lintGutter()];
}

describe('externalDocUpdate / isSyncTransaction', () => {
	it('returns null when the text has not actually changed', () => {
		const state = EditorState.create({ doc: 'same' });
		expect(externalDocUpdate(state, 'same')).toBeNull();
	});

	it('builds a full-document replace tagged with the sync annotation', () => {
		const state = EditorState.create({ doc: 'old text' });
		const spec = externalDocUpdate(state, 'new text');
		expect(spec).not.toBeNull();

		const tr = state.update(spec!);
		expect(tr.state.doc.toString()).toBe('new text');
		expect(isSyncTransaction(tr)).toBe(true);
	});

	it('a normal user-typed transaction is not flagged as a sync echo', () => {
		const state = EditorState.create({ doc: 'abc' });
		const tr = state.update({ changes: { from: 3, insert: 'd' } });
		expect(isSyncTransaction(tr)).toBe(false);
	});
});

describe('DocumentEditorRegistry: per-document isolation', () => {
	it('keeps each of the four documents its own text', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		expect(registry.textFor('cv')).toBe('cv:\n  name: John Doe\n');
		expect(registry.textFor('design')).toBe('design:\n  theme: classic\n');
		expect(registry.textFor('locale')).toBe('');
		expect(registry.textFor('settings')).toBe('');
	});

	it('keeps separate undo histories per document', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);

		// Simulate the user typing in the "cv" tab.
		let cvState = registry.get('cv');
		cvState = cvState.update({ changes: { from: cvState.doc.length, insert: 'more' } }).state;
		registry.set('cv', cvState);

		// The "design" tab was never touched: it has nothing to undo.
		expect(undoDepth(registry.get('design'))).toBe(0);
		expect(undoDepth(registry.get('cv'))).toBeGreaterThan(0);

		// Undoing the cv tab does not touch the design tab's content.
		const undone = undo({
			state: registry.get('cv'),
			dispatch: (tr) => registry.set('cv', tr.state)
		});
		expect(undone).toBe(true);
		expect(registry.textFor('cv')).toBe('cv:\n  name: John Doe\n');
		expect(registry.textFor('design')).toBe('design:\n  theme: classic\n');
	});

	it('redo restores what undo just reverted, scoped to one document', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		let cvState = registry.get('cv');
		cvState = cvState.update({ changes: { from: cvState.doc.length, insert: 'X' } }).state;
		registry.set('cv', cvState);

		undo({ state: registry.get('cv'), dispatch: (tr) => registry.set('cv', tr.state) });
		expect(registry.textFor('cv')).toBe('cv:\n  name: John Doe\n');

		redo({ state: registry.get('cv'), dispatch: (tr) => registry.set('cv', tr.state) });
		expect(registry.textFor('cv')).toBe('cv:\n  name: John Doe\nX');
	});
});

describe('DocumentEditorRegistry: store -> editor sync', () => {
	it('syncFromStore updates an inactive document without a live view', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		const changed = registry.syncFromStore('locale', 'locale:\n  language: en\n');

		expect(changed).toBe(true);
		expect(registry.textFor('locale')).toBe('locale:\n  language: en\n');
	});

	it('is a no-op when the store value already matches the editor', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		const changed = registry.syncFromStore('cv', 'cv:\n  name: John Doe\n');
		expect(changed).toBe(false);
	});

	it('does not create a new undoable step for an external sync', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		registry.syncFromStore('cv', 'cv:\n  name: Jane Doe\n');
		// A sync-tagged change should not itself be undoable by the user,
		// since it did not originate from typing.
		expect(undoDepth(registry.get('cv'))).toBe(0);
	});
});

describe('DocumentEditorRegistry: diagnostics', () => {
	it('lineDiagnostic maps a 1-indexed line to a document range', () => {
		const state = EditorState.create({ doc: 'a\nb\nc\n' });
		const diagnostic = lineDiagnostic(state, 2, 'oops', 'error');
		expect(diagnostic).not.toBeNull();
		expect(state.doc.sliceString(diagnostic!.from, diagnostic!.to)).toBe('b');
	});

	it('lineDiagnostic returns null for an out-of-range line', () => {
		const state = EditorState.create({ doc: 'a\nb\n' });
		expect(lineDiagnostic(state, 99, 'oops', 'error')).toBeNull();
		expect(lineDiagnostic(state, 0, 'oops', 'error')).toBeNull();
	});

	it('setDiagnostics can annotate an inactive document, ready before it becomes active', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		const diagnostic = lineDiagnostic(registry.get('design'), 2, 'Unknown theme', 'error');
		registry.setDiagnostics('design', diagnostic ? [diagnostic] : []);

		expect(diagnosticCount(registry.get('design'))).toBe(1);
		// Other documents are unaffected.
		expect(diagnosticCount(registry.get('cv'))).toBe(0);
	});

	it('clearing diagnostics (empty array) removes previously set markers', () => {
		const registry = new DocumentEditorRegistry(baseDocs(), extensions);
		const diagnostic = lineDiagnostic(registry.get('cv'), 1, 'bad', 'error');
		registry.setDiagnostics('cv', diagnostic ? [diagnostic] : []);
		expect(diagnosticCount(registry.get('cv'))).toBe(1);

		registry.setDiagnostics('cv', []);
		expect(diagnosticCount(registry.get('cv'))).toBe(0);
	});
});

describe('syncAnnotation identity', () => {
	it('is a stable annotation type usable across calls', () => {
		const state = EditorState.create({ doc: 'x' });
		const tr = state.update({ changes: { from: 0, insert: 'y' }, annotations: syncAnnotation.of(true) });
		expect(tr.annotation(syncAnnotation)).toBe(true);
	});
});

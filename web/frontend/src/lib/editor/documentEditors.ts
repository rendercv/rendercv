import {
	Annotation,
	EditorState,
	Transaction,
	type Extension,
	type TransactionSpec
} from '@codemirror/state';
import { setDiagnostics, type Diagnostic } from '@codemirror/lint';
import { DOCUMENT_KEYS, type CvDocuments, type DocumentKey } from '$lib/stores/documents';

/**
 * Tags a transaction as originating from an external store write (as opposed
 * to direct user typing in the editor).
 *
 * Why: the document store and the CodeMirror editor are two views of the
 * same data (see the ui-implementation skill's "one store, two views" rule).
 * Without this tag, writing the store's value back into the editor would
 * fire the editor's own update listener, which would write to the store
 * again, forever. Editor-originated transactions are NOT tagged, so the
 * update listener knows to forward only those to the store.
 */
export const syncAnnotation = Annotation.define<true>();

/** True if any part of this transaction was caused by an external store sync. */
export function isSyncTransaction(tr: Transaction): boolean {
	return tr.annotation(syncAnnotation) === true;
}

/**
 * Builds the transaction that brings an EditorState's document in line with
 * a newer value from the CvDocuments store.
 *
 * Why a full-document replace: the store holds plain strings with no CST/
 * diff information, so a full replace is the only generally-correct sync;
 * simple cases (e.g. the same edit echoing back) are already short-circuited
 * by the identical-text check below, so this never fights the user's own
 * typing.
 *
 * @param state Current EditorState for the document being synced.
 * @param newDoc The store's latest text for this document.
 * @returns A transaction spec to dispatch, or null if the text hasn't
 *   actually changed (avoids clobbering cursor/selection for no reason).
 */
export function externalDocUpdate(state: EditorState, newDoc: string): TransactionSpec | null {
	const current = state.doc.toString();
	if (current === newDoc) return null;

	return {
		changes: { from: 0, to: state.doc.length, insert: newDoc },
		annotations: [syncAnnotation.of(true), Transaction.addToHistory.of(false)],
		selection: { anchor: Math.min(state.selection.main.anchor, newDoc.length) }
	};
}

/** Builds a Diagnostic covering a full 1-indexed line, or null if out of range. */
export function lineDiagnostic(
	state: EditorState,
	line: number,
	message: string,
	severity: Diagnostic['severity'],
	markClass?: string
): Diagnostic | null {
	if (!Number.isInteger(line) || line < 1 || line > state.doc.lines) return null;
	const { from, to } = state.doc.line(line);
	return { from, to: Math.max(to, from), message, severity, markClass };
}

/** Applies a diagnostics transaction to a (possibly inactive) EditorState. */
export function applyDiagnostics(state: EditorState, diagnostics: Diagnostic[]): EditorState {
	return state.update(setDiagnostics(state, diagnostics)).state;
}

/**
 * Holds one EditorState per CV document (cv/design/locale/settings), each
 * with its own undo history, cursor, and scroll position, so switching tabs
 * never loses editing context.
 *
 * Why a plain class instead of Svelte state: this is the "sync logic" the
 * ui-implementation skill asks to be unit-testable without mounting a
 * component or a real CodeMirror view (EditorState has no DOM dependency).
 */
export class DocumentEditorRegistry {
	private states = new Map<DocumentKey, EditorState>();

	constructor(
		initialDocs: CvDocuments,
		private readonly extensions: (key: DocumentKey) => Extension[]
	) {
		for (const key of DOCUMENT_KEYS) {
			this.states.set(key, EditorState.create({ doc: initialDocs[key], extensions: extensions(key) }));
		}
	}

	/** Current EditorState for a document (always defined for the four known keys). */
	get(key: DocumentKey): EditorState {
		const state = this.states.get(key);
		if (!state) throw new Error(`No editor state for document "${key}"`);
		return state;
	}

	/** Replaces the stored state for a key, e.g. after a live view's update. */
	set(key: DocumentKey, state: EditorState): void {
		this.states.set(key, state);
	}

	/**
	 * Brings a (possibly inactive) document's stored state in line with a new
	 * value from the store. Returns true if the state actually changed.
	 */
	syncFromStore(key: DocumentKey, newDoc: string): boolean {
		const state = this.get(key);
		const spec = externalDocUpdate(state, newDoc);
		if (!spec) return false;
		this.states.set(key, state.update(spec).state);
		return true;
	}

	/** Sets diagnostics on a (possibly inactive) document's stored state. */
	setDiagnostics(key: DocumentKey, diagnostics: Diagnostic[]): void {
		this.states.set(key, applyDiagnostics(this.get(key), diagnostics));
	}

	/** Current document text for a key, without needing a live view. */
	textFor(key: DocumentKey): string {
		return this.get(key).doc.toString();
	}
}

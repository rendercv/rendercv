import { writable } from 'svelte/store';
import type { CvSummary } from '$lib/api/cvs';

/** Metadata for the CV currently open in the editor (its four documents live in `$lib/stores/documents`). */
export interface ActiveCvMeta {
	id: number;
	name: string;
}

/** Every saved CV belonging to this session, as shown in the sidebar (newest-updated first). */
export const cvs = writable<CvSummary[]>([]);

/** The CV currently open in the editor, or `null` before bootstrap has resolved one. */
export const activeCv = writable<ActiveCvMeta | null>(null);

/** True while the initial `GET /api/cvs` (+ picking/loading a CV) is in flight. */
export const bootstrapping = writable<boolean>(true);

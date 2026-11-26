/**
 * Remembers each theme's design across a theme switch, per CV, on the server.
 *
 * Why: switching theme rewrites the whole design block (see
 * `EditorPane.switchTheme`), so a CV tuned to fit one page under Harvard
 * came back from a round trip through another theme as Harvard's defaults
 * -- and onto two pages. Leaving a theme now stores its design
 * (`PUT /api/cvs/{id}/theme-designs/{theme}`) and arriving at one asks for
 * it back, so a user who works on two machines gets the same design on
 * either. A per-tab copy covers the moments the server cannot be reached.
 */

import {
	getThemeDesign as getThemeDesignApi,
	putThemeDesign as putThemeDesignApi,
	type DesignMapping
} from '$lib/api/cvs';

export interface ThemeSwitchRequest {
	/** The open CV, or `null` before one has loaded (local memory only). */
	cvId: number | null;
	/** The theme being left. */
	fromTheme: string;
	/** The design being left, or anything else if the document is mid-edit or invalid. */
	fromDesign: unknown;
	/** The theme being switched to. */
	toTheme: string;
	/** `toTheme`'s defaults from `GET /api/themes`. */
	toDefaults: DesignMapping;
}

export interface ThemeSwitchOutcome {
	/** The design to write into the document. */
	design: DesignMapping;
	/** `true` when `design` is a remembered one rather than `toTheme`'s defaults. */
	restored: boolean;
	/**
	 * `true` when the design being left could not be stored on the server.
	 * It is still kept in this tab, but another device will not see it.
	 */
	rememberFailed: boolean;
}

export interface ThemeMemoryOptions {
	getThemeDesign?: typeof getThemeDesignApi;
	putThemeDesign?: typeof putThemeDesignApi;
}

export interface ThemeMemory {
	/** Stores the design being left, then picks the design to arrive at. */
	switchTheme: (request: ThemeSwitchRequest) => Promise<ThemeSwitchOutcome>;
}

function isDesignFor(value: unknown, theme: string): value is DesignMapping {
	return (
		typeof value === 'object' &&
		value !== null &&
		!Array.isArray(value) &&
		(value as DesignMapping).theme === theme
	);
}

export function createThemeMemory(options: ThemeMemoryOptions = {}): ThemeMemory {
	const { getThemeDesign = getThemeDesignApi, putThemeDesign = putThemeDesignApi } = options;

	/** Per-tab copies, keyed by `${cvId}:${theme}` so two CVs never share one. */
	const local = new Map<string, DesignMapping>();
	const keyFor = (cvId: number | null, theme: string): string => `${cvId ?? 'none'}:${theme}`;

	async function remember(
		cvId: number | null,
		theme: string,
		design: DesignMapping
	): Promise<boolean> {
		// A JSON round trip, not `structuredClone`: the design arrives as the
		// form's reactive proxy, which `structuredClone` refuses to copy.
		const copy = JSON.parse(JSON.stringify(design)) as DesignMapping;
		local.set(keyFor(cvId, theme), copy);
		if (cvId === null) return true;
		return putThemeDesign(cvId, theme, copy);
	}

	async function recall(cvId: number | null, theme: string): Promise<DesignMapping | undefined> {
		const localCopy = local.get(keyFor(cvId, theme));
		if (cvId === null) return localCopy;
		try {
			// The server's copy wins: it may come from the other device. The
			// local copy only fills in when the server has none -- a store
			// from this tab that failed -- or cannot be asked.
			return (await getThemeDesign(cvId, theme)) ?? localCopy;
		} catch {
			return localCopy;
		}
	}

	async function switchTheme(request: ThemeSwitchRequest): Promise<ThemeSwitchOutcome> {
		const { cvId, fromTheme, fromDesign, toTheme, toDefaults } = request;

		// Only a design that really belongs to the theme being left is
		// stored: a document that failed to parse has nothing trustworthy to
		// keep, and storing it would overwrite a good earlier copy.
		const storing = isDesignFor(fromDesign, fromTheme)
			? remember(cvId, fromTheme, fromDesign)
			: Promise.resolve(true);

		// Both requests at once: the switch waits on the slower, not the sum.
		const [stored, recalled] = await Promise.all([storing, recall(cvId, toTheme)]);

		if (isDesignFor(recalled, toTheme)) {
			return { design: recalled, restored: true, rememberFailed: !stored };
		}
		return { design: toDefaults, restored: false, rememberFailed: !stored };
	}

	return { switchTheme };
}

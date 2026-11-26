/**
 * Pure math for the editor/preview resizable split (Phase 5 wave 3).
 *
 * Kept dependency-free and side-effect-free on purpose: `Splitter.svelte`
 * (the pointer/keyboard-driven component) and `$lib/stores/splitRatio.ts`
 * (the persisted store) both call into this module, and it's the layer
 * unit-tested for the clamp/step/drag-math edge cases the acceptance
 * criteria calls out explicitly.
 */

/** Default editor:preview split -- an even 50/50, matching the reference. */
export const DEFAULT_SPLIT_RATIO = 50;

/** The divider cannot be dragged closer to either edge than this (percent of the container width). */
export const MIN_SPLIT_RATIO = 25;

/** The divider cannot be dragged further than this (percent of the container width). */
export const MAX_SPLIT_RATIO = 75;

/** ArrowLeft/ArrowRight keyboard step, in percentage points. */
export const SPLIT_RATIO_STEP = 2;

/** Clamps a ratio into the `[MIN_SPLIT_RATIO, MAX_SPLIT_RATIO]` range. */
export function clampSplitRatio(ratio: number): number {
	if (!Number.isFinite(ratio)) return DEFAULT_SPLIT_RATIO;
	return Math.min(MAX_SPLIT_RATIO, Math.max(MIN_SPLIT_RATIO, ratio));
}

/**
 * Computes the new ratio for a pointer drag: `startRatio` is the ratio when
 * the drag began, `deltaPx` is the pointer's horizontal movement since then,
 * and `containerWidthPx` is the width the ratio is a percentage of. Clamped
 * to the same bounds as every other entry point.
 */
export function ratioFromDrag(startRatio: number, deltaPx: number, containerWidthPx: number): number {
	if (containerWidthPx <= 0) return clampSplitRatio(startRatio);
	const deltaPercent = (deltaPx / containerWidthPx) * 100;
	return clampSplitRatio(startRatio + deltaPercent);
}

export type StepDirection = 'decrease' | 'increase';

/** ArrowLeft (`'decrease'`) / ArrowRight (`'increase'`) keyboard stepping, `SPLIT_RATIO_STEP` points at a time. */
export function stepSplitRatio(current: number, direction: StepDirection): number {
	const delta = direction === 'increase' ? SPLIT_RATIO_STEP : -SPLIT_RATIO_STEP;
	return clampSplitRatio(current + delta);
}

/** Parses a persisted preference string (`localStorage` mirror or `GET /api/preferences`) into a valid ratio, falling back to the default for anything unusable. */
export function parseSplitRatio(value: string | undefined | null): number {
	if (value === undefined || value === null) return DEFAULT_SPLIT_RATIO;
	const parsed = Number(value);
	if (!Number.isFinite(parsed)) return DEFAULT_SPLIT_RATIO;
	return clampSplitRatio(parsed);
}

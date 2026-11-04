import { describe, it, expect } from 'vitest';
import {
	DEFAULT_SPLIT_RATIO,
	MIN_SPLIT_RATIO,
	MAX_SPLIT_RATIO,
	SPLIT_RATIO_STEP,
	clampSplitRatio,
	ratioFromDrag,
	stepSplitRatio,
	parseSplitRatio
} from './splitRatio';

describe('clampSplitRatio', () => {
	it('passes values already inside the range through unchanged', () => {
		expect(clampSplitRatio(50)).toBe(50);
		expect(clampSplitRatio(MIN_SPLIT_RATIO)).toBe(MIN_SPLIT_RATIO);
		expect(clampSplitRatio(MAX_SPLIT_RATIO)).toBe(MAX_SPLIT_RATIO);
	});

	it('clamps values below the minimum', () => {
		expect(clampSplitRatio(0)).toBe(MIN_SPLIT_RATIO);
		expect(clampSplitRatio(-100)).toBe(MIN_SPLIT_RATIO);
	});

	it('clamps values above the maximum', () => {
		expect(clampSplitRatio(100)).toBe(MAX_SPLIT_RATIO);
		expect(clampSplitRatio(9999)).toBe(MAX_SPLIT_RATIO);
	});

	it('falls back to the default for non-finite input', () => {
		expect(clampSplitRatio(Number.NaN)).toBe(DEFAULT_SPLIT_RATIO);
		expect(clampSplitRatio(Number.POSITIVE_INFINITY)).toBe(DEFAULT_SPLIT_RATIO);
	});
});

describe('ratioFromDrag', () => {
	it('converts a rightward pixel delta into a proportional percentage increase', () => {
		// 100px of movement across a 1000px container is 10 percentage points.
		expect(ratioFromDrag(50, 100, 1000)).toBe(60);
	});

	it('converts a leftward pixel delta into a proportional percentage decrease', () => {
		expect(ratioFromDrag(50, -100, 1000)).toBe(40);
	});

	it('clamps the result to the min/max bounds', () => {
		expect(ratioFromDrag(50, -10_000, 1000)).toBe(MIN_SPLIT_RATIO);
		expect(ratioFromDrag(50, 10_000, 1000)).toBe(MAX_SPLIT_RATIO);
	});

	it('is a no-op clamp when the container has no width', () => {
		expect(ratioFromDrag(50, 100, 0)).toBe(50);
		expect(ratioFromDrag(90, 100, 0)).toBe(MAX_SPLIT_RATIO);
	});
});

describe('stepSplitRatio', () => {
	it('increases by the fixed step', () => {
		expect(stepSplitRatio(50, 'increase')).toBe(50 + SPLIT_RATIO_STEP);
	});

	it('decreases by the fixed step', () => {
		expect(stepSplitRatio(50, 'decrease')).toBe(50 - SPLIT_RATIO_STEP);
	});

	it('clamps at the boundaries instead of overshooting', () => {
		expect(stepSplitRatio(MAX_SPLIT_RATIO, 'increase')).toBe(MAX_SPLIT_RATIO);
		expect(stepSplitRatio(MIN_SPLIT_RATIO, 'decrease')).toBe(MIN_SPLIT_RATIO);
	});
});

describe('parseSplitRatio', () => {
	it('parses a valid numeric string', () => {
		expect(parseSplitRatio('42')).toBe(42);
	});

	it('clamps an out-of-range parsed value', () => {
		expect(parseSplitRatio('5')).toBe(MIN_SPLIT_RATIO);
		expect(parseSplitRatio('95')).toBe(MAX_SPLIT_RATIO);
	});

	it('falls back to the default for missing or invalid input', () => {
		expect(parseSplitRatio(undefined)).toBe(DEFAULT_SPLIT_RATIO);
		expect(parseSplitRatio(null)).toBe(DEFAULT_SPLIT_RATIO);
		expect(parseSplitRatio('not-a-number')).toBe(DEFAULT_SPLIT_RATIO);
	});
});

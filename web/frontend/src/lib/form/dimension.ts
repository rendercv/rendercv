/**
 * Parse/serialize helpers for typst-dimension strings (`"0.7in"`, `"10pt"`,
 * `"1.25em"`) — backs `DimensionField`'s number input + unit suffix.
 */

export const DIMENSION_UNITS = ['in', 'cm', 'mm', 'pt', 'em'] as const;
export type DimensionUnit = (typeof DIMENSION_UNITS)[number];

export interface ParsedDimension {
	amount: number;
	unit: DimensionUnit;
}

const DIMENSION_PATTERN = /^(-?\d*\.?\d+)\s*(in|cm|mm|pt|em)$/;

/** Parses a typst-dimension string into its numeric amount and unit, or `null` if it doesn't match the expected shape. */
export function parseDimension(value: string): ParsedDimension | null {
	const match = DIMENSION_PATTERN.exec(value.trim());
	if (!match) return null;
	return { amount: Number(match[1]), unit: match[2] as DimensionUnit };
}

/** Re-serializes an amount + unit back into the typst-dimension string form. */
export function serializeDimension(amount: number, unit: DimensionUnit): string {
	return `${amount}${unit}`;
}

import { describe, it, expect } from 'vitest';
import { parseDimension, serializeDimension, DIMENSION_UNITS } from './dimension';

describe('parseDimension / serializeDimension round trip', () => {
	it.each([
		['0.7in', 0.7, 'in'],
		['10pt', 10, 'pt'],
		['1.25em', 1.25, 'em'],
		['-0.1cm', -0.1, 'cm'],
		['3mm', 3, 'mm']
	] as const)('parses "%s" into { amount: %d, unit: "%s" } and re-serializes to the same string', (raw, amount, unit) => {
		const parsed = parseDimension(raw);
		expect(parsed).toEqual({ amount, unit });
		expect(serializeDimension(parsed!.amount, parsed!.unit)).toBe(raw);
	});

	it('returns null for a string with no recognized unit', () => {
		expect(parseDimension('a lot')).toBeNull();
		expect(parseDimension('10px')).toBeNull();
		expect(parseDimension('')).toBeNull();
	});

	it('tolerates surrounding whitespace and a space before the unit', () => {
		expect(parseDimension(' 0.7 in ')).toEqual({ amount: 0.7, unit: 'in' });
	});

	it('declares exactly the 5 typst dimension units the schema documents', () => {
		expect(DIMENSION_UNITS).toEqual(['in', 'cm', 'mm', 'pt', 'em']);
	});
});

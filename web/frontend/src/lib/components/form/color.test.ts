import { describe, it, expect } from 'vitest';
import { toHexColor } from './color';

describe('toHexColor', () => {
	it('accepts a bare 6-digit hex string', () => {
		expect(toHexColor('7fffd4')).toBe('#7fffd4');
	});

	it('accepts a hex string already prefixed with #', () => {
		expect(toHexColor('#7fffd4')).toBe('#7fffd4');
	});

	it('converts an rgb(...) string', () => {
		expect(toHexColor('rgb(0, 79, 144)')).toBe('#004f90');
	});

	it('converts an rgba(...) string, ignoring alpha', () => {
		expect(toHexColor('rgba(0, 79, 144, 0.5)')).toBe('#004f90');
	});

	it('returns null for a named CSS color (no hex conversion attempted)', () => {
		expect(toHexColor('Black')).toBeNull();
	});

	it('returns null for an hsl string', () => {
		expect(toHexColor('hsl(270, 60%, 70%)')).toBeNull();
	});
});

import { describe, it, expect, vi } from 'vitest';
import { deepMerge, isPathOverridden } from './effectiveValue';

describe('deepMerge', () => {
	it('overlays override keys onto base, keeping untouched base keys', () => {
		const base = { page: { size: 'us-letter', top_margin: '0.7in' }, colors: { body: 'black' } };
		const override = { page: { top_margin: '0.5in' } };

		expect(deepMerge(base, override)).toEqual({
			page: { size: 'us-letter', top_margin: '0.5in' },
			colors: { body: 'black' }
		});
	});

	it('passes base through unchanged when override is undefined', () => {
		const base = { theme: 'classic' };
		expect(deepMerge(base, undefined)).toBe(base);
	});

	it('replaces arrays wholly instead of merging element-by-element', () => {
		const base = { show_time_spans_in: ['experience'] };
		const override = { show_time_spans_in: ['experience', 'education'] };
		expect(deepMerge(base, override)).toEqual({ show_time_spans_in: ['experience', 'education'] });
	});

	it('replaces a scalar with the override scalar', () => {
		expect(deepMerge('default value', 'overridden value')).toBe('overridden value');
	});

	it('recurses through multiple levels of nesting', () => {
		const base = { typography: { font_size: { body: '10pt', name: '30pt' } } };
		const override = { typography: { font_size: { body: '11pt' } } };
		expect(deepMerge(base, override)).toEqual({
			typography: { font_size: { body: '11pt', name: '30pt' } }
		});
	});
});

describe('isPathOverridden', () => {
	const overrideTree = { design: { theme: 'ember', page: { top_margin: '0.5in' } } };

	it('is true for a path explicitly present in the override tree', () => {
		expect(isPathOverridden(overrideTree, ['design', 'page', 'top_margin'])).toBe(true);
		expect(isPathOverridden(overrideTree, ['design', 'theme'])).toBe(true);
	});

	it('is false for a path not present in the override tree (falls back to defaults)', () => {
		expect(isPathOverridden(overrideTree, ['design', 'page', 'bottom_margin'])).toBe(false);
		expect(isPathOverridden(overrideTree, ['design', 'colors', 'body'])).toBe(false);
	});

	it('is false against an empty tree (a blank document)', () => {
		expect(isPathOverridden({}, ['design', 'page', 'top_margin'])).toBe(false);
	});
});

describe('OverrideInfo.onReset (contract used by FieldRow/ArrayField)', () => {
	it('a delete op at the leaf path removes just that override, nothing else', () => {
		const submitOp = vi.fn();
		const onReset = (path: (string | number)[]) => submitOp({ op: 'delete', path });

		onReset(['design', 'page', 'top_margin']);

		expect(submitOp).toHaveBeenCalledWith({ op: 'delete', path: ['design', 'page', 'top_margin'] });
	});
});

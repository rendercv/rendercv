import { describe, it, expect } from 'vitest';
import {
	buildDiscriminatorSwitchOp,
	buildEnsurePathOps,
	buildResetFieldOp,
	buildSetFieldOp
} from './documentActions';

describe('buildDiscriminatorSwitchOp', () => {
	it('creates the top-key mapping from scratch when the document is blank', () => {
		expect(buildDiscriminatorSwitchOp('', 'design', 'theme', 'ember')).toEqual({
			op: 'set',
			path: ['design'],
			value: { theme: 'ember' }
		});
	});

	it('treats a whitespace-only document the same as blank', () => {
		expect(buildDiscriminatorSwitchOp('   \n  ', 'design', 'theme', 'sb2nov')).toEqual({
			op: 'set',
			path: ['design'],
			value: { theme: 'sb2nov' }
		});
	});

	it('only touches the discriminator key when the document already has content', () => {
		expect(buildDiscriminatorSwitchOp('design:\n  theme: classic\n', 'design', 'theme', 'ember')).toEqual({
			op: 'set',
			path: ['design', 'theme'],
			value: 'ember'
		});
	});

	it('works the same way for the locale document (language discriminator)', () => {
		expect(buildDiscriminatorSwitchOp('', 'locale', 'language', 'french')).toEqual({
			op: 'set',
			path: ['locale'],
			value: { language: 'french' }
		});
		expect(buildDiscriminatorSwitchOp('locale:\n  language: english\n', 'locale', 'language', 'french')).toEqual({
			op: 'set',
			path: ['locale', 'language'],
			value: 'french'
		});
	});
});

describe('buildSetFieldOp / buildResetFieldOp', () => {
	it('builds a set op at the top-key-prefixed path', () => {
		expect(buildSetFieldOp('design', ['page', 'top_margin'], '0.5in')).toEqual({
			op: 'set',
			path: ['design', 'page', 'top_margin'],
			value: '0.5in'
		});
	});

	it('builds a delete op at the top-key-prefixed path', () => {
		expect(buildResetFieldOp('design', ['page', 'top_margin'])).toEqual({
			op: 'delete',
			path: ['design', 'page', 'top_margin']
		});
	});
});

describe('buildEnsurePathOps', () => {
	it('creates every missing ancestor, shallowest first, on a completely empty tree', () => {
		expect(buildEnsurePathOps({}, ['design', 'page', 'top_margin'])).toEqual([
			{ op: 'set', path: ['design'], value: {} },
			{ op: 'set', path: ['design', 'page'], value: {} }
		]);
	});

	it('only creates the ancestors that are actually missing', () => {
		const tree = { design: { theme: 'ember' } }; // "design" exists, "design.page" doesn't
		expect(buildEnsurePathOps(tree, ['design', 'page', 'top_margin'])).toEqual([
			{ op: 'set', path: ['design', 'page'], value: {} }
		]);
	});

	it('creates nothing when every ancestor already exists (never overwrites existing content)', () => {
		const tree = { design: { page: { top_margin: '0.7in' } } };
		expect(buildEnsurePathOps(tree, ['design', 'page', 'top_margin'])).toEqual([]);
	});

	it('creates nothing for a single-segment path (no ancestor to ensure)', () => {
		expect(buildEnsurePathOps({}, ['design'])).toEqual([]);
	});

	it('seeds the top-key ancestor with topKeySeed instead of an empty object (discriminator requirement)', () => {
		expect(buildEnsurePathOps({}, ['design', 'page', 'top_margin'], { theme: 'classic' })).toEqual([
			{ op: 'set', path: ['design'], value: { theme: 'classic' } },
			{ op: 'set', path: ['design', 'page'], value: {} }
		]);
	});

	it('does not seed a non-top-key ancestor even when topKeySeed is given', () => {
		const tree = { design: { theme: 'ember' } };
		expect(buildEnsurePathOps(tree, ['design', 'page', 'top_margin'], { theme: 'ember' })).toEqual([
			{ op: 'set', path: ['design', 'page'], value: {} }
		]);
	});
});

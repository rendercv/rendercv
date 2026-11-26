import { describe, it, expect } from 'vitest';
import { wrapSelection, wrapAsLink } from './markdownToolbar';

describe('wrapSelection', () => {
	it('wraps a selected substring and keeps it selected', () => {
		const text = 'Hello world';
		// select "world" (indices 6..11)
		const result = wrapSelection(text, 6, 11, '**', '**');

		expect(result.text).toBe('Hello **world**');
		expect(result.text.slice(result.selectionStart, result.selectionEnd)).toBe('world');
	});

	it('places the cursor between markers when nothing is selected', () => {
		const text = 'Hello ';
		const result = wrapSelection(text, 6, 6, '*', '*');

		expect(result.text).toBe('Hello **');
		expect(result.selectionStart).toBe(result.selectionEnd);
		expect(result.selectionStart).toBe(7); // right after the opening marker
	});

	it('supports italics with single asterisks', () => {
		const result = wrapSelection('abc', 0, 3, '*', '*');
		expect(result.text).toBe('*abc*');
	});
});

describe('wrapAsLink', () => {
	it('wraps a selection as a markdown link and selects the url placeholder', () => {
		const text = 'Visit my site';
		// select "my site" (indices 6..13)
		const result = wrapAsLink(text, 6, 13, 'url');

		expect(result.text).toBe('Visit [my site](url)');
		expect(result.text.slice(result.selectionStart, result.selectionEnd)).toBe('url');
	});

	it('inserts a placeholder title when nothing is selected', () => {
		const result = wrapAsLink('', 0, 0, 'url', 'title');
		expect(result.text).toBe('[title](url)');
		expect(result.text.slice(result.selectionStart, result.selectionEnd)).toBe('url');
	});
});

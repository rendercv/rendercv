import { describe, it, expect } from 'vitest';
import { BUILT_IN_THEME_NAMES, themeDisplayName } from './displayName';

describe('themeDisplayName', () => {
	it('spells out the identifiers that are not words', () => {
		// The two that motivated this: everything else is already a word
		// with a capital letter missing, but these read as mashed-together
		// keys no matter how they are cased.
		expect(themeDisplayName('engineeringresumes')).toBe('Engineering Resumes');
		expect(themeDisplayName('engineeringclassic')).toBe('Engineering Classic');
	});

	it('capitalises the single-word identifiers', () => {
		expect(themeDisplayName('classic')).toBe('Classic');
		expect(themeDisplayName('ember')).toBe('Ember');
	});

	it('names every built-in theme', () => {
		// Guards against a theme being added to the API and silently
		// falling through to the computed fallback.
		for (const name of BUILT_IN_THEME_NAMES) {
			expect(themeDisplayName(name)).not.toBe(name);
		}
	});

	it('makes a readable name for a custom theme rather than showing the key', () => {
		// `rendercv create-theme` lets a deployment ship its own theme; it
		// must not be the one place in the UI still rendering a bare key.
		expect(themeDisplayName('my_custom_theme')).toBe('My custom theme');
		expect(themeDisplayName('acme-corp')).toBe('Acme corp');
	});

	it('never returns an empty label for a non-empty identifier', () => {
		// A name of only separators would otherwise collapse to '' and
		// render as an invisible, unclickable option.
		expect(themeDisplayName('_')).toBe('_');
	});
});

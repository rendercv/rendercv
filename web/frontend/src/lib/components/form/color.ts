/**
 * Best-effort conversion of the design schema's color string form
 * (`"rgb(0, 79, 144)"`, `"7fffd4"`, named CSS colors, ...) into a `#rrggbb`
 * hex string a native `<input type="color">` can display. Returns `null`
 * when the string isn't in a directly convertible form (e.g. an SVG color
 * keyword) — the swatch still shows the true color via a plain CSS
 * `background-color`, which accepts every one of these forms natively; only
 * the native color-picker input needs this conversion.
 */
export function toHexColor(input: string): string | null {
	const trimmed = input.trim();

	const hexMatch = /^#?([0-9a-fA-F]{6})$/.exec(trimmed);
	if (hexMatch) return `#${hexMatch[1]}`;

	const rgbMatch = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)$/.exec(trimmed);
	if (rgbMatch) {
		const [, r, g, b] = rgbMatch;
		return `#${[r, g, b]
			.map((n) => Math.min(255, Number(n)).toString(16).padStart(2, '0'))
			.join('')}`;
	}

	return null;
}

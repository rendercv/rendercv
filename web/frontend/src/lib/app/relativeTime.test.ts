import { describe, it, expect } from 'vitest';
import { formatRelativeTime } from './relativeTime';

describe('formatRelativeTime', () => {
	const now = new Date('2026-01-01T12:00:00Z');

	it('says "just now" for very recent times', () => {
		expect(formatRelativeTime('2026-01-01T11:59:30Z', now)).toBe('just now');
	});

	it('formats minutes ago', () => {
		expect(formatRelativeTime('2026-01-01T11:55:00Z', now)).toBe('5 minutes ago');
	});

	it('formats hours ago', () => {
		expect(formatRelativeTime('2026-01-01T09:00:00Z', now)).toBe('3 hours ago');
	});

	it('formats days ago', () => {
		expect(formatRelativeTime('2025-12-30T12:00:00Z', now)).toBe('2 days ago');
	});

	it('treats a timezone-designator-less timestamp (the API\'s actual shape) as UTC, not local time', () => {
		// The API serializes pydantic `datetime` values with no `Z`/offset --
		// they are UTC instants. Without normalization, `new Date(...)` would
		// parse this as local time and could be many hours off.
		expect(formatRelativeTime('2026-01-01T11:59:30.123456', now)).toBe('just now');
		expect(formatRelativeTime('2026-01-01T11:55:00.000000', now)).toBe('5 minutes ago');
	});
});

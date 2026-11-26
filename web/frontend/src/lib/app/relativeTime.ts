const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
	['year', 60 * 60 * 24 * 365],
	['month', 60 * 60 * 24 * 30],
	['week', 60 * 60 * 24 * 7],
	['day', 60 * 60 * 24],
	['hour', 60 * 60],
	['minute', 60]
];

/**
 * Normalizes a backend timestamp to one `Date` can parse as UTC.
 *
 * Why: the API's `updated_at`/`created_at` fields are pydantic `datetime`
 * values serialized without a timezone designator (e.g.
 * `"2026-08-26T13:06:25.376218"`, no trailing `Z` or `+HH:MM`) -- they are
 * UTC instants (the backend never attaches a local timezone), but
 * `new Date(...)` treats a designator-less ISO string as *local* time. On a
 * host that isn't UTC, that silently shifts every timestamp by the local
 * offset (verified: parsing the exact string above from a UTC+7 host lands
 * 7 hours in the past). Appending `Z` when no designator is present fixes
 * the interpretation without needing a backend change.
 */
function parseServerTimestamp(iso: string): Date {
	const hasTimezone = /[zZ]$|[+-]\d{2}:\d{2}$/.test(iso);
	return new Date(hasTimezone ? iso : `${iso}Z`);
}

/**
 * Formats an ISO timestamp as a short relative-time string ("2 minutes
 * ago", "just now") for the CV list sidebar.
 *
 * @param iso - The timestamp to format.
 * @param now - The current time (injectable for tests); defaults to `new Date()`.
 */
export function formatRelativeTime(iso: string, now: Date = new Date()): string {
	const then = parseServerTimestamp(iso);
	const diffSeconds = Math.round((now.getTime() - then.getTime()) / 1000);

	if (diffSeconds < 45) return 'just now';

	const formatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
	for (const [unit, secondsInUnit] of UNITS) {
		if (diffSeconds >= secondsInUnit) {
			const value = Math.round(diffSeconds / secondsInUnit);
			return formatter.format(-value, unit);
		}
	}
	return formatter.format(-diffSeconds, 'second');
}

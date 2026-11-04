/**
 * Fixed English month reference labels for the Locale form's two 12-row
 * tables — the *label* column is always the English month regardless of
 * the CV's language (matching the schema's own English defaults); only the
 * *value* column (the translation) changes per language.
 */

export const ENGLISH_MONTH_NAMES = [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December'
] as const;

export const ENGLISH_MONTH_ABBREVIATIONS = [
	'Jan',
	'Feb',
	'Mar',
	'Apr',
	'May',
	'June',
	'July',
	'Aug',
	'Sept',
	'Oct',
	'Nov',
	'Dec'
] as const;

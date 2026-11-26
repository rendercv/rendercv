import type { ValidationError } from '$lib/api/validate';
import type { PathSegment } from './patchOps';
import { pathKey } from './patchOps';

/**
 * Maps `/api/validate` errors onto form fields by `location` path-prefix
 * match, so a field's inline error slot (see `FieldRow`) shows exactly the
 * errors that apply to it — in either exact-leaf mode (a scalar field) or
 * prefix mode (e.g. "show a marker on this entry if any of its fields are
 * invalid").
 *
 * Errors with `location: null`, or whose location isn't under `cv.` at all
 * (a design/locale/settings error, or one the core couldn't localize), are
 * NOT claimed here — they stay in the top-level error bar exactly as today.
 */

/** Errors whose `location` is exactly this path. */
export function errorsAtPath(errors: ValidationError[], path: PathSegment[]): ValidationError[] {
	const key = pathKey(path);
	return errors.filter((e) => e.location === key);
}

/** Errors whose `location` is this path, or nested under it (`path` itself or `path.<anything>`). */
export function errorsUnderPath(errors: ValidationError[], path: PathSegment[]): ValidationError[] {
	const key = pathKey(path);
	return errors.filter((e) => e.location === key || e.location?.startsWith(`${key}.`));
}

/** True if none of `errors` are claimed by any field under `cv` (so the error bar should still show them). */
export function hasUnclaimedErrors(errors: ValidationError[]): boolean {
	return errors.some((e) => !e.location || !e.location.startsWith('cv.'));
}

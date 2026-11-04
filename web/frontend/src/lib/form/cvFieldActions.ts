import type { PatchOp } from './patchOps';

/** Sets one top-level `cv.<key>` field (header fields, `social_networks`, `custom_connections`) to a whole new value. */
export function buildSetCvFieldOp(key: string, value: unknown): PatchOp {
	return { op: 'set', path: ['cv', key], value };
}

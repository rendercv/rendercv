import { redirect } from '@sveltejs/kit';

/**
 * `/welcome` was the landing page's address before Phase 6 moved it to `/`
 * (and the editor to `/app`). Anything already pointing here -- a bookmark,
 * a shared link, the older builds' sidebar "About" link -- must keep
 * working rather than hitting a 404, so this redirects permanently to the
 * landing page's new home.
 *
 * Why 308 and not 302: the move is permanent, and 308 (unlike 301) is
 * guaranteed not to rewrite the method, so it is the correct permanent
 * redirect for any request shape.
 */
export function load(): never {
	redirect(308, '/');
}

/**
 * Renders the privacy policy to HTML at build time.
 *
 * Why this page in particular, when only the landing page was prerendered
 * before: Google's OAuth review fetches this URL and reads what comes
 * back. Left to the SPA fallback it would answer with an empty shell, and
 * a policy that only exists after JavaScript runs is, to a reviewer or a
 * crawler, a policy that does not exist.
 *
 * The page reads nothing from the API, so there is nothing to defer.
 */
export const prerender = true;

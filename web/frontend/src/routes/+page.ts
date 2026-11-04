/**
 * Renders the landing page to HTML at build time.
 *
 * Why only this route: it is the one page whose content is known without
 * asking the server anything, and the one people arrive at from a link or
 * a search result. Left to the SPA fallback it would be served as an empty
 * shell, so a crawler -- or anyone reading before the JavaScript
 * runs -- would see nothing at all.
 *
 * `/app` is deliberately not prerendered. Everything on it comes from the
 * API and requires a signed-in account, so there is no useful HTML to
 * produce ahead of time.
 */
export const prerender = true;

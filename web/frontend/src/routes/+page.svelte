<script lang="ts">
	/**
	 * `/welcome` — the static landing page (Phase 5c). Reproduces the
	 * structure the plan documents from the observed rendercv.com landing
	 * page (docs/plans/completed/cv-editor-web-app.md, Context, "Landing page"),
	 * adapted for a self-hosted clone: honest copy, no fake testimonials, no
	 * star counts, no payment CTA.
	 *
	 * Fully static and self-contained: no store, no `/api/*` call, no
	 * dependency on the app's own light/dark theme (the reference is
	 * always-dark hero regardless of viewer preference). This lets it render
	 * standalone in tests without a backend.
	 */
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import LandingNav from '$lib/components/landing/LandingNav.svelte';
	import LandingHero from '$lib/components/landing/LandingHero.svelte';
	import ThemesStrip from '$lib/components/landing/ThemesStrip.svelte';
	import FaqAccordion from '$lib/components/landing/FaqAccordion.svelte';
	import FooterCta from '$lib/components/landing/FooterCta.svelte';

	// The one request this page makes, and it is deliberately not awaited by
	// anything that renders: `getAuthStatus` never throws, so a backend that
	// is down or has no Google credentials simply leaves `providerAvailable`
	// false and the page renders complete, minus a sign-in link that could
	// not have worked anyway.
	const authStatus = auth.status;
	onMount(() => {
		void auth.refresh();
	});
</script>

<svelte:head>
	<title>RenderCV — YAML-first resume builder</title>
	<meta
		name="description"
		content="A self-hosted, open-source editor for RenderCV: write your CV in YAML or a guided form, preview the typeset PDF live, and export with any of 9 built-in themes."
	/>
</svelte:head>

<div class="min-h-screen bg-neutral-950 text-neutral-100">
	<LandingNav
		providerAvailable={$authStatus.providerAvailable}
		authenticated={$authStatus.authenticated}
		displayName={$authStatus.displayName ?? $authStatus.email}
	/>
	<main>
		<LandingHero />
		<ThemesStrip />
		<FaqAccordion />
	</main>
	<FooterCta />
</div>

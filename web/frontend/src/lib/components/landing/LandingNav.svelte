<script lang="ts">
	/**
	 * Top nav for the landing page. Self-contained dark styling (the
	 * reference is a dark hero regardless of the app's own light/dark theme
	 * setting) -- this route does not read or write the app's theme store,
	 * it simply always renders dark.
	 *
	 * `providerAvailable` defaults to false so the sign-in link is absent
	 * until the server has actually said sign-in works. That default is also
	 * what renders if the backend is unreachable: the page still shows
	 * everything else rather than offering a link that cannot work.
	 *
	 * `authenticated` hides the sign-in link for someone who already has a
	 * session. Offering it to them was not merely redundant: following it
	 * runs the whole authorization-code flow again, and because
	 * `/google/start` sends `prompt=select_account` -- which is what makes
	 * switching accounts possible at all -- it puts Google's account chooser
	 * in front of a person who only wanted to open the editor. The fix
	 * belongs here rather than in the OAuth request, which is doing the
	 * right thing for the case it is for.
	 */
	import BrandMark from '$lib/components/BrandMark.svelte';
	import { GOOGLE_SIGN_IN_PATH } from '$lib/api/auth';

	let {
		providerAvailable = false,
		authenticated = false,
		displayName = null
	}: {
		providerAvailable?: boolean;
		authenticated?: boolean;
		displayName?: string | null;
	} = $props();
</script>

<header class="sticky top-0 z-20 border-b border-white/10 bg-neutral-950/80 backdrop-blur">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
		<a href="/" class="flex items-center gap-2 text-neutral-100" aria-label="RenderCV home">
			<span class="text-purple-400"><BrandMark /></span>
			<span class="text-lg font-semibold tracking-tight">RenderCV</span>
		</a>

		<div class="flex items-center gap-2">
			{#if authenticated}
				{#if displayName}
					<span class="hidden text-sm text-neutral-400 sm:inline" data-testid="signed-in-as">
						{displayName}
					</span>
				{/if}
			{:else if providerAvailable}
				<a
					href={GOOGLE_SIGN_IN_PATH}
					data-sveltekit-reload
					class="rounded-md px-3 py-1.5 text-sm font-medium text-neutral-300 transition-colors hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
				>
					Sign in
				</a>
			{/if}
			<a
				href="/app"
				class="rounded-md bg-purple-600 px-3.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-purple-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-950"
			>
				Open the editor
			</a>
		</div>
	</div>
</header>

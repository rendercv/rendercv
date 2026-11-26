<script lang="ts">
	/**
	 * What `/app` shows to someone who is not signed in.
	 *
	 * Why the editor needs a gate at all: `/api/cvs` and `/api/preferences`
	 * refuse callers without an account, so an unauthenticated visitor who
	 * reached the editor would meet a wall of 401s with nothing explaining
	 * them. This says the thing the 401s cannot.
	 *
	 * Why one button covers both signing up and signing in: with Google
	 * there is no separate registration step. A first-time visitor and a
	 * returning one press the same control; the difference is invisible to
	 * this component and is resolved server-side by whether the Google
	 * identity is already attached to an account.
	 *
	 * Why the unavailable case is handled rather than hidden: a deployment
	 * with no OAuth credentials configured can no longer be used at all,
	 * and rendering a dead button would leave the operator guessing. The
	 * message names the configuration that is missing.
	 */
	const { providerAvailable }: { providerAvailable: boolean } = $props();
</script>

<div class="flex flex-1 items-center justify-center px-6">
	<div class="max-w-md text-center">
		{#if providerAvailable}
			<h1 class="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
				Sign in to open the editor
			</h1>
			<p class="mt-3 text-sm text-neutral-600 dark:text-neutral-400">
				Your CVs are saved to your account, so they are still here on your next visit and on
				your other devices. First time? Signing in with Google creates the account — there is
				no separate sign-up.
			</p>
			<a
				href="/api/auth/google/start"
				class="mt-6 inline-flex items-center justify-center rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-300"
			>
				Sign in with Google
			</a>
		{:else}
			<h1 class="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
				Sign-in is not configured
			</h1>
			<p class="mt-3 text-sm text-neutral-600 dark:text-neutral-400">
				The editor stores CVs against an account, and this deployment has no sign-in provider
				set up, so there is no way in. Whoever runs it needs to set
				<code class="rounded bg-neutral-100 px-1 py-0.5 dark:bg-neutral-800"
					>GOOGLE_OAUTH_CLIENT_ID</code
				>
				and
				<code class="rounded bg-neutral-100 px-1 py-0.5 dark:bg-neutral-800"
					>GOOGLE_OAUTH_CLIENT_SECRET</code
				>.
			</p>
		{/if}
		<p class="mt-6 text-sm">
			<a class="text-neutral-500 underline hover:text-neutral-800 dark:hover:text-neutral-200" href="/"
				>Back to the home page</a
			>
		</p>
	</div>
</div>

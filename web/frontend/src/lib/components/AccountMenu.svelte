<script lang="ts">
	/**
	 * The account strip in the editor sidebar's footer: who you are signed in
	 * as, or an invitation to sign in.
	 *
	 * Why it can render nothing at all: a deployment with no Google
	 * credentials is fully supported (the editor works anonymously), and
	 * offering a button that can only produce a 503 would be worse than
	 * offering nothing. `providerAvailable` comes from the server, so the
	 * deployment decides, not the build.
	 */
	import type { Readable } from 'svelte/store';
	import type { AuthStatus } from '$lib/api/auth';
	import { GOOGLE_SIGN_IN_PATH } from '$lib/api/auth';

	let {
		status,
		onSignOut,
		onDeleteAccount
	}: {
		status: Readable<AuthStatus>;
		onSignOut: () => void;
		onDeleteAccount: () => void;
	} = $props();

	// Deleting an account cannot be undone, and the control sits beside
	// "Sign out" -- two words apart from something people click without
	// reading. So it is two steps, and the second one spells out what goes.
	let confirming = $state(false);

	// Prefer the name, fall back to the email, and never render an empty
	// strip: Google always supplies at least one of them, but a provider
	// that supplies neither must not produce a blank row.
	const label = $derived($status.displayName ?? $status.email ?? 'Signed in');
</script>

{#if $status.providerAvailable}
	<div
		class="flex items-center gap-1 border-t border-neutral-200 p-2 dark:border-[var(--border-subtle)]"
	>
		{#if $status.authenticated}
			<span
				class="flex min-w-0 flex-1 items-center gap-1.5 px-2 py-1.5 text-xs font-medium text-neutral-500 dark:text-neutral-400"
				title={$status.email ?? label}
			>
				<svg
					viewBox="0 0 24 24"
					width="13"
					height="13"
					fill="none"
					stroke="currentColor"
					stroke-width="1.8"
					aria-hidden="true"
					class="shrink-0"
				>
					<circle cx="12" cy="8" r="3.5" />
					<path d="M4.5 20a7.5 7.5 0 0 1 15 0" stroke-linecap="round" />
				</svg>
				<span class="truncate">{label}</span>
			</span>
			<button
				type="button"
				onclick={onSignOut}
				class="rounded-md px-2 py-1.5 text-xs font-medium text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 dark:text-neutral-400 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-200"
			>
				Sign out
			</button>
			<button
				type="button"
				onclick={() => (confirming = true)}
				aria-label="Delete account"
				title="Delete account"
				class="rounded-md px-2 py-1.5 text-xs font-medium text-neutral-400 hover:bg-red-50 hover:text-red-700 dark:text-neutral-500 dark:hover:bg-red-950 dark:hover:text-red-300"
			>
				Delete
			</button>
		{:else}
			<!-- A link, not a button: the OAuth flow is a full-page redirect to
			     Google, so the browser must navigate rather than fetch. -->
			<a
				href={GOOGLE_SIGN_IN_PATH}
				data-sveltekit-reload
				class="flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-800 dark:text-neutral-300 dark:hover:bg-[var(--surface-card)] dark:hover:text-neutral-100"
			>
				<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true" class="shrink-0">
					<path
						fill="#4285F4"
						d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5a5.6 5.6 0 0 1-2.4 3.7v3h3.9c2.3-2.1 3.5-5.2 3.5-8.9Z"
					/>
					<path
						fill="#34A853"
						d="M12 24c3.2 0 5.9-1.1 7.9-2.9l-3.9-3c-1.1.7-2.4 1.2-4 1.2-3.1 0-5.7-2.1-6.6-4.9H1.4v3.1A12 12 0 0 0 12 24Z"
					/>
					<path fill="#FBBC05" d="M5.4 14.4a7.2 7.2 0 0 1 0-4.6V6.7H1.4a12 12 0 0 0 0 10.8l4-3.1Z" />
					<path
						fill="#EA4335"
						d="M12 4.8c1.8 0 3.3.6 4.6 1.8l3.4-3.4A12 12 0 0 0 1.4 6.7l4 3.1C6.3 6.9 8.9 4.8 12 4.8Z"
					/>
				</svg>
				Sign in with Google
			</a>
		{/if}
	</div>

	{#if confirming}
		<div
			role="alertdialog"
			aria-label="Delete account?"
			class="border-t border-red-200 bg-red-50 p-3 text-xs dark:border-red-900 dark:bg-red-950"
		>
			<p class="mb-2 text-red-900 dark:text-red-200">
				Delete your account? Every CV, its version history and your preferences go with
				it. This cannot be undone.
			</p>
			<div class="flex justify-end gap-2">
				<button
					type="button"
					class="rounded-md border border-neutral-300 px-2.5 py-1 text-neutral-700 dark:border-[var(--border-subtle)] dark:text-neutral-200"
					onclick={() => (confirming = false)}
				>
					Cancel
				</button>
				<button
					type="button"
					class="rounded-md bg-red-600 px-2.5 py-1 font-medium text-white hover:bg-red-700"
					onclick={() => {
						confirming = false;
						onDeleteAccount();
					}}
				>
					Delete account
				</button>
			</div>
		</div>
	{/if}
{/if}

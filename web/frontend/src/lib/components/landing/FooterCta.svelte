<script lang="ts">
	/**
	 * Closing CTA + footer links. The `rendercv` GitHub link is the upstream
	 * OSS project, not this fork. The privacy link is reachable from every
	 * visitor's first screen on purpose: it is the address Google's OAuth
	 * consent screen points at, and the only route to a deletion request for
	 * someone who can no longer sign in.
	 */
</script>

<section class="border-t border-white/10 bg-gradient-to-b from-neutral-950 to-neutral-900 py-20 text-center">
	<div class="mx-auto max-w-2xl px-4 sm:px-6">
		<h2 class="text-2xl font-semibold text-neutral-100 sm:text-3xl">Ready to build your CV?</h2>
		<p class="mt-3 text-neutral-400">
			Sign in with Google, then start from a blank CV or one of the 9 built-in themes.
		</p>
		<a
			href="/app"
			class="mt-6 inline-block rounded-md bg-purple-600 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-purple-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-950"
		>
			Open the editor
		</a>
	</div>
</section>

<footer class="border-t border-white/10 bg-neutral-950 py-8">
	<div class="mx-auto flex max-w-6xl flex-col items-center gap-3 px-4 text-sm text-neutral-500 sm:flex-row sm:justify-between sm:px-6">
		<span>&copy; {new Date().getFullYear()} RenderCV Web Editor.</span>
		<div class="flex items-center gap-4">
			<a
				href="/privacy"
				class="rounded text-neutral-400 underline decoration-neutral-700 underline-offset-4 hover:text-neutral-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
			>
				Privacy
			</a>
			<a
				href="https://github.com/rendercv/rendercv"
				target="_blank"
				rel="noopener noreferrer"
				class="rounded text-neutral-400 underline decoration-neutral-700 underline-offset-4 hover:text-neutral-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
			>
				Powered by RenderCV (open source)
			</a>
		</div>
	</div>
</footer>

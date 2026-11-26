<script lang="ts">
	/**
	 * The 9 built-in themes as pill badges (mirrors the reference's "N themes"
	 * strip).
	 *
	 * Why the names come from `$lib/themes/displayName` rather than a list
	 * written out here: this strip used to carry its own spelling of all
	 * nine, while the editor's theme switcher showed the raw identifiers,
	 * so the same theme went by two names in one app with nothing keeping
	 * them in step. Both now read from the same place.
	 */
	import { BUILT_IN_THEME_NAMES, themeDisplayName } from '$lib/themes/displayName';
</script>

<section class="border-t border-white/10 bg-neutral-950 py-14" aria-labelledby="themes-heading">
	<div class="mx-auto max-w-6xl px-4 text-center sm:px-6">
		<h2 id="themes-heading" class="text-sm font-semibold uppercase tracking-wide text-purple-400">
			9 built-in themes
		</h2>
		<p class="mx-auto mt-2 max-w-xl text-sm text-neutral-400">
			Every theme is a Typst template that ships with this project — pick one, switch anytime, no
			extra install.
		</p>
		<ul class="mt-6 flex flex-wrap items-center justify-center gap-2">
			{#each BUILT_IN_THEME_NAMES as theme, i (theme)}
				<li
					class="reveal rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-sm text-neutral-200"
					style={`animation-delay:${i * 60}ms`}
				>
					{themeDisplayName(theme)}
				</li>
			{/each}
		</ul>
	</div>
</section>

<style>
	.reveal {
		opacity: 0;
		animation: pill-in 0.5s ease-out forwards;
	}

	@keyframes pill-in {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.reveal {
			animation: none;
			opacity: 1;
		}
	}
</style>

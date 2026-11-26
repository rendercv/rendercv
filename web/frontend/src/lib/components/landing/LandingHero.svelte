<script lang="ts">
	import ThemeShowcase from '$lib/components/landing/ThemeShowcase.svelte';

	const features: { title: string; description: string }[] = [
		{
			title: 'Industry-standard themes',
			description: 'Classic, Moderncv, Harvard, and 6 more — the same Typst templates RenderCV ships on the command line.'
		},
		{
			title: 'Form editor or YAML',
			description: 'Every field has a guided form row and a plain-text view. Switch anytime; both stay in sync.'
		},
		{
			title: 'Live PDF preview',
			description: 'Edit a field and the typeset PDF updates a moment later — no manual "compile" step.'
		},
		{
			title: 'Multilanguage support',
			description: 'Locale-aware date formats and translated section headings, built into the Locale tab.'
		},
		{
			title: 'Your data stays on this server',
			description: 'Sign in with Google, and your CVs live in the database this deployment owns — nothing is sent to a third-party service.'
		}
	];
</script>

<section class="relative overflow-hidden bg-neutral-950 pb-20 pt-16 sm:pt-24">
	<div
		class="pointer-events-none absolute left-1/2 top-0 h-[32rem] w-[64rem] -translate-x-1/2 rounded-full bg-purple-700/20 blur-3xl"
		aria-hidden="true"
	></div>

	<div class="relative mx-auto grid max-w-6xl grid-cols-1 gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:items-center lg:gap-8">
		<div class="reveal-up">
			<h1 class="text-4xl font-bold tracking-tight text-neutral-50 sm:text-5xl">
				YAML-first resume builder — professional PDFs with zero formatting risk
			</h1>
			<p class="mt-5 max-w-xl text-lg text-neutral-400">
				Write your CV in plain YAML or a guided form, preview the typeset PDF as you go, and
				export publication-quality output rendered by Typst — self-hosted, and your CVs saved
				to your account.
			</p>

			<ul class="mt-10 space-y-5" aria-label="Key features">
				{#each features as feature, i (feature.title)}
					<li class="reveal-up flex gap-3" style={`animation-delay:${150 + i * 90}ms`}>
						<span
							class="mt-1 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-purple-500/20 text-purple-400"
							aria-hidden="true"
						>
							<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
								<path d="M2 6.5l2.5 2.5L10 3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
							</svg>
						</span>
						<div>
							<p class="font-medium text-neutral-100">{feature.title}</p>
							<p class="text-sm text-neutral-400">{feature.description}</p>
						</div>
					</li>
				{/each}
			</ul>

			<div class="mt-10 flex flex-wrap gap-3">
				<a
					href="/app"
					class="rounded-md bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-purple-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-neutral-950"
				>
					Open the editor
				</a>
				<a
					href="#faq-heading"
					class="rounded-md border border-white/15 px-5 py-2.5 text-sm font-semibold text-neutral-200 transition-colors hover:bg-white/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
				>
					Read the FAQ
				</a>
			</div>
		</div>

		<div class="reveal-up" style="animation-delay: 200ms">
			<ThemeShowcase />
		</div>
	</div>
</section>

<style>
	.reveal-up {
		opacity: 0;
		animation: hero-fade-up 0.6s ease-out forwards;
	}

	@keyframes hero-fade-up {
		from {
			opacity: 0;
			transform: translateY(14px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.reveal-up {
			animation: none;
			opacity: 1;
		}
	}
</style>

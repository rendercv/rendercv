<script lang="ts">
	/**
	 * Fanned-out stack of theme previews in the hero.
	 *
	 * These are real renders: the same nine example PDFs the project ships,
	 * rendered by the same Typst pipeline the editor calls. An earlier
	 * version drew grey page mockups in CSS instead, on the reasoning that a
	 * mockup cannot misrepresent real output. In practice it read as five
	 * blank pages -- as though the images had failed to load -- and the one
	 * thing a CV builder's front page should show is what a CV looks like.
	 *
	 * The files are downscaled WebP copies (560px wide, ~50 KB each) of
	 * `docs/assets/images/examples/*.png`. The originals are 1224x1584 and
	 * around 800 KB apiece; sending five of those to display them at 224 CSS
	 * pixels would cost roughly 4 MB on first paint. Regenerate with
	 * Pillow if the source renders ever change -- resize to 560px wide,
	 * `quality=82`.
	 *
	 * Why the whole fan is one `role="img"` rather than five images: it is a
	 * single decorative composition. Announcing five separate CV screenshots
	 * would give a screen reader five near-identical descriptions of
	 * something the page is using as a picture, so the wrapper carries the
	 * description and the images inside it are marked decorative.
	 *
	 * Why these load eagerly: the fan sits in the hero, on screen before any
	 * scroll. Deferring it would trade a smaller initial request for five
	 * cards visibly popping in after the text has settled.
	 */
	const cards: {
		label: string;
		file: string;
		rotate: number;
		translateX: number;
		z: number;
	}[] = [
		{ label: 'Classic', file: 'classic', rotate: -10, translateX: -64, z: 1 },
		{ label: 'Sb2nov', file: 'sb2nov', rotate: -4, translateX: -28, z: 2 },
		{
			label: 'Engineering Resumes',
			file: 'engineeringresumes',
			rotate: 2,
			translateX: 8,
			z: 3
		},
		{ label: 'Moderncv', file: 'moderncv', rotate: 8, translateX: 44, z: 2 },
		{ label: 'Harvard', file: 'harvard', rotate: 14, translateX: 80, z: 1 }
	];
</script>

<div
	class="relative mx-auto h-80 w-full max-w-sm sm:h-96"
	role="img"
	aria-label="Preview of five CV theme layouts fanned out: Classic, Sb2nov, Engineering Resumes, Moderncv and Harvard"
>
	{#each cards as card, i (card.label)}
		<div
			class="reveal absolute left-1/2 top-1/2 h-72 w-52 overflow-hidden rounded-lg border border-white/10 bg-white shadow-2xl shadow-black/40 sm:h-80 sm:w-56"
			style={`z-index:${card.z}; transform: translate(-50%, -50%) translateX(${card.translateX}px) rotate(${card.rotate}deg); animation-delay:${i * 90}ms`}
		>
			<img
				src={`/themes/${card.file}.webp`}
				alt=""
				width="560"
				height="725"
				class="h-full w-full object-cover object-top"
			/>
			<div
				class="absolute inset-x-0 bottom-0 bg-neutral-900/80 px-2 py-1 text-center text-[10px] font-medium text-neutral-100 backdrop-blur-sm"
			>
				{card.label}
			</div>
		</div>
	{/each}
</div>

<style>
	.reveal {
		opacity: 0;
		animation: fan-in 0.7s ease-out forwards;
	}

	@keyframes fan-in {
		from {
			opacity: 0;
			transform: translate(-50%, -50%) translateY(16px) scale(0.96);
		}
		to {
			opacity: 1;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.reveal {
			animation: none;
			opacity: 1;
		}
	}
</style>

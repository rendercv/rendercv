<script lang="ts">
	/**
	 * The privacy policy, at `/privacy`.
	 *
	 * Why it exists: Google will not publish an OAuth app without one, and
	 * anyone signing in deserves to read what happens to their CVs before
	 * they write one. It is also the only route open to a person who has
	 * lost access to their Google account and wants their data removed --
	 * the delete control lives inside the editor, which they can no longer
	 * open.
	 *
	 * Deliberately self-contained: no store, no `$lib/api`, no `/api/*`
	 * call. Prerendering (see `+page.ts`) then produces a complete page
	 * that is readable with the backend down and with JavaScript off, which
	 * is how a reviewer and a crawler will read it.
	 *
	 * Every claim below is checked against the code that implements it: the
	 * Google scopes in `oauth.py`, the tables in `db/models.py`, the two
	 * cookies (`auth.SESSION_COOKIE_NAME` and `oauth.STATE_COOKIE_NAME`), and
	 * the cascade in `repository.delete_user`. If any of those change, this
	 * page is wrong and must change with them.
	 */
	import BrandMark from '$lib/components/BrandMark.svelte';

	const lastUpdated = 'September 7, 2026';
	const contactEmail = 'quannguyen101202@gmail.com';
</script>

<svelte:head>
	<title>Privacy Policy — RenderCV Web Editor</title>
	<meta
		name="description"
		content="What the RenderCV Web Editor stores, why, who can see it, and how to delete all of it."
	/>
</svelte:head>

<div class="min-h-screen bg-neutral-950 text-neutral-100">
	<header class="border-b border-white/10">
		<div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3 sm:px-6">
			<a href="/" class="flex items-center gap-2 text-neutral-100" aria-label="RenderCV home">
				<span class="text-purple-400"><BrandMark /></span>
				<span class="text-lg font-semibold tracking-tight">RenderCV</span>
			</a>
			<a
				href="/"
				class="rounded text-sm text-neutral-400 transition-colors hover:text-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
			>
				Back to home
			</a>
		</div>
	</header>

	<main class="mx-auto max-w-3xl px-4 py-12 sm:px-6">
		<h1 class="text-3xl font-semibold tracking-tight sm:text-4xl">Privacy Policy</h1>
		<p class="mt-2 text-sm text-neutral-500">Last updated: {lastUpdated}</p>

		<p class="mt-8 leading-relaxed text-neutral-300">
			This is a personal, self-hosted deployment of
			<a
				href="https://github.com/rendercv/rendercv"
				target="_blank"
				rel="noopener noreferrer"
				class="underline decoration-neutral-700 underline-offset-4 hover:text-neutral-100"
				>RenderCV</a
			>, an open-source CV builder. It is run by an individual, not a company. This page describes
			everything it stores about you and how to remove it.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">What is collected</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			<strong class="font-semibold text-neutral-100"
				>From your Google account, when you sign in:</strong
			>
			your email address, your display name, and the account identifier Google uses for you. Sign-in asks
			Google for the standard <code class="text-neutral-400">openid email profile</code> permissions and
			nothing beyond them — no contacts, no Drive or other files, no calendar, no ability to act on your
			behalf. Google's reply also carries the address of your profile photo; it is discarded rather than
			stored.
		</p>
		<p class="mt-3 leading-relaxed text-neutral-300">
			<strong class="font-semibold text-neutral-100">What you write in the editor:</strong>
			your CV documents, their edit history, and your editor preferences such as the light or dark theme.
			A CV is whatever you typed into it, so it usually holds personal information — your name, contact
			details, employers, education. It is stored because a CV editor that forgets your CV is of no use;
			it is not read, analysed, or used for anything else.
		</p>
		<p class="mt-3 leading-relaxed text-neutral-300">
			<strong class="font-semibold text-neutral-100">Two cookies, both strictly functional:</strong>
			a signed session cookie that keeps you signed in, and a short-lived one set only while you are being
			sent to Google and back, which exists to detect a tampered sign-in and is deleted the moment sign-in
			finishes. There is no analytics, no advertising, no tracking pixel, and no third-party script anywhere
			in the application.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Why it is collected</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Only to sign you in and to keep your CVs, so that they are still there on your next visit and
			on your other devices. There is no other purpose.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Who it is shared with</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Nobody. Your data is not sold, rented, published, or handed to advertisers or analytics
			providers. Two parties are unavoidably involved in running the service:
		</p>
		<ul class="mt-3 list-disc space-y-2 pl-6 leading-relaxed text-neutral-300">
			<li>
				<strong class="font-semibold text-neutral-100">Google</strong>, which performs the sign-in.
				Google learns that you signed in to this application. It does not receive your CVs.
			</li>
			<li>
				<strong class="font-semibold text-neutral-100">Render</strong>, which hosts the server and
				the database. As the infrastructure operator, Render holds the disks the data sits on.
			</li>
		</ul>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">How your PDF is produced</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			On this server, by the open-source RenderCV engine. Your CV is not sent to any external
			rendering, AI, or document service in order to produce it.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Deleting your data</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Open the editor and use <strong class="font-semibold text-neutral-100">Delete</strong>, beside
			<strong class="font-semibold text-neutral-100">Sign out</strong>. After a confirmation it erases
			your account, every CV in it, all edit history, and your preferences. This happens immediately and
			cannot be undone — there is no recovery period and no backup to restore you from.
		</p>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Signing out is a different thing: it ends the session on that browser and changes nothing else.
			Your CVs are waiting the next time you sign in.
		</p>
		<p class="mt-3 leading-relaxed text-neutral-300">
			If you can no longer sign in and want your data removed, write to the address at the bottom of
			this page and say which email address the account used.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">How long it is kept</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Until you delete it, or until the deployment itself is shut down. Please read the next section
			before relying on that.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">
			Please do not make this your only copy
		</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			This deployment runs on Render's free plan, whose database is removed roughly thirty days after
			it is created. When that happens, every account and every CV on this server goes with it —
			without warning, and with no backup to restore from. The service may also be taken down at any
			time; it carries no uptime promise of any kind.
		</p>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Export your PDF, and keep your YAML somewhere you control. Treat this as a place to work on a
			CV, not a place to store one.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Children</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			This service is not directed at children under 13, and no account is knowingly created for one.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Changes to this policy</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Any change is published on this page with a new date at the top. There is no mailing list to
			notify, because no address is kept for that purpose.
		</p>

		<h2 class="mt-10 text-xl font-semibold text-neutral-100">Contact</h2>
		<p class="mt-3 leading-relaxed text-neutral-300">
			Questions about this policy, or a request to delete data you can no longer reach:
			<a
				href="mailto:{contactEmail}"
				class="underline decoration-neutral-700 underline-offset-4 hover:text-neutral-100"
				>{contactEmail}</a
			>
		</p>
	</main>

	<footer class="border-t border-white/10 py-8">
		<div class="mx-auto max-w-3xl px-4 text-sm text-neutral-500 sm:px-6">
			<a
				href="/"
				class="rounded underline decoration-neutral-700 underline-offset-4 hover:text-neutral-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
			>
				Back to RenderCV
			</a>
		</div>
	</footer>
</div>

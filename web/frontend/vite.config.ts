import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) => filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},

			// Built as static files that the FastAPI backend serves itself, so
			// the app and its API share one origin. That is not a packaging
			// preference: the session cookie is `SameSite=Lax`, which a
			// browser withholds from cross-site `fetch`, so a frontend on a
			// different host than the API would sign in and lose the session
			// on the very next request -- with no CORS error to explain it.
			//
			// `fallback` puts everything that is not prerendered into SPA
			// mode: the server hands back `index.html` and the client router
			// resolves the route. `/app` needs that; it is an editor whose
			// content comes entirely from the API.
			// The fallback is deliberately not named `index.html`: that is where
			// the prerendered landing page lands, and SvelteKit overwrites it
			// with the empty shell if both claim the name -- silently undoing
			// the prerender, with only a build-log line to say so.
			adapter: adapter({ fallback: 'fallback.html' })
		})
	],
	server: {
		proxy: {
			// The FastAPI backend (web/backend) is served separately in dev.
			// Overridable so the e2e suite can point at the throwaway backend
			// it launches itself (see playwright.config.ts) instead of
			// whatever happens to be on the developer's 8000.
			'/api': {
				target: process.env.RENDERCV_API_TARGET ?? 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	optimizeDeps: {
		// Pre-bundle the client-side preview engine's compiler dependency at
		// server start. It is only ever imported by `engine.worker.ts`, which
		// nothing instantiates until the wasm preview flag is on -- so without
		// this Vite first discovers it whenever the worker is finally
		// constructed and forces a full page reload right then, destroying the
		// page's execution context mid-run (which is exactly what e2e/wasm.spec.ts
		// does). Listing it here makes dev startup deterministic instead.
		include: ['@myriaddreamin/typst.ts', '@myriaddreamin/typst.ts/compiler']
	},
	worker: {
		// The client-side (wasm) preview engine's worker
		// (src/lib/wasm/engine.worker.ts) is constructed with `{ type:
		// 'module' }` and both statically imports an ESM-only package
		// (@myriaddreamin/typst.ts) and dynamically imports Pyodide's ESM
		// build from a CDN URL at runtime. Building it as an ES module
		// (Vite's default worker format is the legacy 'iife') keeps the dev
		// and production behavior of those imports consistent.
		format: 'es'
	},
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});

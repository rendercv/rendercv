import { MemoryAccessModel } from '@myriaddreamin/typst.ts';
import type { PackageRegistry, PackageSpec } from '@myriaddreamin/typst.ts/internal.types';

export interface BundledTypstPackage {
	namespace: string;
	name: string;
	version: string;
	/** Static URL directory the package's files are fetched relative to, e.g. `/wasm/packages/preview/rendercv/0.3.0`. */
	baseUrl: string;
	files: string[];
}

/**
 * A `PackageRegistry` over Typst packages this app bundles itself (the
 * `rendercv` and `fontawesome` packages our own Typst templates import),
 * fetched from our own static assets instead of typst.ts's built-in
 * `FetchPackageRegistry` (which pulls tarballs from packages.typst.org).
 *
 * Why files must be preloaded rather than fetched lazily inside `resolve()`:
 * the compiler's package resolution is a synchronous wasm<->JS callback (see
 * typst.ts's `withPackageRegistry`) -- there is no way to `await` inside it.
 * Every file this registry can serve must already be sitting in the
 * `MemoryAccessModel` before the first `compile()` call, so `preload()`
 * does that fetching up front, once, during engine initialization.
 */
export class LocalPackageRegistry implements PackageRegistry {
	private readonly roots = new Map<string, string>();

	constructor(
		private readonly am: MemoryAccessModel,
		private readonly packages: BundledTypstPackage[]
	) {}

	private static key(namespace: string, name: string, version: string): string {
		return `${namespace}/${name}/${version}`;
	}

	/** Fetches every bundled package's files into the access model. Call once before the first compile. */
	async preload(fetchImpl: typeof fetch = fetch): Promise<void> {
		for (const pkg of this.packages) {
			const root = `/@memory/rendercv/packages/${pkg.namespace}/${pkg.name}/${pkg.version}`;
			for (const file of pkg.files) {
				const url = `${pkg.baseUrl}/${file}`;
				const response = await fetchImpl(url);
				if (!response.ok) {
					throw new Error(`Failed to fetch bundled Typst package file ${url}: HTTP ${response.status}`);
				}
				const data = new Uint8Array(await response.arrayBuffer());
				this.am.insertFile(`${root}/${file}`, data, new Date());
			}
			this.roots.set(LocalPackageRegistry.key(pkg.namespace, pkg.name, pkg.version), root);
		}
	}

	resolve(spec: PackageSpec): string | undefined {
		return this.roots.get(LocalPackageRegistry.key(spec.namespace, spec.name, spec.version));
	}
}

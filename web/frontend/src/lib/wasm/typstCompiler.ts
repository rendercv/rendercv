import { createTypstCompiler, MemoryAccessModel, loadFonts, initOptions } from '@myriaddreamin/typst.ts';
import { CompileFormatEnum } from '@myriaddreamin/typst.ts/compiler';
import { LocalPackageRegistry } from './packageRegistry';
import type { WasmManifest } from './manifest';

const { withAccessModel, withPackageRegistry } = initOptions;

export interface TypstCompilerHandle {
	/** Compiles a `.typ` source string to PDF bytes. Rejects if the compiler produced no output. */
	compileToPdf(typSource: string): Promise<Uint8Array>;
}

async function fetchBytes(url: string, fetchImpl: typeof fetch): Promise<Uint8Array> {
	const response = await fetchImpl(url);
	if (!response.ok) {
		throw new Error(`Failed to fetch ${url}: HTTP ${response.status}`);
	}
	return new Uint8Array(await response.arrayBuffer());
}

/**
 * Sets up a typst.ts compiler pre-loaded with the `rendercv` and
 * `fontawesome` Typst packages (both bundled by this project, served from
 * `static/wasm/packages/`) and the default-theme font subset
 * (`static/wasm/fonts/`) instead of typst.ts's default remote package/font
 * fetching.
 *
 * @param manifest The parsed `static/wasm/manifest.json`.
 * @param baseUrl Origin to fetch `/wasm/...` assets from (the worker's `self.location.origin`).
 */
export async function createBrowserTypstCompiler(
	manifest: WasmManifest,
	baseUrl: string,
	fetchImpl: typeof fetch = fetch
): Promise<TypstCompilerHandle> {
	const am = new MemoryAccessModel();
	const registry = new LocalPackageRegistry(am, [
		{
			namespace: 'preview',
			name: 'rendercv',
			version: manifest.rendercvPackageVersion,
			baseUrl: `${baseUrl}/wasm/packages/preview/rendercv/${manifest.rendercvPackageVersion}`,
			files: ['lib.typ', 'typst.toml']
		},
		{
			namespace: 'preview',
			name: 'fontawesome',
			version: manifest.fontawesomePackageVersion,
			baseUrl: `${baseUrl}/wasm/packages/preview/fontawesome/${manifest.fontawesomePackageVersion}`,
			files: ['lib.typ', 'lib-impl.typ', 'lib-gen-func.typ', 'lib-gen-map.typ', 'typst.toml']
		}
	]);
	await registry.preload(fetchImpl);

	const fontBuffers = await Promise.all(
		manifest.fonts.map((relPath) => fetchBytes(`${baseUrl}/wasm/${relPath}`, fetchImpl))
	);

	const compiler = createTypstCompiler();
	await compiler.init({
		getModule: () => fetchBytes(`${baseUrl}/wasm/${manifest.typstCompilerWasm}`, fetchImpl),
		beforeBuild: [
			withAccessModel(am),
			withPackageRegistry(registry),
			// `{ assets: false }` disables typst.ts's default remote preload of
			// its own text/CJK/emoji font sets -- we supply exactly the fonts
			// the bundled theme needs, fetched from our own static assets.
			loadFonts(fontBuffers, { assets: false })
		]
	});

	const mainFilePath = '/main.typ';

	return {
		async compileToPdf(typSource: string): Promise<Uint8Array> {
			compiler.addSource(mainFilePath, typSource);
			const result = await compiler.compile({
				mainFilePath,
				format: CompileFormatEnum.pdf,
				diagnostics: 'none'
			});
			if (!result.result) {
				throw new Error('Typst compile produced no PDF output');
			}
			return result.result;
		}
	};
}

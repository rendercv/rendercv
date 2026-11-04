#!/usr/bin/env node
// Builds/copies every static asset the client-side (Pyodide + typst.ts)
// preview engine needs at runtime, from this repo's own Python source tree
// and node_modules, into `static/wasm/`.
//
// Why a script instead of committing these files: they are all derived --
// the wheel from `uv build`, the Typst package files and fonts from the
// core's own bundled copies, the compiler wasm binary from an npm package.
// Committing derived binaries invites drift from the source they were
// copied from; regenerating them here keeps this a single command that a
// CI step (or a developer after touching the core) can re-run.
//
// Usage: `node scripts/build-wasm-assets.mjs` from `web/frontend/`.

import { execFileSync } from 'node:child_process';
import { mkdirSync, copyFileSync, readFileSync, readdirSync, writeFileSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const FRONTEND_ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const REPO_ROOT = path.resolve(FRONTEND_ROOT, '../..');
const RENDERER_DIR = path.join(REPO_ROOT, 'src/rendercv/renderer');
const OUT_DIR = path.join(FRONTEND_ROOT, 'static/wasm');

/** Reads the `version` field out of a Typst package's `typst.toml`. */
function readTypstPackageVersion(typstTomlPath) {
	const text = readFileSync(typstTomlPath, 'utf-8');
	const match = text.match(/^version\s*=\s*"([^"]+)"/m);
	if (!match) throw new Error(`Could not find a version in ${typstTomlPath}`);
	return match[1];
}

function copyInto(destDir, srcDir, files) {
	mkdirSync(destDir, { recursive: true });
	for (const file of files) {
		copyFileSync(path.join(srcDir, file), path.join(destDir, file));
	}
}

function buildWheel() {
	console.log('Building the rendercv wheel (uv build --wheel)...');
	const distDir = path.join(OUT_DIR, 'dist');
	rmSync(distDir, { recursive: true, force: true });
	mkdirSync(distDir, { recursive: true });
	execFileSync('uv', ['build', '--wheel', '--out-dir', distDir], {
		cwd: REPO_ROOT,
		stdio: 'inherit'
	});
	const wheelName = readdirSync(distDir).find((f) => f.endsWith('.whl'));
	if (!wheelName) throw new Error(`uv build did not produce a .whl in ${distDir}`);
	return wheelName;
}

function copyTypstPackages() {
	console.log('Copying bundled Typst packages (rendercv, fontawesome)...');
	const rendercvTypstDir = path.join(RENDERER_DIR, 'rendercv_typst');
	const fontawesomeDir = path.join(RENDERER_DIR, 'typst_fontawesome');

	const rendercvVersion = readTypstPackageVersion(path.join(rendercvTypstDir, 'typst.toml'));
	const fontawesomeVersion = readTypstPackageVersion(path.join(fontawesomeDir, 'typst.toml'));

	copyInto(
		path.join(OUT_DIR, 'packages/preview/rendercv', rendercvVersion),
		rendercvTypstDir,
		['lib.typ', 'typst.toml']
	);
	copyInto(
		path.join(OUT_DIR, 'packages/preview/fontawesome', fontawesomeVersion),
		fontawesomeDir,
		['lib.typ', 'lib-impl.typ', 'lib-gen-func.typ', 'lib-gen-map.typ', 'typst.toml']
	);

	return { rendercvVersion, fontawesomeVersion };
}

// The classic theme's default font family ("Source Sans 3") plus the three
// Font Awesome faces the templates use for connection/link icons. Other
// themes/fonts are a documented follow-up (see the phase report) -- bundling
// all ~59MB of `rendercv-fonts` is impractical for a browser download.
const FONT_FILES = [
	'Source Sans 3/SourceSans3-Regular.ttf',
	'Source Sans 3/SourceSans3-Bold.ttf',
	'Source Sans 3/SourceSans3-Italic.ttf',
	'Source Sans 3/SourceSans3-BoldItalic.ttf',
	'Font Awesome 7/Font Awesome 7 Free-Regular-400.otf',
	'Font Awesome 7/Font Awesome 7 Free-Solid-900.otf',
	'Font Awesome 7/Font Awesome 7 Brands-Regular-400.otf'
];

function copyFonts() {
	console.log('Copying the default-theme font subset...');
	const fontsPkgDir = path.join(REPO_ROOT, '.venv/Lib/site-packages/rendercv_fonts');
	const destDir = path.join(OUT_DIR, 'fonts');
	mkdirSync(destDir, { recursive: true });
	const names = [];
	for (const relPath of FONT_FILES) {
		const flatName = path.basename(relPath);
		copyFileSync(path.join(fontsPkgDir, relPath), path.join(destDir, flatName));
		names.push(flatName);
	}
	return names;
}

function copyTypstCompilerWasm() {
	console.log('Copying the typst.ts web-compiler wasm binary...');
	const pkgDir = path.join(FRONTEND_ROOT, 'node_modules/@myriaddreamin/typst-ts-web-compiler/pkg');
	const destDir = path.join(OUT_DIR, 'typst');
	mkdirSync(destDir, { recursive: true });
	copyFileSync(
		path.join(pkgDir, 'typst_ts_web_compiler_bg.wasm'),
		path.join(destDir, 'typst_ts_web_compiler_bg.wasm')
	);
}

function main() {
	mkdirSync(OUT_DIR, { recursive: true });
	const wheelName = buildWheel();
	const { rendercvVersion, fontawesomeVersion } = copyTypstPackages();
	const fontFiles = copyFonts();
	copyTypstCompilerWasm();

	const manifest = {
		generatedAt: new Date().toISOString(),
		wheel: `dist/${wheelName}`,
		rendercvPackageVersion: rendercvVersion,
		fontawesomePackageVersion: fontawesomeVersion,
		fonts: fontFiles.map((name) => `fonts/${name}`),
		typstCompilerWasm: 'typst/typst_ts_web_compiler_bg.wasm'
	};
	writeFileSync(path.join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, '\t') + '\n');
	console.log('Wrote', path.join(OUT_DIR, 'manifest.json'));
	console.log(manifest);
}

main();

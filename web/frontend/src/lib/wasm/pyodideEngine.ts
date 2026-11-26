import type { CvDocuments } from '$lib/stores/documents';

/**
 * Pinned to the release whose bundled `pydantic`/`pydantic-core` versions
 * (2.12.5 / 2.41.5, at the time this was written) satisfy this repo's floor
 * (`pydantic[email]>=2.12.5` in `pyproject.toml`). An older Pyodide release
 * ships an older `pydantic-core` wasm build that micropip cannot upgrade
 * in-place (no matching wasm wheel exists on PyPI for arbitrary
 * `pydantic-core` versions), so this pin isn't cosmetic -- verify the new
 * pin's `pyodide-lock.json` still has a compatible pydantic before bumping.
 *
 * Why the interpreter itself is loaded from jsdelivr rather than
 * self-hosted: everything unique to this project (the wheel, the Typst
 * packages, the fonts, the compiler wasm) is self-hosted via
 * `static/wasm/`; Pyodide's own runtime + its bundled pure/binary packages
 * are pyodide.org's own versioned, immutable CDN distribution. Self-hosting
 * that too (for fully offline operation) is a documented follow-up, not
 * done here -- see the phase report.
 */
const PYODIDE_VERSION = '0.29.4';
const PYODIDE_CDN_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

export interface PyodideEngineHandle {
	/**
	 * Runs the core's YAML -> Typst-source pipeline
	 * (`build_rendercv_dictionary_and_model` + `generate_typst`) and returns
	 * the resulting `.typ` source text.
	 *
	 * Rejects on any validation/parse error -- by design, client-side
	 * validation errors are not surfaced; the caller (the render controller)
	 * treats any rejection as "fall back to the server for this render",
	 * which remains the source of truth for error content.
	 */
	buildTypstSource(docs: CvDocuments): Promise<string>;
}

// Minimal surface of the pyodide instance this module touches, kept narrow
// so this file doesn't need `pyodide`'s (Node-oriented) type declarations,
// which don't describe the browser ESM entry point used here.
interface PyodideInterface {
	FS: { writeFile(path: string, data: Uint8Array): void };
	globals: { set(name: string, value: unknown): void };
	loadPackage(names: string[]): Promise<unknown>;
	runPythonAsync(code: string): Promise<unknown>;
}

/**
 * Loads Pyodide in the current worker, installs the rendercv wheel (base
 * package only -- no `full` extras, so no `typst`/`rendercv-fonts`/`typer`
 * are needed, since PDF compilation happens via typst.ts, not typst-py),
 * and returns a handle that turns CV documents into Typst source text.
 *
 * Mirrors the proven recipe in `tests/test_pyodide.py` (wheel copied into
 * Pyodide's virtual FS to avoid `file://` URL issues, then
 * `micropip.install("emfs:/tmp/<wheel>")`), extended to actually run the
 * YAML -> Typst pipeline rather than just importing the package.
 */
export async function createPyodideEngine(wheelUrl: string): Promise<PyodideEngineHandle> {
	const pyodideModule = (await import(
		/* @vite-ignore */ `${PYODIDE_CDN_BASE}pyodide.mjs`
	)) as { loadPyodide(options: { indexURL: string }): Promise<PyodideInterface> };

	const pyodide = await pyodideModule.loadPyodide({ indexURL: PYODIDE_CDN_BASE });

	const wheelResponse = await fetch(wheelUrl);
	if (!wheelResponse.ok) {
		throw new Error(`Failed to fetch the rendercv wheel (${wheelUrl}): HTTP ${wheelResponse.status}`);
	}
	const wheelBytes = new Uint8Array(await wheelResponse.arrayBuffer());
	const wheelName = wheelUrl.split('/').pop() ?? 'rendercv.whl';
	pyodide.FS.writeFile(`/tmp/${wheelName}`, wheelBytes);

	// Pre-load pydantic/pydantic-core/jinja2 from Pyodide's own package
	// index (matching wasm ABI for this exact Pyodide release) before
	// micropip resolves rendercv's dependency on them -- otherwise micropip
	// tries to fetch a wasm build of whatever exact version rendercv's
	// floor requires from PyPI, which frequently doesn't exist (see the
	// phase report for the failure this sidesteps).
	await pyodide.loadPackage(['micropip', 'pydantic', 'pydantic-core', 'jinja2']);

	await pyodide.runPythonAsync(`
import micropip

# pydantic[email] resolves to this at import time; not always inferred
# correctly by micropip's extras handling, so install it explicitly first.
await micropip.install("email-validator")
await micropip.install("emfs:/tmp/${wheelName}", deps=True)
	`);

	return {
		async buildTypstSource(docs: CvDocuments): Promise<string> {
			pyodide.globals.set('_rendercv_cv_yaml', docs.cv);
			pyodide.globals.set('_rendercv_design_yaml', docs.design);
			pyodide.globals.set('_rendercv_locale_yaml', docs.locale);
			pyodide.globals.set('_rendercv_settings_yaml', docs.settings);

			const typSource = await pyodide.runPythonAsync(`
import pathlib

from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model
from rendercv.renderer.typst import generate_typst


def _blank_to_none(text):
    # Mirrors web/backend/src/rendercv_web/core.py's blank_to_none: an
    # empty overlay tab means "not provided", not "parse this as YAML".
    return text if text.strip() else None


_, _rendercv_model = build_rendercv_dictionary_and_model(
    _rendercv_cv_yaml,
    design_yaml_file=_blank_to_none(_rendercv_design_yaml),
    locale_yaml_file=_blank_to_none(_rendercv_locale_yaml),
    settings_yaml_file=_blank_to_none(_rendercv_settings_yaml),
    input_file_path=pathlib.Path("/cv/in.yaml"),
    dont_generate_markdown=True,
    dont_generate_html=True,
    dont_generate_png=True,
    dont_generate_pdf=True,
)
_rendercv_typst_path = generate_typst(_rendercv_model)
_rendercv_typst_path.read_text(encoding="utf-8")
			`);

			return typSource as string;
		}
	};
}

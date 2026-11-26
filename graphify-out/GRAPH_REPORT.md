# Graph Report - rendercv_P-041  (2026-08-28)

## Corpus Check
- 67 files · ~3,857,847 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2338 nodes · 4238 edges · 187 communities (156 shown, 31 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.57)
- Token cost: 97,964 input · 0 output

## Community Hubs (Navigation)
- Sections & Entry Forms (FE)
- DB Models & Repository (BE)
- Preferences & Split Ratio (FE)
- DB Session & Migration Tests (BE)
- Google Sign-in & Session (BE)
- CV CRUD Endpoints (BE)
- Sign-in & Anonymous Merge Tests (BE)
- CV API Tests (BE)
- Form Field Components (FE)
- FastAPI App & Error Boundary (BE)
- YAML Round-trip & Patch (BE)
- DB Session & Engine (BE)
- Document API Tests (BE)
- Classic Theme (core)
- Typst Renderer (core)
- Entry Template Rendering (core)
- Jinja Templater (core)
- CV Entry Models (core)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Render & Validate API Tests (BE)
- Stores: auth (FE)
- RenderCV Model Builder (core)
- Variant Pydantic Model Generator (core)
- Request & Response Models (BE)
- CV API Client (FE)
- Client-side WASM Preview (FE)
- Create-theme Command (core)
- Preview Render Controller (FE)
- Schema Snapshot: schema.snapshot (FE)
- Locale Translations (core)
- New Command: copy_templates (core)
- Section (core)
- Sample Generator (core)
- App (core)
- Progress Panel (core)
- API Clients (FE)
- YAML Reader (core)
- Package: package (FE)
- Package: package (FE)
- Playwright E2E Suite (FE)
- Stores: documents (FE)
- WASM Engine Handle (FE)
- Connections (core)
- Schema Snapshot: schema.snapshot (FE)
- Documenteditors (FE)
- PDF PNG (core)
- Watcher (core)
- Autosave: autosave (FE)
- Validatecontroller (FE)
- CV: cv (core)
- Models: path (core)
- Pydantic Error Handling (core)
- Schema Snapshot: schema.snapshot (FE)
- @codemirror (FE)
- Tsconfig (FE)
- Schema (BE)
- Errorclassification (FE)
- Form (FE)
- Schema Snapshot: schema.snapshot (FE)
- Readme: README (FE)
- Build WASM Assets (FE)
- Formsync (FE)
- Autosave: autosave (FE)
- Schema Snapshot: schema.snapshot (FE)
- Other Themes: README (core)
- Social Network (core)
- Package: package (FE)
- App (FE)
- Readme
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Helper (core)
- Settings: settings (core)
- Preferences (BE)
- Bootstrap (FE)
- Cvsessionactions (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- English Locale (core)
- Readme: README (BE)
- Readme: README (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Validation Context (core)
- Cache (BE)
- Dimension (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Readme: README (FE)
- Themes (BE)
- Readme: README (FE)
- Readme: README (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Run Rendercv (core)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Entry Point (core)
- Entries: EducationEntry.j2 (core)
- Publication (core)
- Readme: README (BE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Cvs (BE)
- Markdown Parser (core)
- JSON Schema Generator (core)
- 320e31bb905f Add OAuth Identity Columns To Users (BE)
- 8a6ebf56c34d Create Baseline Schema (BE)
- Documents (BE)
- Limits (BE)
- Package: package (FE)
- Cvsessionactions Test (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Full (core)
- Rendercv Model (core)
- Color (FE)
- Schema Snapshot: schema.snapshot (FE)
- Schema Snapshot: schema.snapshot (FE)
- Thumbnail (core)
- Typst Dimension (core)
- Favicon (FE)
- Global Setup (FE)
- Months (FE)
- Markdown (core)
- Error Dictionary (core)
- Entry (core)
- Entry With Date (core)
- Package: package (FE)
- App D (FE)
- Robots (FE)
- Cluster 149
- Cluster 150
- Cluster 151
- Cluster 152
- Cluster 153
- Backend (BE)
- Entries: BulletEntry.j2 (core)
- Entries: NumberedEntry.j2 (core)
- Entries: OneLineEntry.j2 (core)
- Entries: ReversedNumberedEntry.j2 (core)
- Entries: TextEntry.j2 (core)
- Other Themes: ink (core)
- Cluster 175
- Cluster 176
- Cluster 177
- Cluster 178
- Cluster 179
- Cluster 180
- Cluster 181

## God Nodes (most connected - your core abstractions)
1. `BaseModelWithoutExtraKeys` - 42 edges
2. `default` - 37 edges
3. `RenderCVModel` - 35 edges
4. `CvDocuments` - 34 edges
5. `default` - 32 edges
6. `RenderCVInternalError` - 30 edges
7. `RenderCVUserError` - 27 edges
8. `session()` - 24 edges
9. `BaseEntry` - 22 edges
10. `Locale Localization Schema` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Arabic locale (RTL; 'DEGREE في AREA'; Gregorian month names transliterated)` --implements--> `Locale Localization Schema`  [EXTRACTED]
  src/rendercv/schema/models/locale/other_locales/arabic.yaml → schema.json
- `Danish locale ('DEGREE i AREA'; year/years both 'år')` --implements--> `Locale Localization Schema`  [EXTRACTED]
  src/rendercv/schema/models/locale/other_locales/danish.yaml → schema.json
- `Dutch locale ('DEGREE in AREA'; present = 'heden')` --implements--> `Locale Localization Schema`  [EXTRACTED]
  src/rendercv/schema/models/locale/other_locales/dutch.yaml → schema.json
- `French locale ('DEGREE en AREA'; month/months both 'mois')` --implements--> `Locale Localization Schema`  [EXTRACTED]
  src/rendercv/schema/models/locale/other_locales/french.yaml → schema.json
- `German locale ('DEGREE in AREA'; present = 'gegenwärtig')` --implements--> `Locale Localization Schema`  [EXTRACTED]
  src/rendercv/schema/models/locale/other_locales/german.yaml → schema.json

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Playwright e2e run against a throwaway database** — web_readme_playwright_e2e, web_readme_throwaway_e2e_database, web_readme_rendercv_web_database_url, web_readme_uvicorn_rendercv_web_app, web_frontend_readme_npm_run_test_e2e, web_readme_playwright_single_worker [EXTRACTED 1.00]
- **Client-side WASM render path** — web_readme_wasm_client_preview, web_readme_pyodide, web_readme_typst_ts, web_readme_build_wasm_assets, web_readme_wasm_preview_flag, web_frontend_readme_wasm_engine_module [EXTRACTED 1.00]
- **Deployment environment variable contract** — web_readme_deploy, web_readme_rendercv_web_secret, web_readme_rendercv_web_https, web_readme_rendercv_web_database_url, web_readme_rendercv_web_allowed_origins, web_readme_postgres_extra [EXTRACTED 1.00]
- **Markdown entry-type rendering templates** — src_rendercv_renderer_templater_templates_markdown_entries_bulletentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_educationentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_experienceentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_normalentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_numberedentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_onelineentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_publicationentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_reversednumberedentry_j2, src_rendercv_renderer_templater_templates_markdown_entries_textentry_j2 [EXTRACTED 1.00]
- **Built-in other-themes design override catalog** — src_rendercv_schema_models_design_other_themes_ember, src_rendercv_schema_models_design_other_themes_engineeringclassic, src_rendercv_schema_models_design_other_themes_engineeringresumes, src_rendercv_schema_models_design_other_themes_harvard, src_rendercv_schema_models_design_other_themes_ink, src_rendercv_schema_models_design_other_themes_moderncv, src_rendercv_schema_models_design_other_themes_opal, src_rendercv_schema_models_design_other_themes_sb2nov [EXTRACTED 1.00]
- **All 21 other_locales translation files implement the shared Locale Localization Schema (each declares $schema=../../../../../../schema.json and defines the same locale keys: language, last_updated, month/months, year/years, present, phrases.degree_with_area, month_abbreviations, month_names)** — src_rendercv_schema_models_locale_other_locales_arabic_locale, src_rendercv_schema_models_locale_other_locales_danish_locale, src_rendercv_schema_models_locale_other_locales_dutch_locale, src_rendercv_schema_models_locale_other_locales_french_locale, src_rendercv_schema_models_locale_other_locales_german_locale, src_rendercv_schema_models_locale_other_locales_hebrew_locale, src_rendercv_schema_models_locale_other_locales_hindi_locale, src_rendercv_schema_models_locale_other_locales_hungarian_locale, src_rendercv_schema_models_locale_other_locales_indonesian_locale, src_rendercv_schema_models_locale_other_locales_italian_locale, src_rendercv_schema_models_locale_other_locales_japanese_locale, src_rendercv_schema_models_locale_other_locales_korean_locale, src_rendercv_schema_models_locale_other_locales_mandarin_chinese_locale, src_rendercv_schema_models_locale_other_locales_norwegian_bokm_l_locale, src_rendercv_schema_models_locale_other_locales_norwegian_nynorsk_locale, src_rendercv_schema_models_locale_other_locales_persian_locale, src_rendercv_schema_models_locale_other_locales_portuguese_locale, src_rendercv_schema_models_locale_other_locales_russian_locale, src_rendercv_schema_models_locale_other_locales_spanish_locale, src_rendercv_schema_models_locale_other_locales_turkish_locale, src_rendercv_schema_models_locale_other_locales_vietnamese_locale, schema_locale_localization_schema [EXTRACTED 1.00]
- **design.templates-driven education entry rendering** — src_rendercv_renderer_templater_templates_markdown_entries_educationentry_j2, src_rendercv_schema_models_design_other_themes_ember, src_rendercv_schema_models_design_other_themes_engineeringclassic, src_rendercv_schema_models_design_other_themes_engineeringresumes, src_rendercv_schema_models_design_other_themes_harvard, src_rendercv_schema_models_design_other_themes_ink, src_rendercv_schema_models_design_other_themes_moderncv, src_rendercv_schema_models_design_other_themes_opal, src_rendercv_schema_models_design_other_themes_sb2nov [INFERRED 0.75]
- **AREA-first degree phrase group: Hindi, Japanese, Korean, Mandarin Chinese, and Turkish reverse the placeholder order (AREA before DEGREE) in phrases.degree_with_area, unlike the DEGREE-first pattern of the other 16 locales** — src_rendercv_schema_models_locale_other_locales_hindi_locale, src_rendercv_schema_models_locale_other_locales_japanese_locale, src_rendercv_schema_models_locale_other_locales_korean_locale, src_rendercv_schema_models_locale_other_locales_mandarin_chinese_locale, src_rendercv_schema_models_locale_other_locales_turkish_locale [INFERRED 0.85]
- **RTL-script locale group: Arabic, Hebrew, and Persian are written right-to-left, which affects how the Typst renderer must lay out dates and the degree_with_area phrase** — src_rendercv_schema_models_locale_other_locales_arabic_locale, src_rendercv_schema_models_locale_other_locales_hebrew_locale, src_rendercv_schema_models_locale_other_locales_persian_locale [INFERRED 0.85]

## Communities (187 total, 31 thin omitted)

### Community 0 - "Sections & Entry Forms (FE)"
Cohesion: 0.06
Nodes (60): ei(), addEntryLabel(), displaySectionTitle(), singularizeWord(), buildAddEntryOp(), buildAddHighlightOp(), buildAddSectionOp(), buildDeleteEntryOp() (+52 more)

### Community 1 - "DB Models & Repository (BE)"
Cohesion: 0.07
Nodes (55): datetime, DeclarativeBase, Base, Cv, CvVersion, Preference, SQLAlchemy ORM models for the RenderCV Web Editor's baseline schema. Why: Per…, An append-only autosave snapshot of a CV's four documents. Why: Powers undo… (+47 more)

### Community 2 - "Preferences & Split Ratio (FE)"
Cohesion: 0.06
Nodes (40): getPreferences(), setPreference(), clampSplitRatio(), DEFAULT_SPLIT_RATIO, MAX_SPLIT_RATIO, MIN_SPLIT_RATIO, parseSplitRatio(), ratioFromDrag() (+32 more)

### Community 3 - "DB Session & Migration Tests (BE)"
Cohesion: 0.06
Nodes (26): normalize_database_url(), Point bare Postgres URLs at the driver this project actually installs. Why:…, fixture, Path, Session, sessionmaker, Tests for the persistence layer: models, repository functions, and the initial…, `update_cv_conditional`: the autosave concurrency guarantee. (+18 more)

### Community 4 - "Google Sign-in & Session (BE)"
Cohesion: 0.08
Nodes (48): AuthStatus, Depends, RedirectResponse, cookie_is_https_only(), decode_cookie(), encode_cookie(), generate_session_token(), get_current_user() (+40 more)

### Community 5 - "CV CRUD Endpoints (BE)"
Cohesion: 0.08
Nodes (46): apply_update_result(), create_cv(), cv_documents(), cv_to_detail(), cv_to_summary(), duplicate_cv(), get_cv(), get_owned_cv_or_404() (+38 more)

### Community 6 - "Sign-in & Anonymous Merge Tests (BE)"
Cohesion: 0.09
Nodes (25): client(), make_client(), patch_identity(), fixture, TestClient, Contract tests for Phase 6: Google sign-in and the anonymous merge. Why there…, Run a full start -> callback sign-in against the patched identity. Why it goes…, `GET /api/auth/me` -- who am I, and is sign-in even offered here. (+17 more)

### Community 7 - "CV API Tests (BE)"
Cohesion: 0.09
Nodes (21): client(), create_default_cv(), make_client(), fixture, TestClient, Contract tests for Phase 4b: session identity, `/api/cvs`, `/api/preferences`.…, `GET/POST/PUT/DELETE /api/cvs` happy paths., A CV id belonging to another session must look exactly like 404. (+13 more)

### Community 8 - "Form Field Components (FE)"
Cohesion: 0.11
Nodes (13): errorsAtPath(), errorsUnderPath(), hasUnclaimedErrors(), applyOp(), cloneContainer(), cloneSpineTo(), collapseOps(), getChild() (+5 more)

### Community 9 - "FastAPI App & Error Boundary (BE)"
Cohesion: 0.08
Nodes (41): FastAPI, lifespan(), parse_document(), patch_document(), post, Response, FastAPI application exposing the rendercv core as a web service. Why: Phase 0…, Convert the validated request model into the core wrapper's document shape.… (+33 more)

### Community 10 - "YAML Round-trip & Patch (BE)"
Cohesion: 0.10
Nodes (38): Exception, PatchOp, apply_delete(), apply_insert(), apply_move(), apply_patch_ops(), apply_set(), build_document_yaml() (+30 more)

### Community 11 - "DB Session & Engine (BE)"
Cohesion: 0.09
Nodes (32): Config, Engine, Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Persistence layer for the RenderCV Web Editor (Phase 4a). Why: Isolates…, build_alembic_config() (+24 more)

### Community 12 - "Document API Tests (BE)"
Cohesion: 0.08
Nodes (17): client(), fixture, TestClient, Contract tests for the comment-preserving YAML document endpoints. Why: `POST…, The scenario required verbatim: one `set` op, everything else intact., Contract tests for each `POST /api/documents/patch` op type., 400 error-shape contract tests for `POST /api/documents/patch`., 413 size-cap contract test for `POST /api/documents/patch`. (+9 more)

### Community 13 - "Classic Theme (core)"
Cohesion: 0.10
Nodes (30): FontFamilyType, PydanticColor, BaseModelWithoutExtraKeys, Pydantic base model that rejects unrecognized fields. Why: Most RenderCV models…, Bold, ClassicTheme, Colors, Connections (+22 more)

### Community 14 - "Typst Renderer (core)"
Cohesion: 0.12
Nodes (28): generate_html(), Path, Generate HTML file from Markdown source with styling. Why: HTML format enables…, generate_markdown(), Path, Generate Markdown file from CV model via Jinja2 templates. Why: Markdown…, build_name_variants(), Path (+20 more)

### Community 15 - "Entry Template Rendering (core)"
Cohesion: 0.09
Nodes (34): EntryType, RuntimeError, Internal error indicating a bug in RenderCV logic. Why: Distinguishes…, RenderCVInternalError, format_single_date(), Format single date with locale-aware template or pass through custom strings.…, clean_trailing_parts(), process_authors() (+26 more)

### Community 16 - "Jinja Templater (core)"
Cohesion: 0.14
Nodes (30): Pattern, build_date_placeholders(), compute_time_span_string(), date_object_to_string(), format_date_range(), Date, Locale, Build all date-related template placeholders from a date and locale. Why: Date… (+22 more)

### Community 17 - "CV Entry Models (core)"
Cohesion: 0.15
Nodes (21): BaseModelWithExtraKeys, Pydantic base model that allows unrecognized fields. Why: Entry models need to…, BaseEntry, Base class for all CV entry types. Why: All entry types share common…, BaseEntryWithComplexFields, BaseEntryWithDate, BulletEntry, Single bullet point entry for simple list items. Why: Some sections contain… (+13 more)

### Community 18 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.06
Nodes (32): Apr, Aug, Dec, Feb, Jan, Jul, July, Jun (+24 more)

### Community 19 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.06
Nodes (32): April, August, Augustus, December, Februar, Februari, February, Januar (+24 more)

### Community 20 - "Render & Validate API Tests (BE)"
Cohesion: 0.10
Nodes (17): client(), minimal_request(), fixture, TestClient, Contract tests for the RenderCV Web Editor API. Why: Each endpoint…, Contract tests for `POST /api/render`., Contract tests for `GET /api/schema`., Contract tests for `GET /api/themes`. (+9 more)

### Community 21 - "Stores: auth (FE)"
Cohesion: 0.09
Nodes (15): AuthStatus, AuthStatusPayload, getAuthStatus(), GOOGLE_SIGN_IN_PATH, signedOutStatus(), signOut(), formatRelativeTime(), parseServerTimestamp() (+7 more)

### Community 22 - "RenderCV Model Builder (core)"
Cohesion: 0.14
Nodes (26): collect_input_file_paths(), Path, Unpack, Execute complete CV generation pipeline with progress tracking and error…, Collect all input file paths involved in a render. Why: A render may involve…, run_rendercv(), User-facing error carrying multiple structured validation errors. Why: YAML…, RenderCVUserValidationError (+18 more)

### Community 23 - "Variant Pydantic Model Generator (core)"
Cohesion: 0.15
Nodes (27): BaseModel, FieldInfo, FieldSpec, create_discriminator_field_spec(), create_nested_field_spec(), create_nested_model_variant_model(), create_simple_field_spec(), create_variant_pydantic_model() (+19 more)

### Community 24 - "Request & Response Models (BE)"
Cohesion: 0.12
Nodes (25): CvConflictError, Exception, FastAPI, The API's single exception boundary. Why: Guardrails ("Inside code"): one…, Raised when an autosave write loses the optimistic-concurrency check. Why:…, Store the current server-side state to return to the client. Args: current: The…, Convert one core validation error into the API's error shape. Args: error:…, Register the API's single exception boundary on the FastAPI app. Args: app: The… (+17 more)

### Community 25 - "CV API Client (FE)"
Cohesion: 0.14
Nodes (24): createCv(), CvDetailPayload, CvDocumentsPayload, CvSummaryPayload, CvVersionSummary, CvVersionSummaryPayload, deleteCv(), duplicateCv() (+16 more)

### Community 26 - "Client-side WASM Preview (FE)"
Cohesion: 0.12
Nodes (13): ctx, init(), loadWasmManifest(), WasmManifest, BundledTypstPackage, LocalPackageRegistry, createPyodideEngine(), PyodideEngineHandle (+5 more)

### Community 27 - "Create-theme Command (core)"
Cohesion: 0.13
Nodes (20): create_init_file_for_theme(), Path, Generate `__init__.py` for custom theme by templating from ClassicTheme. Why:…, cli_command_create_theme(), Argument, command, help, handle_user_errors() (+12 more)

### Community 28 - "Preview Render Controller (FE)"
Cohesion: 0.13
Nodes (17): renderPreview(), RenderResult, docs, genericSystemError(), ClientRenderEngine, createRenderController(), activate(), clientEngineUsable() (+9 more)

### Community 29 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.16
Nodes (25): properties, $ref, properties, properties, properties, $ref, $ref, $ref (+17 more)

### Community 30 - "Locale Translations (core)"
Cohesion: 0.10
Nodes (24): Locale Localization Schema, Arabic locale (RTL; 'DEGREE في AREA'; Gregorian month names transliterated), Danish locale ('DEGREE i AREA'; year/years both 'år'), DEGREE/AREA phrase ordering rationale: each locale's degree_with_area template reorders the DEGREE and AREA placeholders and picks the joining preposition to match natural word order in that language — most European languages keep DEGREE first with a preposition (in/en/em/i/di/в/ngành), while Hindi, Japanese, Korean, Mandarin Chinese, and Turkish place AREA first because the field of study naturally precedes the degree name in those languages, Dutch locale ('DEGREE in AREA'; present = 'heden'), French locale ('DEGREE en AREA'; month/months both 'mois'), German locale ('DEGREE in AREA'; present = 'gegenwärtig'), Hebrew locale (RTL; 'DEGREE בAREA' with prefixed preposition; apostrophe-marked month abbreviations) (+16 more)

### Community 31 - "New Command: copy_templates (core)"
Cohesion: 0.11
Nodes (19): available_locales, available_themes, join, Panel, copy_templates(), make_tree_writable(), Path, Copy built-in template directory to user location for customization. Why: Users… (+11 more)

### Community 32 - "Section (core)"
Cohesion: 0.12
Nodes (19): EntryModel, CustomConnection, User-defined contact method with custom icon and URL. Why: Built-in social…, Cv, Transform user's section dict to list of typed section objects. Why: Templates…, BaseRenderCVSection, create_section_models(), dictionary_key_to_proper_section_title() (+11 more)

### Community 33 - "Sample Generator (core)"
Cohesion: 0.19
Nodes (22): comment_out_section_sub_fields(), create_sample_cv_file(), create_sample_design_file(), create_sample_locale_file(), create_sample_rendercv_pydantic_model(), create_sample_settings_file(), create_sample_yaml_file(), create_sample_yaml_input_file() (+14 more)

### Community 34 - "App (core)"
Cohesion: 0.13
Nodes (21): callback, cli_command_no_args(), fetch_and_cache_latest_version(), fetch_latest_version_from_pypi(), get_cache_dir(), get_version_cache_file(), Context, help (+13 more)

### Community 35 - "Progress Panel (core)"
Cohesion: 0.13
Nodes (14): CompletedStep, format_validation_error_location(), ProgressPanel, Path, Display error panel and exit with error code. Args: user_error: User-facing…, Display validation errors in table format and exit. Why: Pydantic validation…, Format schema/YAML location for validation error table rows. Why: YAML parsing…, Clear all completed steps and panel display. (+6 more)

### Community 36 - "API Clients (FE)"
Cohesion: 0.18
Nodes (12): parseCvDocument(), ParseResult, patchCvDocument(), PatchOpError, PatchResult, apiFetch(), ThemeInfo, parseValidationErrors() (+4 more)

### Community 37 - "YAML Reader (core)"
Cohesion: 0.12
Nodes (17): ClassicTheme, EnglishLocale, discover_other_themes(), Auto-discover and load theme variant classes from other_themes/ directory. Why:…, discover_other_locales(), Auto-discover and load locale variant classes from other_locales/ directory.…, build_yaml_parser(), CommentedMap (+9 more)

### Community 38 - "Package: package (FE)"
Cohesion: 0.10
Nodes (21): codemirror, @codemirror/commands, @codemirror/lang-yaml, @codemirror/language, @codemirror/lint, @codemirror/state, @codemirror/view, @lezer/highlight (+13 more)

### Community 39 - "Package: package (FE)"
Cohesion: 0.10
Nodes (21): @playwright/test, svelte-check, @sveltejs/adapter-auto, @sveltejs/kit, @sveltejs/vite-plugin-svelte, tailwindcss, @tailwindcss/vite, typescript (+13 more)

### Community 40 - "Playwright E2E Suite (FE)"
Cohesion: 0.16
Nodes (3): switchToFormMode(), firstPreviewUrl(), gotoReady()

### Community 41 - "Stores: documents (FE)"
Cohesion: 0.15
Nodes (9): derivePdfFilename(), extractScalar(), sanitizeFilename(), createDefaultDocuments(), DOCUMENT_LABELS, documents, resetDocuments(), setDocument() (+1 more)

### Community 42 - "WASM Engine Handle (FE)"
Cohesion: 0.18
Nodes (5): PendingRender, FakeWorker, WasmRenderEngine, WasmEngineRequest, WasmEngineResponse

### Community 43 - "Connections (core)"
Cohesion: 0.15
Nodes (18): Environment, compute_connections(), compute_connections_for_markdown(), compute_connections_for_typst(), Connection, parse_connections(), Format connections with Typst markup, Font Awesome icons, and conditional…, Format connections as Markdown links without icons. Args: rendercv_model: CV… (+10 more)

### Community 44 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.11
Nodes (19): fontawesome_icon, placeholder, url, additionalProperties, description, properties, required, title (+11 more)

### Community 45 - "Documenteditors (FE)"
Cohesion: 0.22
Nodes (8): applyDiagnostics(), DocumentEditorRegistry, externalDocUpdate(), isSyncTransaction(), lineDiagnostic(), syncAnnotation, DOCUMENT_KEYS, DocumentKey

### Community 46 - "PDF PNG (core)"
Cohesion: 0.21
Nodes (16): Compiler, copy_photo_next_to_typst_file(), generate_pdf(), generate_png(), get_package_path(), get_typst_compiler(), install_bundled_typst_package(), Path (+8 more)

### Community 47 - "Watcher (core)"
Cohesion: 0.12
Nodes (14): DirModifiedEvent, FileModifiedEvent, cli_command_render(), Argument, command, Context, help, Option (+6 more)

### Community 48 - "Autosave: autosave (FE)"
Cohesion: 0.15
Nodes (12): UpdateCvResult, AutosaveBaseline, AutosaveController, AutosaveControllerOptions, AutosaveState, AutosaveStatus, documentsEqual(), initialState() (+4 more)

### Community 49 - "Validatecontroller (FE)"
Cohesion: 0.19
Nodes (12): docs, validateDocuments(), ValidateResult, createValidateController(), activate(), runValidate(), scheduleValidate(), DocumentSource (+4 more)

### Community 50 - "CV: cv (core)"
Cohesion: 0.12
Nodes (13): EmailStr, field_serializer, ModelWrapValidatorHandler, PhoneNumber, Any, field_validator, HttpUrl, model_validator (+5 more)

### Community 51 - "Models: path (core)"
Cohesion: 0.15
Nodes (14): Any, ValidationInfo, Validate design options for built-in or custom themes with dynamic loading.…, validate_design(), Path, ValidationInfo, Convert relative path to absolute path based on input file location. Why: Users…, resolve_relative_path() (+6 more)

### Community 52 - "Pydantic Error Handling (core)"
Cohesion: 0.21
Nodes (13): ErrorDetails, CustomPydanticErrorTypes, get_coordinates_of_a_key_in_a_yaml_object(), get_inner_yaml_object_from_its_key(), parse_plain_pydantic_error(), parse_validation_errors(), Any, CommentedMap (+5 more)

### Community 53 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.13
Nodes (15): anyOf, additionalProperties, title, type, $defs, ArbitraryDate, ClassicTheme, EngineeringclassicTheme (+7 more)

### Community 54 - "@codemirror (FE)"
Cohesion: 0.16
Nodes (4): if(), wrapAsLink(), WrapResult, wrapSelection()

### Community 55 - "Tsconfig (FE)"
Cohesion: 0.14
Nodes (13): ./.svelte-kit/tsconfig.json, compilerOptions, allowJs, checkJs, esModuleInterop, forceConsistentCasingInFileNames, moduleResolution, resolveJsonModule (+5 more)

### Community 56 - "Schema (BE)"
Cohesion: 0.15
Nodes (13): Any, get, Serve the repository's root JSON Schema for the form generator. Returns: Parsed…, List built-in themes with their default design options. Returns: One entry per…, schema(), themes(), load_schema(), Any (+5 more)

### Community 57 - "Errorclassification (FE)"
Cohesion: 0.22
Nodes (11): ValidationError, YamlSource, classifyError(), documentKeyForError(), ErrorCategory, groupErrorsByDocument(), isSyntaxError(), YAML_SOURCE_TO_DOCUMENT_KEY (+3 more)

### Community 58 - "Form (FE)"
Cohesion: 0.26
Nodes (10): buildDiscriminatorSwitchOp(), buildEnsurePathOps(), buildResetFieldOp(), buildSetFieldOp(), deepMerge(), isPathOverridden(), isPlainObject(), OverrideInfo (+2 more)

### Community 59 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.14
Nodes (14): discriminator, oneOf, BuiltInDesign, mapping, propertyName, classic, ember, engineeringclassic (+6 more)

### Community 60 - "Readme: README (FE)"
Cohesion: 0.18
Nodes (13): rendercv-web-frontend, Single shared setup/run/test doc in ../README.md, SvelteKit + TypeScript + Tailwind stack, Autosave, Four document tabs (CV, Design, Locale, Settings), graphify-out/GRAPH_REPORT.md, npm install, RenderCV Web Editor (+5 more)

### Community 61 - "Build WASM Assets (FE)"
Cohesion: 0.23
Nodes (12): buildWheel(), copyFonts(), copyInto(), copyTypstCompilerWasm(), copyTypstPackages(), FONT_FILES, FRONTEND_ROOT, main() (+4 more)

### Community 62 - "Formsync (FE)"
Cohesion: 0.29
Nodes (10): createFormSync(), activate(), applyOptimistic(), currentCvYaml(), destroy(), flush(), reparse(), scheduleFlush() (+2 more)

### Community 63 - "Autosave: autosave (FE)"
Cohesion: 0.32
Nodes (10): createAutosaveController(), flush(), flushBeforeUnload(), isDirty(), performSave(), resolveConflict(), retryNow(), runSave() (+2 more)

### Community 64 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.22
Nodes (11): 2020, 2020-09, 2020-09-24, Fall 2023, Summer 2020, anyOf, default, description (+3 more)

### Community 65 - "Other Themes: README (core)"
Cohesion: 0.24
Nodes (11): RenderCV Typst Package Changelog, RTL Text Direction Support, RenderCV Typst Package README, RenderCV Typst Package (@preview/rendercv), typst-fontawesome Library README, fa-icon Typst Function, Engineering Classic Theme Design Overrides, Engineering Resumes Theme Design Overrides (+3 more)

### Community 66 - "Social Network (core)"
Cohesion: 0.18
Nodes (7): field_validator, model_validator, ValidationInfo, Validate generated URL is well-formed. Why: URL generation from username might…, Generate profile URL from network and username. Why: Users provide…, Validate username format per network's requirements. Why: Different platforms…, SocialNetwork

### Community 67 - "Package: package (FE)"
Cohesion: 0.18
Nodes (11): scripts, build, build:wasm-assets, check, check:watch, dev, prepare, preview (+3 more)

### Community 68 - "App (FE)"
Cohesion: 0.20
Nodes (11): Frontend README (sv / SvelteKit scaffold), npm run dev / build / preview workflow, Scaffold configuration: minimal template, TypeScript, tailwindcss, vitest unit tests, sv CLI (sv@0.17.0, sveltejs/cli), SvelteKit deployment adapter (may be required for target environment), documentElement 'dark' class toggle with prefers-color-scheme fallback and try/catch light fallback, localStorage key 'rendercv.uiTheme', Rationale: apply saved theme before first paint to avoid a flash of the wrong theme; server preferences arrive async, so only the localStorage mirror or OS preference is available at this point (+3 more)

### Community 69 - "Readme"
Cohesion: 0.24
Nodes (11): Anonymous CV merge on first sign-in, Anonymous signed-cookie session, Cross-origin CORS configuration, Deploy, GOOGLE_OAUTH_CLIENT_ID / _SECRET / _REDIRECT_URI, /api/auth/google/callback redirect URI, Optional Google sign-in, provider_available: false hides sign-in UI (+3 more)

### Community 70 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.20
Nodes (10): ●, Excellent communication skills, Python, JavaScript, C++, enum, examples, title, type, properties (+2 more)

### Community 71 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.20
Nodes (10): 2024, 2024-05, 2024-05-20, present, anyOf, default, description, examples (+2 more)

### Community 72 - "Helper (core)"
Cohesion: 0.29
Nodes (9): fetch_icons(), generate_gallery(), generate_lib(), main(), map_icons(), Generate typst library files for FontAwesome icons. Args: icon_maps: A…, Generate a typst gallery file for FontAwesome icons. Args: icon_maps: A…, Fetch icons from FontAwesome API for a specific version. Args: version: The… (+1 more)

### Community 73 - "Settings: settings (core)"
Cohesion: 0.27
Nodes (5): RenderCommand, field_validator, model_validator, Remove duplicate keywords from bold list. Why: Users might accidentally list…, Settings

### Community 74 - "Preferences (BE)"
Cohesion: 0.22
Nodes (10): PreferenceUpdateRequest, Request body for `PUT /api/preferences`., get_preferences(), CurrentUser, get, put, SessionDep, List the current session's UI preferences. Args: current_user: The session's… (+2 more)

### Community 75 - "Bootstrap (FE)"
Cohesion: 0.33
Nodes (6): CvDetail, CvSummary, bootstrapApp(), BootstrapDeps, BootstrapResult, pickCv()

### Community 76 - "Cvsessionactions (FE)"
Cohesion: 0.36
Nodes (8): createCvSessionActions(), createNew(), duplicate(), loadInto(), remove(), restore(), switchTo(), toSummary()

### Community 77 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.22
Nodes (9): BA, BS, MS, PhD, anyOf, default, examples, title (+1 more)

### Community 78 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.22
Nodes (9): https://example.com/photo.jpg, images/profile.png, photo.jpg, anyOf, default, description, examples, title (+1 more)

### Community 79 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.22
Nodes (9): Istanbul, Türkiye, London, UK, New York, NY, Remote, anyOf, default, examples, title (+1 more)

### Community 80 - "English Locale (core)"
Cohesion: 0.22
Nodes (5): EnglishLocale, Phrases, Get ISO 639-1 two-letter language code for locale. Why: Typst's text element…, Get flag emoji for the locale's primary country. Why: Flag emojis are displayed…, Check if language uses right-to-left text direction. Returns: True if language…

### Community 81 - "Readme: README (BE)"
Cohesion: 0.22
Nodes (9): cv-editor-web-app plan reference, rendercv-web-backend README, FastAPI backend for the RenderCV Web Editor, JSON schema HTTP capability, PDF rendering HTTP capability, rendercv core (editable path dependency), Theme defaults HTTP capability, Validation HTTP capability (+1 more)

### Community 82 - "Readme: README (FE)"
Cohesion: 0.28
Nodes (9): npm run test:e2e, Playwright end-to-end suite, Playwright frontend on port 5199, uv sync --extra postgres, Postgres URL normalization, RENDERCV_WEB_DATABASE_URL, Default SQLite database file, Throwaway e2e database (+1 more)

### Community 83 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.22
Nodes (9): additionalProperties, properties, title, type, Cv, social_networks, anyOf, default (+1 more)

### Community 84 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): area, institution, EducationEntry, additionalProperties, description, required, title, type

### Community 85 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): Boğaziçi University, Harvard University, MIT, properties, examples, title, type, institution

### Community 86 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): Computer Science, Electrical Engineering, Mechanical Engineering, description, examples, title, type, area

### Community 87 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): Data Scientist, Product Manager, Software Engineer, anyOf, default, examples, title, headline

### Community 88 - "Validation Context (core)"
Cohesion: 0.25
Nodes (7): model_validator, Self, ValidationInfo, get_current_date(), Date, ValidationInfo, Extract current date from validation context or default to today. Why: Date…

### Community 89 - "Cache (BE)"
Cohesion: 0.25
Nodes (5): Thread-safe, size-capped cache of rendered PDF bytes. Why: FastAPI can serve a…, Create an empty cache. Args: max_entries: Maximum number of cached renders to…, Look up a cached render by key. Args: key: Cache key, as produced by…, Store a render, evicting the oldest entry once over capacity. Args: key: Cache…, RenderCache

### Community 90 - "Dimension (FE)"
Cohesion: 0.36
Nodes (5): DIMENSION_UNITS, DimensionUnit, ParsedDimension, parseDimension(), serializeDimension()

### Community 91 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): DutchLocale, additionalProperties, properties, title, type, description, $ref, phrases

### Community 92 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.25
Nodes (8): EnglishLocale, additionalProperties, properties, default, description, title, type, months

### Community 93 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.29
Nodes (7): bullet, additionalProperties, description, required, title, type, BulletEntry

### Community 94 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.29
Nodes (7): Completed advanced coursework in machine learning and artificial intelligence., Led a team of 5 engineers to develop innovative solutions., summary, anyOf, default, examples, title

### Community 95 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.29
Nodes (7): Jane Smith, John Doe, anyOf, default, examples, title, name

### Community 96 - "Readme: README (FE)"
Cohesion: 0.33
Nodes (7): Core wrapper HTTP surface (validate, render, schema, theme defaults), Frontend /api communication with backend, npm run dev, /api/render backend renderer, Playwright workers: 1, uv run uvicorn rendercv_web.app:app --port 8000, Vite /api proxy to port 8000

### Community 97 - "Themes (BE)"
Cohesion: 0.33
Nodes (6): One built-in theme's name and default design options., ThemeInfo, list_theme_defaults(), ThemeInfo, Theme listing endpoint support: names and per-theme design defaults. Why:…, Build the default design options for every built-in theme. Why: Instantiating…

### Community 98 - "Readme: README (FE)"
Cohesion: 0.29
Nodes (7): npm run build, npm run check (svelte-check), npm run test (Vitest), uv run pytest -q (backend gate), just check, just test, Per-layer green gates before PR

### Community 99 - "Readme: README (FE)"
Cohesion: 0.33
Nodes (7): src/lib/wasm client-side render engine, npm run build:wasm-assets, Pyodide, typst.ts browser compiler, Client-side WASM preview, WASM preview known limitations, localStorage flag rendercv.wasmPreview

### Community 100 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.29
Nodes (7): type, items, description, items, title, type, month_names

### Community 101 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.29
Nodes (7): sections, anyOf, default, description, examples, $ref, title

### Community 102 - "Run Rendercv (core)"
Cohesion: 0.33
Nodes (6): args, kwargs, P, T, Execute function, measure timing, and update progress panel with result. Why:…, timed_step()

### Community 103 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): +1-234-567-8900, default, description, examples, title, phone

### Community 104 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): center, left, right, enum, type, Alignment

### Community 105 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): https://johndoe.com, website, default, description, examples, title

### Community 106 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): john.doe@example.com, default, description, examples, title, email

### Community 107 - "Entry Point (core)"
Cohesion: 0.40
Nodes (4): entry_point(), Entry point for the RenderCV CLI. Why: Users might install RenderCV with `pip…, Entry point for the RenderCV CLI., `__main__.py` file is the file that gets executed when the RenderCV package…

### Community 108 - "Entries: EducationEntry.j2 (core)"
Cohesion: 0.33
Nodes (6): Markdown EducationEntry Template, Markdown ExperienceEntry Template, Markdown NormalEntry Template, Markdown PublicationEntry Template, Ember Theme Design Overrides, Opal Theme Design Overrides

### Community 109 - "Publication (core)"
Cohesion: 0.40
Nodes (4): model_validator, Self, Prioritize DOI over custom URL when both provided. Why: DOI is canonical,…, Validate generated DOI URL is well-formed. Why: DOI URL generation from DOI…

### Community 110 - "Readme: README (BE)"
Cohesion: 0.47
Nodes (6): rendercv-web-backend, Editable path dependency on core, rendercv Python core, uv-only Python tooling policy, uv sync, web/backend FastAPI service

### Community 111 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): anyOf, default, description, examples, title, custom_connections

### Community 112 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): const, default, description, title, type, language

### Community 113 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.33
Nodes (6): description, maxItems, minItems, title, type, month_abbreviations

### Community 115 - "Cvs (BE)"
Cohesion: 0.50
Nodes (5): delete, delete_cv(), Delete a CV and its version history. Why: Returns `None` rather than a fresh…, delete_cv(), Delete a CV (and, via `ON DELETE CASCADE`, its versions). Args: session: The…

### Community 116 - "Markdown Parser (core)"
Cohesion: 0.40
Nodes (5): Element, escape_typst_characters(), Recursively convert XML Element tree to Typst markup string. Why: Python…, Escape Typst special characters while preserving Typst commands and math. Why:…, to_typst_string()

### Community 117 - "JSON Schema Generator (core)"
Cohesion: 0.40
Nodes (5): generate_json_schema(), generate_json_schema_file(), Path, Generate JSON Schema (Draft-07) from RenderCV Pydantic models. Why: IDEs and…, Generate and save JSON Schema to file. Args: json_schema_path: Target file path…

### Community 118 - "320e31bb905f Add OAuth Identity Columns To Users (BE)"
Cohesion: 0.40
Nodes (4): downgrade(), Add the nullable account-identity columns and their unique constraint., Drop the account-identity columns, returning `users` to anonymous-only., upgrade()

### Community 119 - "8a6ebf56c34d Create Baseline Schema (BE)"
Cohesion: 0.40
Nodes (4): downgrade(), Create `users`, `cvs`, `preferences`, and `cv_versions`., Drop the four baseline tables, children before parents., upgrade()

### Community 120 - "Documents (BE)"
Cohesion: 0.40
Nodes (4): RoundTripScanner, Treat `*` as a plain scalar character instead of alias syntax. Why: Mirrors…, Treat `*` as a plain scalar character instead of alias syntax., ScannerNoAlias

### Community 121 - "Limits (BE)"
Cohesion: 0.60
Nodes (4): enforce_documents_size_cap(), enforce_yaml_size_cap(), Shared request-size guardrails (guardrails: "trust no one"). Why: Every YAML…, Reject a single YAML document over the size cap before it reaches the core.…

### Community 122 - "Package: package (FE)"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 123 - "Cvsessionactions Test (FE)"
Cohesion: 0.60
Nodes (3): detail(), docs(), makeStores()

### Community 124 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): additionalProperties, properties, title, type, ArabicLocale

### Community 125 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): additionalProperties, properties, title, type, DanishLocale

### Community 126 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): default, description, title, type, last_updated

### Community 127 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): default, description, title, type, month

### Community 128 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): default, description, title, type, present

### Community 129 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): year, default, description, title, type

### Community 130 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.40
Nodes (5): years, default, description, title, type

### Community 131 - "Full (core)"
Cohesion: 0.50
Nodes (4): HTML Full Page Template, GitHub Markdown CSS (CDN), KaTeX Math Rendering (CDN), Markdown Header Template

### Community 132 - "Rendercv Model (core)"
Cohesion: 0.50
Nodes (3): model_validator, ValidationInfo, Store input file path in private attribute for path resolution. Why: Photo…

### Community 134 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.50
Nodes (4): EmberTheme, additionalProperties, title, type

### Community 135 - "Schema Snapshot: schema.snapshot (FE)"
Cohesion: 0.50
Nodes (4): start_date, anyOf, default, description

### Community 136 - "Thumbnail (core)"
Cohesion: 1.00
Nodes (3): John Doe synthetic sample CV (education, experience sections used as RenderCV demo content), RenderCV PDF output (YAML-to-PDF rendered CV with professional typography), RenderCV sample CV thumbnail (John Doe, classic-style theme preview)

## Ambiguous Edges - Review These
- `Markdown EducationEntry Template` → `Ember Theme Design Overrides`  [AMBIGUOUS]
  src/rendercv/renderer/templater/templates/markdown/entries/EducationEntry.j2.md · relation: shares_data_with

## Knowledge Gaps
- **451 isolated node(s):** `CvDocumentsPayload`, `CvVersionSummary`, `CvVersionSummaryPayload`, `SectionsMap`, `WrapResult` (+446 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Markdown EducationEntry Template` and `Ember Theme Design Overrides`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **Why does `$defs` connect `Schema Snapshot: schema.snapshot (FE)` to `Sections & Entry Forms (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `RenderCVUserError` connect `Create-theme Command (core)` to `Sample Generator (core)`, `Progress Panel (core)`, `Typst Renderer (core)`, `Jinja Templater (core)`, `Models: path (core)`, `RenderCV Model Builder (core)`, `Request & Response Models (BE)`, `New Command: copy_templates (core)`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `properties` connect `Schema Snapshot: schema.snapshot (FE)` to `Schema Snapshot: schema.snapshot (FE)`, `Sections & Entry Forms (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`, `Schema Snapshot: schema.snapshot (FE)`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `BaseModelWithoutExtraKeys` (e.g. with `Bold` and `ClassicTheme`) actually correct?**
  _`BaseModelWithoutExtraKeys` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RenderCVModel` (e.g. with `generate_html()` and `generate_markdown()`) actually correct?**
  _`RenderCVModel` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CvDocumentsPayload`, `CvVersionSummary`, `CvVersionSummaryPayload` to the rest of the system?**
  _451 weakly-connected nodes found - possible documentation gaps or missing edges._
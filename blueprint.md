# RenderCV Workflow (Sequence Diagrams)

This file sketches the control flow through the render pipeline so newcomers can quickly see how the CLI, validation, and renderers cooperate.

## CLI Entry and Dispatch (`rendercv render`)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant CLI as Typer app (`rendercv`)
    participant Decorator as handle_user_errors
    participant Cmd as cli_command_render
    participant Overrides as parse_override_arguments
    participant Watcher as run_function_if_file_changes
    participant Runner as run_rendercv_wrapper

    U->>CLI: rendercv render <input> [options]
    CLI->>Decorator: dispatch render command
    Decorator->>Cmd: call
    Cmd->>Overrides: parse extra --foo.bar "value"
    Overrides-->>Cmd: overrides dict | RenderCVUserError on shape issues
    Cmd->>Cmd: assemble BuildRendercvModelArguments\n(paths, dont_generate flags, overrides)
    Cmd->>Runner: define wrapper -> run_rendercv / run_rendercv_quietly
    alt --watch provided
        Cmd->>Watcher: run_function_if_file_changes(input_path, Runner)
        Watcher->>Runner: initial call
        loop on file change
            Files-->>Watcher: watchdog FileModifiedEvent
            Watcher->>Runner: re-run render pipeline
        end
    else
        Cmd->>Runner: execute once
    end
    Runner-->>Decorator: propagate success or RenderCVUserError
    Decorator->>U: print message on error, exit 1
```

Key notes:
- `run_rendercv` shows a live progress panel; `run_rendercv_quietly` skips the UI but follows the same steps.
- The decorator only catches `RenderCVUserError`, letting unexpected exceptions surface for debugging.

## Model Build and Validation

```mermaid
sequenceDiagram
    autonumber
    participant Runner as run_rendercv*
    participant Build as build_rendercv_dictionary_and_model
    participant Dict as build_rendercv_dictionary
    participant Reader as read_yaml
    participant Overrides as apply_overrides_to_dictionary
    participant Model as build_rendercv_model_from_commented_map
    participant Pydantic as RenderCVModel.model_validate
    participant Errors as parse_validation_errors

    Runner->>Build: BuildRendercvModelArguments (paths, flags, overrides)
    Build->>Dict: build_rendercv_dictionary(...)
    Dict->>Reader: read_yaml(main_input)
    alt optional design/locale/settings files
        Dict->>Reader: read_yaml(overlay)\nassign into input dict
    end
    Dict->>Dict: merge render_command CLI overrides\n(paths, dont_generate*)
    alt CLI data overrides provided
        Dict->>Overrides: apply_overrides_to_dictionary(input_dict, overrides)
        Overrides-->>Dict: deep-updated dict or RenderCVUserError
    end
    Dict-->>Build: CommentedMap (preserves YAML coords)
    Build->>Model: build_rendercv_model_from_commented_map(dict, input_path)
    Model->>Pydantic: RenderCVModel.model_validate(context=ValidationContext)
    alt validation fails
        Pydantic-->>Errors: ValidationError
        Errors-->>Runner: RenderCVUserValidationError(validation_errors)
    else validation ok
        Pydantic-->>Model: RenderCVModel instance\n(with resolved paths, defaults)
        Model-->>Build: (dict, model)
        Build-->>Runner: (dict, model)
    end
```

Key notes:
- `ValidationContext` carries the input file path and current date into validators (for relative paths, time spans, etc.).
- YAML is read with ISO date parsing disabled so dates stay as strings until validated.
- Validation errors are rewritten with user-friendly messages and YAML coordinates, then printed by `print_validation_errors` inside `run_rendercv`.

## Rendering Pipeline (typst → pdf/png + md → html)

```mermaid
sequenceDiagram
    autonumber
    participant Runner as run_rendercv*
    participant Progress as timed_step/progress panel
    participant TypstGen as generate_typst
    participant Tpl as render_full_template
    participant Proc as process_model
    participant Jinja as jinja2 env
    participant Path as resolve_rendercv_file_path
    participant PDF as generate_pdf
    participant PNG as generate_png
    participant MD as generate_markdown
    participant HTML as generate_html

    Runner->>Progress: timed_step("Validated the input file", BuildRendercv...)
    Runner->>Progress: timed_step("Generated Typst", TypstGen(model))
    alt dont_generate_typst flag
        TypstGen-->>Runner: None (skip downstream typst consumers)
    else
        TypstGen->>Path: resolve_rendercv_file_path(model, typst_path tmpl)
        TypstGen->>Tpl: render_full_template(model, "typst")
        Tpl->>Proc: process_model(model, "typst")
        Proc->>Proc: compute connections, top note, footer\nstring processing & keyword bolding
        Proc->>Proc: expand entry templates (dates, URLs, summaries)
        Tpl->>Jinja: render templates (user overrides > bundled templates)
        Jinja-->>TypstGen: typst source string
        TypstGen->>TypstGen: write typst file
    end
    Runner->>Progress: timed_step("Generated PDF", PDF(model, typst_path))
    alt typst_path is None or dont_generate_pdf
        PDF-->>Runner: None
    else
        PDF->>Path: resolve_rendercv_file_path(model, pdf_path tmpl)
        PDF->>typst.Compiler: compile(format="pdf", font_paths=[rendercv_fonts,...])
        PDF->>PDF: copy photo next to typst if needed
        typst.Compiler-->>PDF: pdf bytes->file
    end
    Runner->>Progress: timed_step("Generated PNG", PNG(model, typst_path))
    alt typst_path is None or dont_generate_png
        PNG-->>Runner: None
    else
        PNG->>Path: resolve_rendercv_file_path(model, png_path tmpl)
        PNG->>typst.Compiler: compile(format="png")
        PNG->>PNG: emit page_1.png, page_2.png, ...
    end
    Runner->>Progress: timed_step("Generated Markdown", MD(model))
    alt dont_generate_markdown
        MD-->>Runner: None
    else
        MD->>Path: resolve_rendercv_file_path(model, markdown_path tmpl)
        MD->>Tpl: render_full_template(model, "markdown")
        Tpl->>Proc: process_model(model, "markdown")\n(no markdown→typst conversion)
        Tpl->>Jinja: render markdown templates
        MD->>MD: write markdown file
    end
    Runner->>Progress: timed_step("Generated HTML", HTML(model, md_path))
    alt markdown_path is None or dont_generate_html
        HTML-->>Runner: None
    else
        HTML->>Path: resolve_rendercv_file_path(model, html_path tmpl)
        HTML->>HTML: markdown_to_html(md_text)
        HTML->>Jinja: render html/Full.html (wraps body)
        HTML->>HTML: write html file
    end
    Runner->>Progress: update panel title "Your CV is ready"
    note over Runner: Errors caught:\n- YAML parse → RenderCVUserError\n- Jinja syntax → RenderCVUserError\n- Validation → print_validation_errors then RenderCVUserError
```

Key notes:
- `render_full_template` re-processes the model per output type, so typst and markdown runs can diverge (e.g., markdown_to_typst filter only for typst).
- Template lookup order: user folder containing the input file (allows overrides) → bundled templates directory.
- `resolve_rendercv_file_path` substitutes placeholders such as `NAME`, `MONTH_NAME`, etc., and ensures parent folders exist.
- `typst.Compiler` is cached per typst path for reuse between PDF and PNG renders; font search includes `rendercv_fonts` plus `./fonts` or `<input_dir>/fonts`.

## Watch Mode Loop (when `--watch` is set)

```mermaid
sequenceDiagram
    autonumber
    participant Watcher as watchdog Observer
    participant Handler as EventHandler.on_modified
    participant Runner as run_rendercv_wrapper
    participant User as Editing files

    Watcher->>Handler: initial synthetic FileModifiedEvent
    Handler->>Runner: invoke render pipeline
    loop forever
        User-->>Watcher: save input YAML (or same dir on Windows)
        Watcher->>Handler: FileModifiedEvent
        Handler->>Runner: invoke render pipeline
        note over Handler: RenderCVUserError is caught\nand printed without killing watcher
    end
```

Key notes:
- On Windows the observer watches the directory because single-file watching is unsupported.
- The watchdog thread is kept alive with a sleep loop and stops cleanly on `KeyboardInterrupt`.

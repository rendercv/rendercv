# Upgrade from v2.8

Most CVs render the same in v2.9. These changes may need your attention.

## Paths given on the command line

Relative paths given on the command line are relative to the folder you run `rendercv` in, not to the CV's folder. Run from `/work`, this command writes `/work/review/jane.pdf`, where v2.8 wrote `/work/cvs/review/jane.pdf`:

```bash
rendercv render cvs/Jane_CV.yaml --pdf-path review/jane.pdf
```

The same goes for dotted options like `--cv.photo`. Paths written in YAML files are still relative to the main CV file. See [Paths](../yaml_input_structure/settings.md#paths).

## Outputs

- An output can't overwrite an input file or another output. RenderCV reports the clash before writing anything.
- SVG files, one per page, are made by default. Set `settings.render_command.dont_generate_svg: true` to turn them off.
- `dont_generate_typst: true` no longer stops the PDF, PNG, and SVG files. It only skips saving the `.typ` file.
- The photo must be an image file.

## Accessible PDFs

PDFs conform to PDF/UA-1, the accessibility standard, which needs `cv.name` and alternative text for images in Typst code, like `#image("logo.png", alt: "Logo")`. To make an ordinary PDF instead, set `settings.pdf_profile: standard`.

## Templates and themes

- A custom theme's `__init__.py` must define every design option of the classic theme. Recreate it with `rendercv create-theme` and copy your changes into it.
- Custom theme names must start with a letter.
- Templates written for RenderCV 1 are rejected.
- CLI overrides no longer accept negative list indices.

## Layout

Headings stay with the content that follows them, the time spans of month ranges count whole months (January to February is 2 months), and the small-capital headings of `ember` and `opal` use Source Sans 3. Lines can wrap differently, so check the new PDF before sending it.

## Editors

Point the `$schema` comment at the top of your YAML files to version 2.9's schema, so that your editor knows the new fields. See [JSON Schema](../yaml_input_structure/index.md#json-schema).

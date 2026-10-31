# Add a New Theme

A **theme** is a set of design choices: fonts, colors, spacing, and layout options. Every built-in theme starts from the Classic theme and lists only the values it changes, so a new theme is a single YAML file that reuses all of RenderCV's rendering code. A different page structure, as opposed to different styling, also needs [template changes](../../user_guide/how_to/override_default_templates.md).

1. Create a YAML file in `src/rendercv/schema/models/design/other_themes/`:

    ```bash
    touch src/rendercv/schema/models/design/other_themes/mytheme.yaml
    ```

2. Write the values that differ from Classic:

    ```yaml
    # yaml-language-server: $schema=../../../../../../schema.json
    design:
      theme: mytheme
      colors:
        name: rgb(0,0,0)
      typography:
        font_family: New Computer Modern
    ```

    The first line points your editor to RenderCV's [schema](../json_schema.md), so it suggests the available options as you type. `classic_theme.py`, in the folder above, lists every option with its Classic value.

3. Regenerate the files that list every theme: the schema, the examples, and the entry pictures in the user guide:

    ```bash
    just update-schema
    just update-examples
    just update-entry-figures
    ```

4. The tests render every theme and compare the result with saved reference files, which don't exist yet for the new theme. Create them, open the new theme's PDFs and images in `tests/renderer/testdata/` to check that they look right, and run the tests:

    ```bash
    just update-testdata
    just test
    ```

5. Use it:

    ```bash
    rendercv new "John Doe" --theme mytheme
    ```

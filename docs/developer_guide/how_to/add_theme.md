# Add a New Theme

1. Create a YAML file in `src/rendercv/schema/models/design/other_themes/`

    ```bash
    touch src/rendercv/schema/models/design/other_themes/mytheme.yaml
    ```

2. Add the schema reference and override Classic theme defaults

    ```yaml
    # yaml-language-server: $schema=../../../../../../schema.json
    design:
      theme: mytheme
      # Override any defaults from classic_theme.py here
      colors:
        name: rgb(0,0,0)
      typography:
        font_family: New Computer Modern
      # ... add any other overrides
    ```

3. Update the JSON Schema

    ```bash
    just update-schema
    ```

    This regenerates `schema.json` so that editors can provide autocomplete and validation for the new theme. See [JSON Schema](../json_schema.md) for details.

4. Done. Use it:

    ```bash
    rendercv new "John Doe" --theme mytheme
    ```

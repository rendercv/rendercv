# The YAML Input File

RenderCV uses a single YAML file to generate your CV. This file has four top-level fields:

```yaml title="Your_Name_CV.yaml"
cv:
  ...
  # Your content (name, sections, entries)
  ...
design:
  ...
  # Visual styling (theme, colors, fonts, spacing)
  ...
locale:
  ...
  # Language strings (month names, "present", etc.)
  ...
settings:
  ...
  # RenderCV behavior (current date, bold keywords)
  ...
```

Only `cv` is required. The others have sensible defaults.


Explore the detailed documentation for each field:

- [`cv` Field](cv.md)
- [`design` Field](design.md)
- [`locale` Field](locale.md)
- [`settings` Field](settings.md)

## JSON Schema

To maximize your productivity while editing the input YAML file, set up RenderCV's JSON Schema in your IDE. It will validate your inputs on the fly and give auto-complete suggestions.

![JSON Schema in action](../../assets/images/json_schema.gif)

=== "Visual Studio Code"

    1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
    2. Name your file ending with `_CV.yaml`. The schema activates automatically.
    3. Press `Ctrl + Space` for suggestions.

=== "Other Editors"

    1. Add this line at the top of your file:
        ```yaml
        # yaml-language-server: $schema=https://github.com/rendercv/rendercv/blob/main/schema.json?raw=true
        ```
    2. Press `Ctrl + Space` for suggestions (if your editor supports JSON Schema).

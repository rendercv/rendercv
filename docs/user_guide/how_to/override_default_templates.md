# Override Default Templates

When design options don't provide enough control, you can override the default Typst templates to fully customize your CV's appearance.

## When to Override Templates

Use template overriding when you need to:

- Change the fundamental layout structure
- Add custom Typst functions or packages
- Modify how entries are rendered beyond what `design.templates` allows
- Create completely custom designs not achievable through design options

For simpler customizations, try these first:

- [`design`](../yaml_input_structure.md#design) for colors, fonts, spacing
- [`design.templates`](arbitrary_keys_in_entries.md) for changing entry text layout

## Two Methods

### Method 1: Quick Template Customization

Use this when you want to tweak an existing theme's templates without creating a full custom theme.

1. Create templates alongside your CV:

    ```bash
    rendercv new "Your Name" --create-typst-templates
    ```

    This creates:
    ```
    Your_Name_CV.yaml
    classic/
      Preamble.j2.typ
      Header.j2.typ
      SectionBeginning.j2.typ
      entries/
        NormalEntry.j2.typ
        ...
    ```

2. Modify any template file in the `classic/` folder.

3. Render as usual:

    ```bash
    rendercv render Your_Name_CV.yaml
    ```

RenderCV automatically uses your local templates instead of the built-in ones.

### Method 2: Create a Custom Theme

Use this when building a reusable theme with its own design options.

1. Create a custom theme:

    ```bash
    rendercv create-theme mytheme
    ```

    This creates:
    ```
    mytheme/
      __init__.py
      Preamble.j2.typ
      Header.j2.typ
      SectionBeginning.j2.typ
      entries/
        NormalEntry.j2.typ
        ...
    ```

2. Modify template files and optionally add custom design options in `__init__.py`.

3. Use your theme in the YAML file:

    ```yaml
    design:
      theme: mytheme
      # Your custom design options work here
    ```

4. Render:

    ```bash
    rendercv render Your_Name_CV.yaml
    ```

## Template Structure

Templates use [Jinja2](https://jinja.palletsprojects.com/) syntax with Typst code:

```typst
// Example: entries/NormalEntry.j2.typ
#regular-entry(
  [
{% for line in entry.main_column.splitlines() %}
    {{ line }}
{% endfor %}
  ],
  [
{% for line in entry.date_and_location_column.splitlines() %}
    {{ line }}
{% endfor %}
  ],
)
```

### Variables Available in Templates

- `cv`: All CV data (name, sections, etc.)
- `design`: All design options
- `locale`: Locale strings (month names, translations)
- `entry`: Current entry data (in entry templates)

Example accessing design options:

```typst
// In Preamble.j2.typ
#show: rendercv.with(
  page-size: "{{ design.page.size }}",
  colors-body: {{ design.colors.body.as_rgb() }},
  typography-font-family-body: "{{ design.typography.font_family.body }}",
  // ...
)
```

## Markdown Templates

Both methods also support Markdown template customization with `--create-markdown-templates`. The process is identical to Typst templates.

## Tips

- Start by copying templates and making small changes
- Templates are Jinja2 + Typst, not pure Typst
- Delete template files you don't need to customize (RenderCV falls back to built-in versions)

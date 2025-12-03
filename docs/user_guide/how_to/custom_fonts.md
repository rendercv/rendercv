# Custom Fonts

RenderCV automatically discovers custom fonts placed in a `fonts` directory next to your YAML input file.

## How to Use Custom Fonts

1. Create a `fonts` directory in the same location as your YAML file:

    ```
    Your_Name_CV.yaml
    fonts/
      CustomFont-Regular.ttf
      CustomFont-Bold.ttf
      AnotherFont.otf
    ```

2. In your YAML file, specify the font family name in the design section:

    ```yaml
    design:
      typography:
        font_family: CustomFont
    ```

RenderCV passes the font family name directly to Typst, which searches for matching fonts in this order:

1. Custom fonts in your `fonts/` directory
2. System fonts
3. Embedded fonts (Libertinus Serif, New Computer Modern, DejaVu Sans Mono)

## Supported Font Formats

- `.ttf` (TrueType Font)
- `.otf` (OpenType Font)

## Font Family Names

Use the font family name exactly as defined in the font file's metadata. For most fonts, this is the name you see when you install the font on your system.

If you're unsure of the exact name:

- On macOS: Open the font file in Font Book to see the family name
- On Windows: Right-click the font file ’ Properties ’ Details ’ Title
- On Linux: Use `fc-query` command

## Font Fallback

You can specify multiple fonts as a fallback list. If the first font doesn't have a required glyph, Typst tries the next one:

```yaml
design:
  typography:
    font_family: [CustomFont, Noto Sans, Arial]
```

This is useful when your CV includes special characters or multiple languages.

## Checking Available Fonts

To see all fonts available to RenderCV (including your custom fonts), run:

```bash
typst fonts --font-path="fonts"
```

This shows the exact font family names you should use in your YAML configuration.

# Custom Fonts

RenderCV automatically discovers custom fonts placed in a `fonts` directory next to your YAML input file.

The `rendercv[full]` installation already includes the fonts in
[`rendercv-fonts`](https://github.com/rendercv/rendercv/tree/main/packages/rendercv-fonts),
including Font Awesome 7.3.1. These bundled fonts work offline; you only need a
local `fonts` directory for additional font families.

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

## Supported Font Formats

- `.ttf` (TrueType Font)
- `.otf` (OpenType Font)

## Font Family Names

Use the font family name exactly as defined in the font file's metadata. For most fonts, this is the name you see when you install the font on your system.

## Chinese, Japanese, and Korean

RenderCV ships Noto Sans fonts for Chinese, Japanese, and Korean, and Typst uses them for these characters when the selected font lacks them. The three languages draw some shared characters differently, so the font of the locale's language comes first. For other writing systems, Typst uses a font on your computer that has the characters, or one you put in the `fonts` folder.

Small capitals use the font's own small-capital letters, through [Typst's `smallcaps`](https://typst.app/docs/reference/text/smallcaps/), so choose a font that has them, such as Source Sans 3.

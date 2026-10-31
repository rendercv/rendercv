# Set Up Zed for RenderCV

[Zed supports YAML natively](https://zed.dev/docs/languages/yaml), using the same
YAML language server as VS Code’s YAML extension. It can suggest RenderCV
fields, explain them on hover, and flag invalid values as you type.

## Enable the schema

Open your CV’s folder in Zed. A file created by `rendercv new` already has a
schema comment at the top. Keep that comment: it selects the schema for the
RenderCV version that created the file. For an existing CV, add:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/v<< rendercv_version >>/schema.json
```

Use the version reported by `rendercv --version` in that URL. Type below a field
such as `design:` to see suggestions. Built-in theme names retain their named
choices; custom theme names are accepted too. The CLI still validates the actual
theme files, which an editor schema cannot inspect.

For offline editing, download the matching `schema.json` beside the CV and use
`# yaml-language-server: $schema=./schema.json` instead. Rendering itself does
not fetch the editor schema.

## Watch your edits

In Zed’s terminal, run:

```bash
rendercv render Your_Name_CV.yaml --watch
```

Open the PDF in a viewer that reloads changed files and arrange it beside Zed.
Saving the YAML regenerates the outputs. To save automatically after a short
pause, add this to your Zed project settings (`.zed/settings.json`):

```json
{
  "autosave": { "after_delay": { "milliseconds": 500 } }
}
```

If suggestions are missing, check that Zed identifies the file as YAML and
that its language server can read the schema URL or local file. If the PDF
does not update, check the watch command’s terminal output for validation errors.

# Set Up VS Code for RenderCV

Visual Studio Code can be configured to provide a live preview environment for writing your CV with RenderCV. This setup enables you to see your changes reflected in the PDF instantly as you type, making the CV editing process smooth and interactive.

## Required Extensions

Install these two VS Code extensions:

1. [**YAML Extension** by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml): Provides YAML language support with autocompletion and validation.

2. [**PDF Viewer** by tomoki1207](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf): Allows you to view PDF files directly within VS Code.

## Configure Auto-Save

To enable automatic rendering as you type, you need to configure VS Code to auto-save your files.

1. Open the VS Code settings JSON file:

    === "macOS"

        Press `Cmd+Shift+P` to open the Command Palette, then type:

        ```
        Preferences: Open User Settings (JSON)
        ```

    === "Windows/Linux"

        Press `Ctrl+Shift+P` to open the Command Palette, then type:

        ```
        Preferences: Open User Settings (JSON)
        ```

2. Add the following lines to your `settings.json` file:

    ```json
    {
        "files.autoSave": "afterDelay",
        "files.autoSaveDelay": 10
    }
    ```

These settings will automatically save your YAML file 10 milliseconds after you stop typing.

## Start Writing Your CV with Live Preview

Once the extensions are installed and auto-save is configured, follow these steps to start the live preview:

1. **Open your YAML input file** (e.g. `John_Doe_CV.yaml`) in VS Code

2. **Run `rendercv render` with the watch mode**:

    ```bash
    rendercv render --watch John_Doe_CV.yaml
    ```

    The `--watch` flag tells RenderCV to monitor the YAML file for changes and automatically re-render the PDF whenever the file is saved.

3. **Arrange your workspace**:

    - Place your YAML file on the left side of the editor
    - Open the generated PDF (from `rendercv_output/`) on the right side

4. **Start editing**: As you make changes to the YAML file, they will be automatically saved, triggering RenderCV to regenerate the PDF. The PDF viewer will update to show your changes in real-time.

![Live Preview Demonstration](../../assets/images/design_options.gif)

!!! tip
    You can split your editor vertically by right-clicking on the PDF file tab and selecting "Split Right" or using the keyboard shortcut `Cmd+\` (macOS) or `Ctrl+\` (Windows/Linux).

## Troubleshooting

If the live preview isn't working:

- Make sure auto-save is enabled and the delay is set
- Verify that `rendercv render --watch` is running in the terminal without errors
- Try closing and reopening the PDF file in VS Code

With this setup, you'll have a productive environment for creating and refining your CV with instant visual feedback.

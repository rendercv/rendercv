# Command Line Interface (CLI)

This page lists the available commands and options of the RenderCV CLI.

## `rendercv` command

- `#!bash --version` or `#!bash -v`

    Shows the version of RenderCV.

    ```bash
    rendercv --version
    ```

- `#!bash --help` or `#!bash -h`
    
    Shows the help message.

    ```bash
    rendercv --help
    ```

## `rendercv new` command

- `#!bash --theme "THEME_NAME"`

    Generates files for a specific built-in theme, instead of the default `classic` theme. Currently, the available themes are: {{available_themes}}.

    ```bash
    rendercv new "Full Name" --theme "THEME_NAME" 
    ```

- `#!bash --dont-create-theme-source-files` or `#!bash -notypst`

    Prevents the creation of the theme source files. By default, the theme source files are created.

    ```bash
    rendercv new "Full Name" --dont-create-theme-source-files
    ```

- `#!bash --dont-create-markdown-source-files` or `#!bash -nomd`

    Prevents the creation of the Markdown source files. By default, the Markdown source files are created.

    ```bash
    rendercv new "Full Name" --dont-create-markdown-source-files
    ```

- `#!bash --help` or `#!bash -h`

    Shows the help message.

    ```bash
    rendercv new --help
    ```


## `rendercv render` command

- `#!bash --watch` or `#!bash -w`

    Watches the input YAML file for changes and automatically renders if there is any change.

    ```bash
    rendercv render "Full_Name_CV.yaml" --watch
    ```

- `#!bash --output-folder-name "OUTPUT_FOLDER_NAME"` or `#!bash -o "OUTPUT_FOLDER_NAME"`

    Generates the output files in a folder with the given name. By default, the output folder name is `rendercv_output`. The output folder will be created in the current working directory.

    ```bash
    rendercv render "Full_Name_CV.yaml" --output-folder-name "OUTPUT_FOLDER_NAME"
    ```

- `#!bash --typst-path "PATH"` or `#!bash -typst "PATH"`

    Copies the generated Typst source code from the output folder and pastes it to the specified path.

    ```bash
    rendercv render "Full_Name_CV.yaml" --typst-path "PATH"
    ```

- `#!bash --pdf-path "PATH"` or `#!bash -pdf "PATH"`

    Copies the generated PDF file from the output folder and pastes it to the specified path.

    ```bash
    rendercv render "Full_Name_CV.yaml" --pdf-path "PATH"
    ```

- `#!bash --markdown-path "PATH"` or `#!bash -md "PATH"`

    Copies the generated Markdown file from the output folder and pastes it to the specified path.

    ```bash
    rendercv render "Full_Name_CV.yaml" --markdown-path "PATH"
    ```

- `#!bash --html-path "PATH"` or `#!bash -html "PATH"`

    Copies the generated HTML file from the output folder and pastes it to the specified path.

    ```bash
    rendercv render "Full_Name_CV.yaml" --html-path "PATH"
    ```

- `#!bash --png-path "PATH"` or `#!bash -png "PATH"`

    Copies the generated PNG files from the output folder and pastes them to the specified path.

    ```bash
    rendercv render "Full_Name_CV.yaml" --png-path "PATH"
    ```

- `#!bash --dont-generate-markdown` or `#!bash -nomd`

    Prevents the generation of the Markdown file.

    ```bash
    rendercv render "Full_Name_CV.yaml" --dont-generate-markdown
    ```

- `#!bash --dont-generate-html` or `#!bash -nohtml`

    Prevents the generation of the HTML file.

    ```bash
    rendercv render "Full_Name_CV.yaml" --dont-generate-html
    ```

- `#!bash --dont-generate-png` or `#!bash -nopng`

    Prevents the generation of the PNG files.

    ```bash
    rendercv render "Full_Name_CV.yaml" --dont-generate-png
    ```
- `#!bash --design design.yaml`
   
    Uses the given design file for the `design` field of the input YAML file.

    ```bash
    rendercv render "Full_Name_CV.yaml" --design "design.yaml"
    ```

- `#!bash --locale-catalog locale.yaml`
   
    Uses the given locale catalog file for the `locale` field of the input YAML file.

    ```bash
    rendercv render "Full_Name_CV.yaml" --locale-catalog "locale.yaml"
    ```

- `#!bash --rendercv-settings rendercv_settings.yaml`
   
    Uses the given RenderCV settings file for the `rendercv_settings` field of the input YAML file.

    ```bash
    rendercv render "Full_Name_CV.yaml" --rendercv-settings "rendercv_settings.yaml"
    ```

- `#!bash --ANY.LOCATION.IN.THE.YAML.FILE "VALUE"`

    Overrides the value of `ANY.LOCATION.IN.THE.YAML.FILE` with `VALUE`. This option can be used to avoid storing sensitive information in the YAML file. Sensitive information, like phone numbers, can be passed as a command-line argument with environment variables. This method is also beneficial for creating multiple CVs using the same YAML file by changing only a few values. Here are a few examples:

    ```bash
    rendercv render "Full_Name_CV.yaml" --cv.phone "+905555555555"
    ```

    ```bash
    rendercv render "Full_Name_CV.yaml" --cv.sections.education.1.institution "Your University"
    ```

    Multiple `#!bash --ANY.LOCATION.IN.THE.YAML.FILE "VALUE"` options can be used in the same command.

- `#!bash --help` or `#!bash -h`

    Shows the help message.

    ```bash
    rendercv render --help
    ```

## `rendercv create-theme` command

- `#!bash --based-on "THEME_NAME"`

    Generates a custom theme based on the specified built-in theme, instead of the default `classic` theme. Currently, the available themes are: {{available_themes}}. 
    
    ```bash
    rendercv create-theme "mycustomtheme" --based-on "THEME_NAME"
    ```

- `#!bash --help` or `#!bash -h`

    Shows the help message.

    ```bash
    rendercv create-theme --help
    ```

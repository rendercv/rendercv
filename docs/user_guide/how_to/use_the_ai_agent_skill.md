# Use the AI Agent Skill

RenderCV provides an AI agent skill that teaches AI coding assistants how to create, edit, and render CVs. Once installed, your agent gains full knowledge of RenderCV's YAML schema, CLI commands, themes, locales, and design options.

## Supported Agents

The skill works with any AI coding agent that supports the skills protocol, including:

- Claude Code
- Cursor
- Codex
- Copilot
- Windsurf
- Gemini CLI
- and 20+ others

## Install the Skill

=== "Vercel Skills CLI"

    ```bash
    npx skills add rendercv/rendercv
    ```

    You can also target a specific agent:

    ```bash
    npx skills add rendercv/rendercv -a claude-code
    npx skills add rendercv/rendercv -a cursor
    npx skills add rendercv/rendercv -a codex
    ```

=== "OpenSkills"

    ```bash
    npx openskills install rendercv/rendercv
    ```

=== "Manual"

    Copy the content of [`skills/rendercv/SKILL.md`](https://github.com/rendercv/rendercv/blob/main/skills/rendercv/SKILL.md) into your agent's skill directory. For example, for Claude Code:

    ```bash
    git clone https://github.com/rendercv/rendercv.git
    cp -r rendercv/skills/rendercv ~/.claude/skills/
    ```

## What the Skill Provides

The skill gives your AI agent:

- Full knowledge of RenderCV's YAML input structure
- All 6 built-in themes and their design options
- Complete locale and language support (20 built-in languages)
- CLI commands and their options
- Pydantic model schemas for precise field types and defaults
- A complete sample CV as a reference

## Usage

After installing the skill, simply ask your AI agent to work with your CV:

- "Create a new CV for me using the classic theme"
- "Switch my CV to the engineeringresumes theme"
- "Add a new experience entry to my CV"
- "Change the font to Source Sans 3 and make the margins smaller"
- "Translate my CV to German"

The agent will use its knowledge from the skill to produce correct YAML and run the right `rendercv` commands.

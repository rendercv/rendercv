# RenderCV development

Read the shared contributor documentation before changing code:

- [Setup](docs/developer_guide/index.md)
- [Architecture](docs/developer_guide/understanding_rendercv.md)
- [Contributing and code conventions](docs/developer_guide/contributing.md)
- [Testing](docs/developer_guide/testing.md)

Use `uv` for Python commands. Run `just format` and `just check` before committing,
and run tests appropriate to the change. Keep input validation in `schema/`;
unexpected failures after validation must propagate as bugs.

The developer guide also covers themes, locales, social networks, documentation,
release workflows, and publishing the Typst package. Keep contributor guidance
there so it applies equally to humans and coding agents.

Write developer documentation for readers who have never heard of the topic and may
not be technical: give them an intuitive and technically accurate picture of what
each thing is, why we need it, and how RenderCV uses it, in as few words as that
takes. See [Writing documentation](docs/developer_guide/contributing.md#writing-documentation).

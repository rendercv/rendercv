# Arbitrary Keys in Entries

The `design.templates` field controls how entry data is displayed. Add any custom field to your entries and reference it in templates using UPPERCASE placeholders.

## How It Works

Templates use **UPPERCASE PLACEHOLDERS** that map to entry keys.

Given this entry:

```yaml
company: Google
position: Software Engineer
tech_stack: Python, Go, Kubernetes
```

And this template:

```yaml
design:
  templates:
    experience_entry:
      main_column: |-
        **COMPANY**, POSITION
        *Tech stack:* TECH_STACK
```

RenderCV replaces `COMPANY` → "Google", `POSITION` → "Software Engineer", `TECH_STACK` → "Python, Go, Kubernetes".

Any key you add to an entry becomes available as an uppercase placeholder.

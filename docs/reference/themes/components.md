# `rendercv.themes.components`

## Jinja Templates

{% for template_name, template in theme_components.items() %}

### {{ template_name }}

```typst
{{ template }}
```

{% endfor %}
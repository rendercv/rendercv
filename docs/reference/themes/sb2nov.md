#  `rendercv.themes.sb2nov`

::: rendercv.themes.sb2nov

## Jinja Templates

{% for template_name, template in theme_templates["sb2nov"].items() %}
### {{ template_name }}

```typst
{{ template }}
```

{% endfor %}

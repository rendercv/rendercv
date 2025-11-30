## {{ entry.main_column.splitlines()[0] }}
{%- if design.templates.education_entry.degree_column %}


{{ entry.degree_column }}

{% endif -%}
{% for line in entry.date_and_location_column.splitlines() %}
{{ line }}

{% endfor %}
{% for line in entry.main_column.splitlines()[1:] %}
{%- if line != "!!! note" -%}{{ line|replace("    ", "") }}

{% endif -%}
{% endfor %}

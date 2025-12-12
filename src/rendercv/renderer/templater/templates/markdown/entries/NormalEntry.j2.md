## {{ entry.main_column.splitlines()[0] }}

{% for line in entry.date_and_location_column.splitlines() %}
{{ line }}

{% endfor %}
{% for line in entry.main_column.splitlines()[1:] %}
{%- if line != "!!! summary" -%}{{ line|replace("    ", "") }}

{% endif -%}
{% endfor %}

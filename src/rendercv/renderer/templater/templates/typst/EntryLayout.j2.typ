{% macro main_column(entry, limit) %}
{% set lines = entry.main_column.splitlines() %}
{% set heading_lines = entry._main_column_heading_lines %}
{% if heading_lines %}
#entry-heading[
{% for line in lines[:heading_lines] %}
  {{ line|indent(2) }}

{% endfor %}
]
{% endif %}
{% for line in lines[heading_lines:limit] %}
{{ line }}

{% endfor %}
{% endmacro %}

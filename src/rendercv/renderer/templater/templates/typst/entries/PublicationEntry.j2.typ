{% from entry_layout import main_column %}
{% if not design.entries.short_second_row %}
{% set first_row_lines = entry.date_and_location_column.splitlines()|length %}
{% set first_row_lines = [first_row_lines, entry._main_column_heading_lines, 1]|max %}
{% else %}
{% set first_row_lines = entry.main_column.splitlines()|length %}
{% endif %}
#regular-entry(
  [
{{ main_column(entry, first_row_lines)|trim|indent(4, first=true) }}
  ],
  [
{% for line in entry.date_and_location_column.splitlines() %}
{{ line|indent(4, first=true) if line else "" }}

{% endfor %}
  ],
{% if not design.entries.short_second_row %}
  main-column-second-row: [
{% for line in entry.main_column.splitlines()[first_row_lines:] %}
{{ line|indent(4, first=true) if line else "" }}

{% endfor %}
  ],
{% endif %}
)

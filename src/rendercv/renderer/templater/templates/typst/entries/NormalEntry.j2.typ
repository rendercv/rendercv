{% if design.entries.short_second_row %}
{% set first_row_lines = 1 %}
{% else %}
{% set first_row_lines = entry.main_column_template.splitlines()|length %}
{% endif %}
#regular-entry(
  [
{% for line in entry.main_column_template.splitlines()[:first_row_lines] %}
    {{ line|indent(4) }}
    
{% endfor %}
  ],
  [
    {{ entry.date_and_location_column_template|indent(4) }}
  ],
{% if design.entries.short_second_row %}
  main-column-second-row: [
{% for line in entry.main_column_template.splitlines()[first_row_lines:] %}
    {{ line|indent(4) }}
    
{% endfor %}
  ],
{% endif %}
)

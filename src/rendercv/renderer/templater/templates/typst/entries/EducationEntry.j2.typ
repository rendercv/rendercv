#education-entry(
  [
    {{ entry.main_column_template|indent(4) }}
  ],
  [
    {{ entry.date_and_location_column_template|indent(4) }}
  ],
{% if entry.degree_column_template %}
  degree-column: [
    {{ entry.degree_column_template|indent(4) }}
  ],
{% endif %}
)

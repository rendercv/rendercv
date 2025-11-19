#education-entry(
  [
    {{ entry.main_column_template }}
  ],
  [
    {{ entry.date_and_location_column_template }}
  ],
{% if entry.degree_column_template %}
  degree-column: [
    {{ entry.degree_column_template }}
  ],
{% endif %}
)

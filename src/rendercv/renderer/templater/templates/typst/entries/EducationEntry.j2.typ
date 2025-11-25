#education-entry(
  [
{% for line in entry.main_column_template.splitlines() %}
    {{ line|indent(4) }}
    
{% endfor %}
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

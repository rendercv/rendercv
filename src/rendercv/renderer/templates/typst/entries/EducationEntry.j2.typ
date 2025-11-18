{% if date_and_location_column_template and design.entry_types.education_entry.degree_column_template %}
// YES DATE, YES DEGREE
#three-col-entry(
  left-column-width: {{design.entry_types.education_entry.degree_column_width}},
  left-content: [{{degree_column_template}}],
  middle-content: [
    {{main_column_first_row_template}}
    {% if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" %}
    {% if main_column_second_row_template %}
    #v(-design-text-leading)
    {% endif %}

    {{main_column_second_row_template|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")}}
    {% endif %}
  ],
  right-content: [
    {{date_and_location_column_template}}
  ],
)
{% if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n")) and main_column_second_row_template %}
#block(
  [
    #set par(spacing: 0pt)
    {{main_column_second_row_template}}
  ],
  inset: (
    left: design-entry-types-education-entry-degree-column-width + design-entries-horizontal-space-between-columns + design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
)
{% endif %}
{% elif date_and_location_column_template and not design.entry_types.education_entry.degree_column_template %}
// YES DATE, NO DEGREE
#two-col-entry(
  left-content: [
    {{main_column_first_row_template}}
    {% if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" %}
    {% if main_column_second_row_template %}
    #v(-design-text-leading)
    {% endif %}

    {{main_column_second_row_template|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")}}
    {% endif %}
  ],
  right-content: [
    {{date_and_location_column_template}}
  ],
)
  {% if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv") %}
#block(
  [
    #set par(spacing: 0pt)
    {{main_column_second_row_template}}
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
)
{% endif %}
{% elif not date_and_location_column_template and design.entry_types.education_entry.degree_column_template %}
// NO DATE, YES DEGREE
#two-col-entry(
  left-column-width: {{design.entry_types.education_entry.degree_column_width}},
  right-column-width: 1fr,
  alignments: (left, left),
  left-content: [
    {{degree_column_template}}
  ],
  right-content: [
    {{main_column_first_row_template}}
    {% if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" %}
    {% if main_column_second_row_template %}
    #v(-design-text-leading)
    {% endif %}
  
    {{main_column_second_row_template|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")}}
    {% endif %}
  ],
)
{% if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n")) and main_column_second_row_template %}
#block(
  [
    #set par(spacing: 0pt)
    {{main_column_second_row_template}}
  ],
  inset: (
    left: design-entry-types-education-entry-degree-column-width + design-entries-horizontal-space-between-columns + design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
)
{% endif %}
{% else %}
// NO DATE, NO DEGREE

#one-col-entry(
  content: [
    {{main_column_first_row_template}}

    {% if main_column_second_row_template %}
    #v(-design-text-leading)
    {% endif %}
    {{main_column_second_row_template|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")}}
  ],
)
{% endif %}
{% if date_and_location_column_template %}
#two-col-entry(
  left-content: [
    {{main_column_first_row_template}}

  {% if design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv" %}
  #v(-design-text-leading)
    {% if not (entry.doi or entry.url)%}
  {{main_column_second_row_without_url_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- elif not entry.journal -%}
  {{main_column_second_row_without_journal_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- else -%}
  {{main_column_second_row_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- endif -%}
  {% endif %}
  ],
  right-content: [
    {{date_and_location_column_template}}
  ],
)
  {% if not (design.entries.short_second_row or date_and_location_column_template.count("\n\n") > main_column_first_row_template.count("\n\n") or design.section_titles.type=="moderncv") %}
#one-col-entry(content:[
    {% if not (entry.doi or entry.url)%}
  {{main_column_second_row_without_url_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- elif not entry.journal -%}
  {{main_column_second_row_without_journal_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- else -%}
  {{main_column_second_row_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- endif -%}
])
  {% endif %}
{% else %}
#one-col-entry(content:[
  {{main_column_first_row_template}}

  #v(-design-text-leading)
    {% if not (entry.doi or entry.url)%}
  {{main_column_second_row_without_url_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- elif not entry.journal -%}
  {{main_column_second_row_without_journal_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- else -%}
  {{main_column_second_row_template|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")}}
    {%- endif -%}
])
{% endif %}
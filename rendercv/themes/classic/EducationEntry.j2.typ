#block(
  [
    ((* if second_column_template and design.entry_types.education_entry.degree_column_template *))
    // YES DATE, YES DEGREE
    #three-col-entry(
      left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
      left-content: [<<degree_column_template>>],
      middle-content: [
        <<first_column_first_row_template>>
        ((* if design.entries.short_second_row or "\n\n" in second_column_template *))

        <<first_column_second_row_template>>
        ((* endif *))
      ],
      right-content: [
        <<second_column_template>>
      ],
    )
    ((* if not (design.entries.short_second_row or "\n\n" in second_column_template) and first_column_second_row_template *))
    #block(
      [
        <<first_column_second_row_template>>
      ],
      inset: (
        left: <<design.entry_types.education_entry.degree_column_width>> + <<design.entries.horizontal_space_between_columns>>,
      ),
    )
    ((* endif *))
    ((* elif second_column_template and not design.entry_types.education_entry.degree_column_template *))
    // YES DATE, NO DEGREE
    #two-col-entry(
      left-content: [
        <<first_column_first_row_template>>
        ((* if design.entries.short_second_row or "\n\n" in second_column_template *))

        <<first_column_second_row_template>>
        ((* endif *))
      ],
      right-content: [
        <<second_column_template>>
      ],
    )
    ((* if not (design.entries.short_second_row or "\n\n" in second_column_template) *))
    <<first_column_second_row_template>>
    ((* endif *))
    ((* elif not second_column_template and design.entry_types.education_entry.degree_column_template *))
    // NO DATE, YES DEGREE
    #two-col-entry(
      left-column-width: <<design.entry_types.education_entry.degree_column_width>>,
      right-column-width: 1fr,
      alignments: (left, left),
      left-content: [
        <<degree_column_template>>
      ],
      right-content: [
        <<first_column_first_row_template>>
        ((* if design.entries.short_second_row or "\n\n" in second_column_template *))

        <<first_column_second_row_template>>
        ((* endif *))
      ],
    )
    ((* if not (design.entries.short_second_row or "\n\n" in second_column_template) and first_column_second_row_template *))
    #block(
      [
        <<first_column_second_row_template>>
      ],
      inset: (
        left: <<design.entry_types.education_entry.degree_column_width>> + <<design.entries.horizontal_space_between_columns>>,
      ),
    )
    ((* endif *))
    ((* else *))
    // NO DATE, NO DEGREE

    <<first_column_first_row_template>>

    <<first_column_second_row_template>>
    ((* endif *))
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)

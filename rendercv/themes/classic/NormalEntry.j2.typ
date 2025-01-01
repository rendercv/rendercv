#block(
  [
    ((* if second_column_template *))
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
    ((* else *))

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

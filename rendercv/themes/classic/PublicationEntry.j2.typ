#block(
  [
    #set par(spacing: design-highlights-vertical-space-between-highlights)
  ((* if second_column_template *))
    #two-col-entry(
      left-content: [
        #set par(spacing: design-highlights-vertical-space-between-highlights)
        <<first_column_first_row_template>>

      ((* if design.entries.short_second_row or "\n\n" in second_column_template *))
        ((* if not (entry.doi or entry.url)*))
      <<first_column_second_row_without_url_template>>
        ((*- elif not entry.journal -*))
      <<first_column_second_row_without_journal_template>>
        ((*- else -*))
      <<first_column_second_row_template>>
        ((*- endif -*))
      ((* endif *))
      ],
      right-content: [
        <<second_column_template>>
      ],
    )
    ((* if not (design.entries.short_second_row or "\n\n" in second_column_template) *))
        ((* if not (entry.doi or entry.url)*))
      <<first_column_second_row_without_url_template>>
        ((*- elif not entry.journal -*))
      <<first_column_second_row_without_journal_template>>
        ((*- else -*))
      <<first_column_second_row_template>>
        ((*- endif -*))
    ((* endif *))
  ((* else *))

    <<first_column_first_row_template>>

    ((* if not (entry.doi or entry.url)*))
    <<first_column_second_row_without_url_template>>
    ((*- elif not entry.journal -*))
    <<first_column_second_row_without_journal_template>>
    ((*- else -*))
    <<first_column_second_row_template>>
    ((*- endif -*))
  ((* endif *))
  ],
  inset: (
    left: design-entries-left-and-right-margin,
    right: design-entries-left-and-right-margin,
  ),
  breakable: design-entries-allow-page-break-in-entries,
  width: 100%,
)
((* set first_row_split = first_row_template|split_and_trim *))
((* if not (entry.doi or entry.url) *))
    ((* set second_row_split = second_row_no_url_template|split_and_trim *))
((* elif not entry.journal *))
    ((* set second_row_split = second_row_no_journal_template|split_and_trim *))
((* else *))
    ((* set second_row_split = second_row_template|split_and_trim *))
((* endif *))

((* if first_row_split|length == 3 *))
#three-col-entry(
  left-column-width: <<design.entry_types.education_entry.first_column_width>>,
  left-content: [<< first_row_split[0] >>],
  middle-content: [
    << first_row_split[1] >>
    ((* if design.entries.short_second_row
          or first_row_split[2].count("\n\n") > first_row_split[1].count("\n\n")
          or design.section_titles.type == "moderncv" *))
      ((* if second_row_split *))
            #v(-design-text-leading)
            ((* if second_row_split|length > 1 *))
            << second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
            ((*- else -*))
            << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
            ((*- endif -*))
      ((*- endif -*))
    ((*- endif -*))
  ],
  right-content: [
    << first_row_split[2] >>
  ],
)
((* elif first_row_split|length == 2 *))
#two-col-entry(
  left-content: [
    << first_row_split[0] >>
    ((* if design.entries.short_second_row
          or first_row_split[1].count("\n\n") > first_row_split[0].count("\n\n")
          or design.section_titles.type == "moderncv" *))
      ((* if second_row_split *))
        #v(-design-text-leading)
        << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
      ((*- endif -*))
    ((*- endif -*))
  ],
  right-content: [
    << first_row_split[1] >>
  ],
)
((* else *))
    #one-col-entry(content: [<< first_row_split[0] >>])
((* endif *))

((* if not (
    (first_row_split|length in [2, 3])
    and (
      design.entries.short_second_row
      or first_row_split[-1].count("\n\n") > first_row_split[-2].count("\n\n")
      or design.section_titles.type == "moderncv"
    )
    and second_row_template
  ) *))
  #v(design-highlights-top-margin)
  ((* if second_row_split|length == 3 *))
  #three-col-entry(
      left-column-width: <<design.entry_types.education_entry.first_column_width>>,
      left-content: [<< second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>],
      middle-content: [<< second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>],
      right-content: [<< second_row_split[2]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>],
  )
  ((* elif second_row_split|length == 2 *))
  #two-col-entry(
    left-content: [<< second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>],
    right-content: [<< second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>]
  )
  ((* else *))
  #one-col-entry(content: [<< second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>])
  ((* endif *))
((* endif *))

((* set first_row_split = first_row_template|split_and_trim *))
((* set second_row_split = second_row_template|split_and_trim *))

((* if first_row_split|length == 3 *))
#three-col-entry(
  left-column-width: <<design.entry_types.education_entry.first_column_width>>,
  left-content: [ <<first_row_split[0] >>],
  middle-content: [
    <<first_row_split[1]>>
    ((* if design.entries.short_second_row
          or first_row_split[2].count("\n\n") > first_row_split[1].count("\n\n")
          or design.section_titles.type == "moderncv" *))
      ((* if second_row_template *))
        #v(-design-text-leading)
        ((* if second_row_split|length > 1 *))
        << second_row_split[1]|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")>>
        ((* else *))
        << second_row_split[0]|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n")>>
        ((* endif *))
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
      ((* if second_row_template *))
        #v(-design-text-leading)
        << second_row_split[0]|replace("\n\n", "\n\n#v(-design-text-leading)")|replace("!!LINEBREAK!!", "\n\n") >>
      ((* endif *))
    ((* endif *))
  ],
  right-content: [
    << first_row_split[1] >>
  ],
)
((* else *))
#one-col-entry(content: [<<first_row_template>>])
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
    ((* if second_row_split|length == 3 *))
    #three-col-entry(
      left-column-width: <<design.entry_types.education_entry.first_column_width>>,
      left-content: [ << second_row_split[0] >>],
      middle-content: [<< second_row_split[1] >>],
      right-content: [<< second_row_split[2] >>],
    )
    ((* elif second_row_split|length == 2 *))
    #two-col-entry(
      left-content: [<< second_row_split[0] >>],
      right-content: [<< second_row_split[1] >>],
    )
    ((* else *))
    #one-col-entry(content: [<<second_row_template|replace("\n\n", "\n\n#v(-design-text-leading)")>>])
    ((* endif *))


((* endif *))
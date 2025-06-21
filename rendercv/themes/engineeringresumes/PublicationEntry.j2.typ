((* set first_row_split = first_row_template|split_and_trim *))
((* set second_row_split = second_row_template|split_and_trim *))
((* set third_row_split = third_row_template|split_and_trim *))

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
            ((* if entry.journal or entry.doi or entry.url *))
                ((* if second_row_split|length > 1 *))
                << second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
                ((*- else -*))
                << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
                ((*- endif -*))
            ((*- endif -*))
            ((* if entry.conference or entry.conference_url *))
                ((* if third_row_split|length > 1 *))
                << third_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
                ((*- else -*))
                << third_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)")>>
                ((*- endif -*))
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
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
        ((* if entry.conference or entry.conference_url *))
        << third_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
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
      left-content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
    ],
      middle-content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
      ],
      right-content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[2]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[2]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
      ],
  )
  ((* elif second_row_split|length == 2 *))
  #two-col-entry(
    left-content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
    ],
    right-content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[1]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
    ]
  )
  ((* else *))
  #one-col-entry(content: [
        ((* if entry.journal or entry.doi or entry.url *))
        << second_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((* endif *))
        ((* if entry.conference or entry.conference_url *))
        #v(design-highlights-top-margin - design-text-leading);
        << third_row_split[0]|replace("\n\n", "\n\n#v(design-highlights-top-margin - design-text-leading)") >>
        ((*- endif -*))
  ])
  ((* endif *))
((* endif *))

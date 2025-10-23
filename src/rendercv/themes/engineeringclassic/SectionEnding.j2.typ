((* if entry_type in ["NumberedEntry", "ReversedNumberedEntry"] *))
  ((* if entry_type == "ReversedNumberedEntry" *))
  )
  #enum(
    numbering: n => [#{rev-enum-items.len() + 1 - n}.],
    ..rev-enum-items,
  )
  ((* endif *))
  ],
)
((* endif *))
((* if not design.entries.allow_page_break_in_sections *))
  ],
  breakable: false,
  inset: (
    left: 0cm,
    right: 0cm,
  ),
  width: 100%,
)
((* endif *))
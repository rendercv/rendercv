<<preamble>>

<<header>>

((* for section_beginning, entries, section_ending in sections *))
<<section_beginning>>

    ((* for entry in entries *))
<<entry>>
      ((* if not loop.last *))
#v(design-entries-vertical-space-between-entries)
      ((* endif *))
    ((* endfor *))

<<section_ending>>
((* endfor *))

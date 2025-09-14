<<preamble>>

<<header>>

((* for section_beginning, entries, section_ending, entry_type, vertical_space_between_entries in sections *))
<<section_beginning>>

    ((* for entry in entries *))
<<entry>>
      ((* if not loop.last and entry_type not in ["NumberedEntry", "ReversedNumberedEntry"] *))
#v(<<vertical_space_between_entries>>)
      ((* endif *))
    ((* endfor *))

<<section_ending>>
((* endfor *))

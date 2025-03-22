((* for item in entry.highlights *))
  ((* if loop.first *))
  #v(design-highlights-top-margin);#highlights(
  ((*- endif -*))
    [<<item|replace("\n", "!!LINEBREAK!!")>>], 
  ((*- if loop.last -*))
  )
  ((* endif *))
((* endfor *))
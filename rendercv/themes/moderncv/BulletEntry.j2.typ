((* for item in entry.bullets *))
  ((* if loop.first *))
  #bullet-entry(
  ((*- endif -*))
    [<<item|replace("\n", "!!LINEBREAK!!")>>], 
  ((*- if loop.last -*))
  )
  ((* endif *))
((* endfor *))
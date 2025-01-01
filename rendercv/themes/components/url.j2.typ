((*- if entry.doi -*))
#link("<<entry.doi_url>>")[<<entry.doi>>]
((*- elif entry.url -*))
#link("<<entry.url>>")[<<entry.clean_url>>]
((*- endif -*))
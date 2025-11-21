// Import the rendercv function and all the refactored components
#import "lib.typ": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  entries-left-and-right-margin: 0.3cm,
  text-leading: 0.8em,
  entries-vertical-space-between-entries: 2cm,
  section-titles-vertical-space-below: 0cm,
  section-titles-vertical-space-above: 0cm,
  entries-horizontal-space-between-columns: 0.3cm,
  header-vertical-space-between-connections-and-first-section: 1cm,
  header-vertical-space-between-name-and-connections: 0.4cm,
  section-titles-type: "moderncv",
  header-separator-between-connections: "|",
  page-left-margin: 2cm,
  page-right-margin: 2cm,
)

= John Doe

#connections(
  [Location],
  [#link("mailto:john.doe@example.com", icon: false)[john.doe\@example.com]],
  [#link("tel:+1-609-999-9995", icon: false)[(609) 999-9995]],
  [#link("https://linkedin.com/in/john.doe", icon: false)[john.doe]],
  [#link("https://github.com/john.doe", icon: false)[john.doe]],
)

== Projects

#regular-entry(
  [
    #strong[#link("https://example.com")[Example Project]]
    
    A web application for writing essays
    
    - Launched an #link("https://example.com")[iOS app] in 09\/2024 that currently has 10k+ monthly active users
    
    - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub])
    
      - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub]) with #link("https://github.com")[on GitHub]
    
      - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub]) with #link("https://github.com")[on GitHub]
    
      - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub]) with #link("https://github.com")[on GitHub]
    
  ],
  [
    
  ],
)

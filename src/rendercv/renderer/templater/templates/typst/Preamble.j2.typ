// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.0.1": *

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

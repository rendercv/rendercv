// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.3.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "Jane Doe",
  title: "Jane Doe - CV",
  footer: context { [#emph[Jane Doe -- #str(here().page())\/#str(counter(page).final().first())]] },
  top-note: [ #emph[Last updated in Nov 2025] ],
  locale-catalog-language: "en",
  text-direction: ltr,
  page-size: "us-letter",
  page-top-margin: 0.6in,
  page-bottom-margin: 0.6in,
  page-left-margin: 0.6in,
  page-right-margin: 0.6in,
  page-show-footer: true,
  page-show-top-note: true,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(42, 24, 82),
  colors-headline: rgb(42, 24, 82),
  colors-connections: rgb(70, 50, 110),
  colors-section-titles: rgb(42, 24, 82),
  colors-links: rgb(42, 24, 82),
  colors-footer: rgb(120, 100, 140),
  colors-top-note: rgb(120, 100, 140),
  typography-line-spacing: 0.55em,
  typography-alignment: "justified",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "EB Garamond",
  typography-font-family-name: "EB Garamond",
  typography-font-family-headline: "EB Garamond",
  typography-font-family-connections: "EB Garamond",
  typography-font-family-section-titles: "EB Garamond",
  typography-font-size-body: 10pt,
  typography-font-size-name: 32pt,
  typography-font-size-headline: 11pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.4em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: true,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: true,
  links-underline: true,
  links-show-external-link-icon: false,
  header-alignment: left,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.5cm,
  header-space-below-headline: 0.4cm,
  header-space-below-connections: 0.5cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: false,
  header-connections-display-urls-instead-of-usernames: true,
  header-connections-separator: "|",
  header-connections-space-between-connections: 0.4cm,
  section-titles-type: "without_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.5cm,
  section-titles-space-below: 0.2cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.2em,
  sections-space-between-regular-entries: 1em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0cm,
  entries-space-between-columns: 0.2cm,
  entries-allow-page-break: false,
  entries-short-second-row: false,
  entries-degree-width: 1cm,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.06cm,
  entries-highlights-bullet:  "•" ,
  entries-highlights-nested-bullet:  "•" ,
  entries-highlights-space-left: 0cm,
  entries-highlights-space-above: 0.06cm,
  entries-highlights-space-between-items: 0.06cm,
  entries-highlights-space-between-bullet-and-text: 0.4em,
  date: datetime(
    year: 2025,
    month: 11,
    day: 30,
  ),
)


= Jane Doe

  #headline([Research Scientist])

#connections(
)


== Selected Work

#text(weight: "bold")[Career Highlights]


Built a research platform that supports **mixed subsection entry types**.

#text(weight: "bold")[Featured Projects]


#regular-entry(
  [
    #strong[Subsection Support]

  ],
  [
    Feb 2024

  ],
  main-column-second-row: [
    #summary[Implemented subsection-based sections across schema, rendering, and docs.]

  ],
)

#text(weight: "bold")[Recent Milestones]


#reversed-numbered-entries(
  [

+ Rolled out subsection rendering

+ Added schema and snapshot coverage
  ],
)

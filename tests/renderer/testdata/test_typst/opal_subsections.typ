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
  page-top-margin: 0.65in,
  page-bottom-margin: 0.65in,
  page-left-margin: 0.65in,
  page-right-margin: 0.65in,
  page-show-footer: false,
  page-show-top-note: false,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(0, 100, 90),
  colors-headline: rgb(0, 80, 72),
  colors-connections: rgb(0, 80, 72),
  colors-section-titles: rgb(0, 100, 90),
  colors-links: rgb(0, 100, 90),
  colors-footer: rgb(100, 140, 135),
  colors-top-note: rgb(100, 140, 135),
  typography-line-spacing: 0.6em,
  typography-alignment: "left",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "Lato",
  typography-font-family-name: "Lato",
  typography-font-family-headline: "Lato",
  typography-font-family-connections: "Lato",
  typography-font-family-section-titles: "Lato",
  typography-font-size-body: 10pt,
  typography-font-size-name: 26pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 9pt,
  typography-font-size-section-titles: 1.2em,
  typography-small-caps-name: false,
  typography-small-caps-headline: true,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: true,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: false,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.3cm,
  header-space-below-headline: 0.3cm,
  header-space-below-connections: 0.6cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: true,
  header-connections-display-urls-instead-of-usernames: false,
  header-connections-separator: "•",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "centered_without_line",
  section-titles-line-thickness: 0.4pt,
  section-titles-space-above: 0.55cm,
  section-titles-space-below: 0.25cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.3em,
  sections-space-between-regular-entries: 1.1em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.15cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: false,
  entries-short-second-row: true,
  entries-degree-width: 1cm,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.04cm,
  entries-highlights-bullet:  "◦" ,
  entries-highlights-nested-bullet:  "◦" ,
  entries-highlights-space-left: 0.15cm,
  entries-highlights-space-above: 0.04cm,
  entries-highlights-space-between-items: 0.04cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
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

    #summary[Implemented subsection-based sections across schema, rendering, and docs.]

  ],
  [
    Feb 2024

  ],
)

#text(weight: "bold")[Recent Milestones]


#reversed-numbered-entries(
  [

+ Rolled out subsection rendering

+ Added schema and snapshot coverage
  ],
)

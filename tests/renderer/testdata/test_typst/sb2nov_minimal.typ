// Import the rendercv function and all the refactored components
#import "lib.typ": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  footer-text: "Page 1 of 1",
  last-updated-date-text: "Last updated in Nov 2025",
  locale-catalog-language: "en",
  page-size: "us-letter",
  page-top-margin: 2cm,
  page-bottom-margin: 2cm,
  page-left-margin: 2cm,
  page-right-margin: 2cm,
  page-show-page-numbering: true,
  page-show-last-updated-date: true,
  colors-text: rgb(0, 0, 0),
  colors-name: rgb(0, 0, 0),
  colors-connections: rgb(0, 0, 0),
  colors-section-titles: rgb(0, 0, 0),
  colors-links: rgb(0, 79, 144),
  colors-last-updated-date-and-page-numbering: rgb(128, 128, 128),
  text-font-family: "New Computer Modern",
  text-font-size: 10pt,
  text-leading: 0.6em,
  text-alignment: "justified",
  text-date-and-location-column-alignment: right,
  links-underline: true,
  links-use-external-link-icon: false,
  header-name-font-family: "New Computer Modern",
  header-name-font-size: 30pt,
  header-name-bold: true,
  header-small-caps-for-name: false,
  header-photo-width: 3.5cm,
  header-connections-font-family: "New Computer Modern",
  header-vertical-space-between-name-and-connections: 0.7cm,
  header-vertical-space-between-connections-and-first-section: 0.7cm,
  header-horizontal-space-between-connections: 0.5cm,
  header-separator-between-connections: "",
  header-alignment: center,
  section-titles-type: "with-full-line",
  section-titles-font-family: "New Computer Modern",
  section-titles-font-size: 1.4em,
  section-titles-bold: true,
  section-titles-small-caps: false,
  section-titles-line-thickness: 0.5pt,
  section-titles-vertical-space-above: 0.5cm,
  section-titles-vertical-space-below: 0.3cm,
  entries-date-and-location-width: 4.15cm,
  entries-left-and-right-margin: 0.2cm,
  entries-horizontal-space-between-columns: 0.1cm,
  entries-vertical-space-between-entries: 1.2em,
  entries-allow-page-break-in-sections: true,
  entries-allow-page-break-in-entries: true,
  highlights-bullet: "◦",
  highlights-nested-bullet: "-",
  highlights-top-margin: 0.25cm,
  highlights-left-margin: 0.4cm,
  highlights-vertical-space-between-highlights: 0.25cm,
  highlights-horizontal-space-between-bullet-and-highlights: 0.5em,
  highlights-summary-left-margin: 0cm,
  entry-types-education-entry-degree-column-width: 1cm,
  date: datetime(
    year: 2025,
    month: 11,
    day: 26,
  ),
)

= John Doe

#connections(
)

== Experience

Software Engineer at Company X, 2020-2023

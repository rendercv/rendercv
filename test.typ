// Import the rendercv function and all the refactored components
#import "lib.typ": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John #emph[Doe] hey\@",
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
  colors-name: rgb(0, 79, 144),
  colors-connections: rgb(0, 79, 144),
  colors-section-titles: rgb(0, 79, 144),
  colors-links: rgb(0, 79, 144),
  colors-last-updated-date-and-page-numbering: rgb(128, 128, 128),
  text-font-family: "Source Sans 3",
  text-font-size: 10pt,
  text-leading: 0.6em,
  text-alignment: "justified",
  text-date-and-location-column-alignment: "right",
  links-underline: false,
  links-use-external-link-icon: true,
  header-name-font-family: "Source Sans 3",
  header-name-font-size: 30pt,
  header-name-bold: true,
  header-small-caps-for-name: false,
  header-photo-width: 3.5cm,
  header-connections-font-family: "Source Sans 3",
  header-vertical-space-between-name-and-connections: 0.7cm,
  header-vertical-space-between-connections-and-first-section: 0.7cm,
  header-horizontal-space-between-connections: 0.5cm,
  header-separator-between-connections: "",
  header-alignment: center,
  section-titles-type: "with-partial-line",
  section-titles-font-family: "Source Sans 3",
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
  entries-short-second-row: false,
  highlights-bullet: "•",
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
    day: 21,
  ),
)

= John #emph[Doe] hey\@

  Software Engineer
  
#connections(
  [#connection-with-icon("location-dot")[Location]],
  [#link("mailto:john.doe@example.com", icon: false)[#connection-with-icon("envelope")[john.doe\@example.com]]],
  [#link("tel:+1-609-999-9995", icon: false)[#connection-with-icon("phone")[(609) 999-9995]]],
  [#link("https://linkedin.com/in/john.doe", icon: false)[#connection-with-icon("linkedin")[john.doe]]],
  [#link("https://github.com/john.doe", icon: false)[#connection-with-icon("github")[john.doe]]],
)

== Welcome to RenderCV!

[RenderCV](https://rendercv.com) is a Typst-based CV framework designed for academics and engineers, with Markdown syntax support.

Each section title is arbitrary. Each section contains a list of entries, and there are 7 different entry types to choose from.

== Education

#education-entry(
  [
    #strong[Stanford University], Computer Science
    - Working on the optimization of autonomous vehicles in urban environments
  ],
  [
    Stanford, CA, USA
  ],
  degree-column: [
    #strong[PhD]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Computer Engineering
    - GPA: 3.9\/4.0, ranked 1st out of 100 students
    - Awards: Best Senior Project, High Honor
  ],
  [
    Istanbul, Türkiye
  ],
  degree-column: [
    #strong[BS]
  ],
)

== Experience

#regular-entry(
  [
    #strong[Company C], Summer Intern
    - Developed deep learning models for the detection of gravitational waves in LIGO data
    - Published #link("https://example.com")[3 peer-reviewed research papers] about the project and results
  ],
  [
    Livingston, LA, USA
  ],
)

#regular-entry(
  [
    #strong[Company B], Summer Intern
    - Optimized the production line by 15\% by implementing a new scheduling algorithm
  ],
  [
    Ankara, Türkiye
  ],
)

#regular-entry(
  [
    #strong[Company A], Summer Intern
    - Designed an inventory management web application for a warehouse
  ],
  [
    Istanbul, Türkiye
  ],
)

== Projects

#regular-entry(
  [
    #strong[#link("https://example.com")[Example Project]]
    
    A web application for writing essays
    
    - Launched an #link("https://example.com")[iOS app] in 09\/2024 that currently has 10k+ monthly active users
    
    - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub])
    
  ],
  [
    
  ],
)

#regular-entry(
  [
    #strong[#link("https://example.com")[Teaching on Udemy]]
    
    - Instructed the \"Statistics\" course on Udemy (60,000+ students, 200,000+ hours watched)
    
  ],
  [
    Fall 2023
  ],
)

== Skills







== Publications

#regular-entry(
  [
    #strong[3D Finite Element Analysis of No-Insulation Coils]
Frodo Baggins, #strong[#emph[John Doe]], Samwise Gamgee
  ],
  [
    Jan 2004
  ],
)

== Extracurricular Activities

- There are 7 unique entry types in RenderCV: #emph[BulletEntry], #emph[TextEntry], #emph[EducationEntry], #emph[ExperienceEntry], #emph[NormalEntry], #emph[PublicationEntry], and #emph[OneLineEntry].

- Each entry type has a different structure and layout. This document demonstrates all of them.

== Numbered Entries

+ This is a numbered entry.

+ This is another numbered entry.

+ This is the third numbered entry.

== Reversed Numbered Entries

#reversed-numbered-entries(
  [

+ This is a reversed numbered entry.

+ This is another reversed numbered entry.

+ This is the third reversed numbered entry.
  ],
)

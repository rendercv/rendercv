// Import the rendercv function and all the refactored components
#import "lib.typ": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  footer: context { "John Doe - " + str(here().page()) + "/" + str(counter(page).final().first()) + "" },
  top-note: "Last updated in Nov 2025",
  locale-catalog-language: "en",
  page-size: "us-letter",
  page-top-margin: 2cm,
  page-bottom-margin: 2cm,
  page-left-margin: 2cm,
  page-right-margin: 2cm,
  colors-text: rgb(0, 0, 0),
  colors-name: rgb(0, 0, 0),
  colors-headline: rgb(0, 79, 144),
  colors-connections: rgb(0, 0, 0),
  colors-section-titles: rgb(0, 0, 0),
  colors-links: rgb(0, 0, 0),
  colors-footer: rgb(128, 128, 128),
  colors-top-note: rgb(128, 128, 128),
  typography-line-spacing: 0.6em,
  typography-alignment: "justified",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "XCharter",
  typography-font-family-name: "XCharter",
  typography-font-family-headline: "Source Sans 3",
  typography-font-family-connections: "XCharter",
  typography-font-family-section-titles: "XCharter",
  typography-font-size-body: 10pt,
  typography-font-size-name: 25pt,
  typography-font-size-headline: 20pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.2em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: false,
  typography-bold-headline: true,
  typography-bold-connections: true,
  typography-bold-section-titles: true,
  links-underline: true,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.7cm,
  header-space-below-connections: 0.7cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: false,
  header-connections-display-urls-instead-of-usernames: true,
  header-connections-separator: "|",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "with_full_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.55cm,
  section-titles-space-below: 0.3cm,
  sections-allow-page-break: true,
  sections-space-between-entries: 0.4cm,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: true,
  entries-short-second-row: false,
  entries-summary-space-left: 0cm,
  entries-highlights-bullet: "•",
  entries-highlights-nested-bullet: "-",
  entries-highlights-space-left: 0cm,
  entries-highlights-space-above: 0.25cm,
  entries-highlights-space-between-items: 0.19cm,
  entries-highlights-space-between-bullet-and-text: 0.3em,
  date: datetime(
    year: 2025,
    month: 11,
    day: 27,
  ),
)

= John Doe

#connections(
  [Location],
  [#link("mailto:john.doe@example.com", icon: false, if-underline: false, if-color: false)[john.doe\@example.com]],
  [#link("tel:+1-609-999-9995", icon: false, if-underline: false, if-color: false)[(609) 999-9995]],
  [#link("https://linkedin.com/in/john.doe", icon: false, if-underline: false, if-color: false)[linkedin.com\/in\/john.doe]],
  [#link("https://github.com/john.doe", icon: false, if-underline: false, if-color: false)[github.com\/john.doe]],
)

== Welcome to RenderCV!

#link("https://rendercv.com")[RenderCV] is a Typst-based CV framework designed for academics and engineers, with Markdown syntax support.

Each section title is arbitrary. Each section contains a list of entries, and there are 7 different entry types to choose from.

== Education

#education-entry(
  [
    #strong[Stanford University], PhD in Computer Science -- Stanford, CA, USA
    
    - Working on the optimization of autonomous vehicles in urban environments
    
  ],
  [
    Sept 2023 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Computer Engineering -- Istanbul, Türkiye
    
    - GPA: 3.9\/4.0, ranked 1st out of 100 students
    
    - Awards: Best Senior Project, High Honor
    
  ],
  [
    Sept 2018 – June 2022
    
  ],
)

== Experience

#regular-entry(
  [
    #strong[Summer Intern], Company C -- Livingston, LA, USA
    
    - Developed deep learning models for the detection of gravitational waves in LIGO data
    
    - Published #link("https://example.com")[3 peer-reviewed research papers] about the project and results
    
  ],
  [
    June 2024 – Sept 2024
    
  ],
)

#regular-entry(
  [
    #strong[Summer Intern], Company B -- Ankara, Türkiye
    
    - Optimized the production line by 15\% by implementing a new scheduling algorithm
    
  ],
  [
    June 2023 – Sept 2023
    
  ],
)

#regular-entry(
  [
    #strong[Summer Intern], Company A -- Istanbul, Türkiye
    
    - Designed an inventory management web application for a warehouse
    
  ],
  [
    June 2022 – Sept 2022
    
  ],
)

== Projects

#regular-entry(
  [
    #strong[#link("https://example.com")[Example Project]]
    
    #summary[A web application for writing essays]
    
    - Launched an #link("https://example.com")[iOS app] in 09\/2024 that currently has 10k+ monthly active users
    
    - The app is made open-source (3,000+ stars #link("https://github.com")[on GitHub])
    
  ],
  [
    May 2024 – present
    
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

#strong[Programming:] Proficient with Python, C++, and Git; good understanding of Web, app development, and DevOps

#strong[Mathematics:] Good understanding of differential equations, calculus, and linear algebra

#strong[Languages:] English (fluent, TOEFL: 118\/120), Turkish (native)

== Publications

#regular-entry(
  [
    #strong[3D Finite Element Analysis of No-Insulation Coils]
    
    Frodo Baggins, #strong[#emph[John Doe]], Samwise Gamgee
    
    #link("https://doi.org/10.1109/TASC.2023.3340648")[10.1109\/TASC.2023.3340648]
    
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

// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.1.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  footer: context { [#emph[John Doe -- #str(here().page())\/#str(counter(page).final().first())]] },
  top-note: [ #emph[Last updated in Nov 2025] ],
  locale-catalog-language: "en",
  page-size: "us-letter",
  page-top-margin: 0.7in,
  page-bottom-margin: 0.7in,
  page-left-margin: 0.7in,
  page-right-margin: 0.7in,
  page-show-footer: true,
  page-show-top-note: true,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(0, 79, 144),
  colors-headline: rgb(0, 79, 144),
  colors-connections: rgb(0, 79, 144),
  colors-section-titles: rgb(0, 79, 144),
  colors-links: rgb(0, 79, 144),
  colors-footer: rgb(128, 128, 128),
  colors-top-note: rgb(128, 128, 128),
  typography-line-spacing: 0.6em,
  typography-alignment: "justified",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "Source Sans 3",
  typography-font-family-name: "Source Sans 3",
  typography-font-family-headline: "Source Sans 3",
  typography-font-family-connections: "Source Sans 3",
  typography-font-family-section-titles: "Source Sans 3",
  typography-font-size-body: 10pt,
  typography-font-size-name: 30pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.4em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: true,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.7cm,
  header-space-below-connections: 0.7cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: true,
  header-connections-display-urls-instead-of-usernames: false,
  header-connections-separator: "",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "with_partial_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.5cm,
  section-titles-space-below: 0.3cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.3em,
  sections-space-between-regular-entries: 1.2em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.2cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: false,
  entries-short-second-row: true,
  entries-degree-width: 1cm,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0cm,
  entries-highlights-bullet:  "•" ,
  entries-highlights-nested-bullet:  "•" ,
  entries-highlights-space-left: 0.15cm,
  entries-highlights-space-above: 0cm,
  entries-highlights-space-between-items: 0cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime(
    year: 2025,
    month: 11,
    day: 30,
  ),
)


#grid(
  columns: (auto, 1fr),
  column-gutter: 0cm,
  align: horizon + left,
  [#pad(left: 0.4cm, right: 0.4cm, image("profile_picture.jpg", width: 3.5cm))
],
  [
= John Doe

  #headline([AI Researcher and Entrepreneur])

#connections(
  [#connection-with-icon("location-dot")[Istanbul, Turkey]],
  [#link("mailto:john_doe@example.com", icon: false, if-underline: false, if-color: false)[#connection-with-icon("envelope")[john\_doe\@example.com]]],
  [#link("tel:+90-541-999-99-99", icon: false, if-underline: false, if-color: false)[#connection-with-icon("phone")[0541 999 99 99]]],
  [#link("https://example.com/", icon: false, if-underline: false, if-color: false)[#connection-with-icon("link")[example.com]]],
  [#link("https://linkedin.com/in/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("linkedin")[johndoe]]],
  [#link("https://github.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("github")[johndoe]]],
  [#link("https://imdb.com/name/nm0000001", icon: false, if-underline: false, if-color: false)[#connection-with-icon("imdb")[nm0000001]]],
  [#link("https://instagram.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("instagram")[johndoe]]],
  [#link("https://orcid.org/0000-0000-0000-0000", icon: false, if-underline: false, if-color: false)[#connection-with-icon("orcid")[0000-0000-0000-0000]]],
  [#link("https://scholar.google.com/citations?user=F8IyYrQAAAAJ", icon: false, if-underline: false, if-color: false)[#connection-with-icon("graduation-cap")[Google Scholar]]],
  [#link("https://example.com/@johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("mastodon")[\@johndoe\@example.com]]],
  [#link("https://stackoverflow.com/users/12323/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("stack-overflow")[12323\/johndoe]]],
  [#link("https://gitlab.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("gitlab")[johndoe]]],
  [#link("https://researchgate.net/profile/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("researchgate")[johndoe]]],
  [#link("https://youtube.com/@johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("youtube")[johndoe]]],
  [#link("https://t.me/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("telegram")[johndoe]]],
  [#link("https://wa.me/+14155552671", icon: false, if-underline: false, if-color: false)[#connection-with-icon("whatsapp")[+14155552671]]],
  [#link("https://x.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("x-twitter")[johndoe]]],
  [#link("https://bsky.app/profile/johndoe.bsky.social", icon: false, if-underline: false, if-color: false)[#connection-with-icon("bluesky")[johndoe.bsky.social]]],
  [#link("https://reddit.com/user/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("reddit")[johndoe]]],
)
  ]
)


== Text Entries

This is a #emph[TextEntry]. It is only a text and can be useful for sections like #strong[Summary]. To showcase the TextEntry completely, this sentence is added, but it doesn't contain any information.

Another text entry with #emph[markdown] and #strong[bold] text. This is the second text entry.

Third text with #link("https://example.com")[link] and more content.

== Publication Entries

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

     (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

     (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

     (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

     (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://example.com/")[example.com] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of No-Insulation Coils]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    J. Doe, #strong[#emph[H. Tom]], S. Doe, A. Andsurname, S. Doe, A. Andsurname

    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)

  ],
  [
    Sept 2021

  ],
)

== Experience Entries

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[Some Company], Software Engineer

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

== Education Entries

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
  degree-column: [
    #strong[BS]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Mechanical Engineering

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
  degree-column: [
    #strong[BS]
  ],
)

== Normal Entries

#regular-entry(
  [
    #strong[My Project]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

  ],
)

#regular-entry(
  [
    #strong[My Project]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – present

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2015 – June 2020

  ],
)

#regular-entry(
  [
    #strong[My Project]

    #summary[Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.]

    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

      - Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.

  ],
  [
    Istanbul, Turkey

    Sept 2021

  ],
)

== One Line Entries

#strong[Programming:] Python, C++, JavaScript, MATLAB

#strong[Programming:] Python, C++, JavaScript, MATLAB

== Bullet Entries

- This is a bullet entry.

- This is a bullet entry.

== Numbered Entries

+ This is a numbered entry.

+ This is a numbered entry.

== Reversed Numbered Entries

#reversed-numbered-entries(
  [

+ This is a reversed numbered entry.

+ This is a reversed numbered entry.

+ This is a reversed numbered entry.
  ],
)

== A Section & with \% Special Characters

#regular-entry(
  [
    #strong[A Section & with \% Special Characters]

  ],
  [
  ],
)

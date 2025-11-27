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
  typography-font-family-body: "Raleway",
  typography-font-family-name: "Raleway",
  typography-font-family-headline: "Source Sans 3",
  typography-font-family-connections: "Raleway",
  typography-font-family-section-titles: "Raleway",
  typography-font-size-body: 10pt,
  typography-font-size-name: 30pt,
  typography-font-size-headline: 20pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.4em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: false,
  typography-bold-headline: true,
  typography-bold-connections: true,
  typography-bold-section-titles: false,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: left,
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
  sections-space-between-entries: 1.2em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.2cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: true,
  entries-short-second-row: false,
  entries-summary-space-left: 0cm,
  entries-highlights-bullet: "•",
  entries-highlights-nested-bullet: "-",
  entries-highlights-space-left: 0cm,
  entries-highlights-space-above: 0.25cm,
  entries-highlights-space-between-items: 0.25cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime(
    year: 2025,
    month: 11,
    day: 27,
  ),
)

= John Doe

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
  [#link("https://scholar.google.com/citations?user=F8IyYrQAAAAJ", icon: false, if-underline: false, if-color: false)[#connection-with-icon("graduation-cap")[F8IyYrQAAAAJ]]],
  [#link("https://example.com/@johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("mastodon")[\@johndoe\@example.com]]],
  [#link("https://stackoverflow.com/users/12323/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("stack-overflow")[12323\/johndoe]]],
  [#link("https://gitlab.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("gitlab")[johndoe]]],
  [#link("https://researchgate.net/profile/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("researchgate")[johndoe]]],
  [#link("https://youtube.com/@johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("youtube")[johndoe]]],
  [#link("https://t.me/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("telegram")[johndoe]]],
  [#link("https://x.com/johndoe", icon: false, if-underline: false, if-color: false)[#connection-with-icon("x-twitter")[johndoe]]],
)

== Text Entries

This is a #emph[TextEntry]. It is only a text and can be useful for sections like #strong[Summary]. To showcase the TextEntry completely, this sentence is added, but it doesn't contain any information.

Another text entry with #emph[markdown] and #strong[bold] text. This is the second text entry.

Third text with #link("https://example.com")[link] and more content.

== Bullet Entries

- This is a bullet entry.

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
    
    #link("https://example.com/")[example.com] (IEEE Transactions on Applied Superconductivity)
    
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
    
    #link("https://doi.org/10.1007/978-3-319-69626-3_101-1")[10.1007\/978-3-319-69626-3\_101-1] (IEEE Transactions on Applied Superconductivity)
    
  ],
  [
    Sept 2021
    
  ],
)

== Experience Entries

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[Software Engineer], Some Company -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

== Education Entries

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University],  in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Mechanical Engineering -- Istanbul, Turkey
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
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
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
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
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
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
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
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
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – present
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2015 – June 2020
    
  ],
)

#regular-entry(
  [
    #strong[My Project] -- #strong[Istanbul, Turkey]
    
    #summary[
    
    Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    ]
    
    - Did #emph[this] and this is a #strong[bold] #link("https://example.com")[link]. But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful.
    
    - Did that. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.
    
  ],
  [
    Sept 2021
    
  ],
)

== One Line Entries

#strong[Pro]gram#strong[ming:] Python, C++, JavaScript, MATLAB

== Numbered Entries

+ This is a numbered entry.

== Reversed Numbered Entries

#reversed-numbered-entries(
  [

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

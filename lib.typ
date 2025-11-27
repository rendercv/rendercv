
#import "@preview/fontawesome:0.5.0": fa-icon

// State to hold rendercv configuration for use by components
#let rendercv-config = state("rendercv-config", (:))

#let connections(..connections) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()
    let typography-line-spacing = config.at("typography-line-spacing")
    let header-connections-space-between-connections = config.at("header-connections-space-between-connections")
    let header-connections-separator = config.at("header-connections-separator")
    let page-left-margin = config.at("page-left-margin")
    let page-right-margin = config.at("page-right-margin")
    let header-space-below-connections = config.at("header-space-below-connections")
    let header-space-below-name = config.at("header-space-below-name")
    let section-titles-space-above = config.at("section-titles-space-above")
    let colors-connections = config.at("colors-connections")
    let typography-font-family-connections = config.at("typography-font-family-connections")
    let typography-font-size-connections = config.at("typography-font-size-connections")
    let typography-small-caps-connections = config.at("typography-small-caps-connections")
    let typography-bold-connections = config.at("typography-bold-connections")
    let header-alignment = config.at("header-alignment")

    set par(spacing: 0pt, leading: typography-line-spacing * 1.7, justify: false)
    set text(
      fill: colors-connections,
      font: typography-font-family-connections,
      size: typography-font-size-connections,
      weight: if typography-bold-connections { 700 } else { 400 },
    )
    let separator = (
      h(header-connections-space-between-connections / 2, weak: true)
        + header-connections-separator
        + h(header-connections-space-between-connections / 2, weak: true)
    )
    let line-width = 0cm
    let separator-width = (
      measure(header-connections-separator).width + header-connections-space-between-connections
    )
    v(header-space-below-name, weak: true)
    if connections.pos().len() > 0 {
      align(
        header-alignment,
        {
          for connection in connections.pos().slice(0, -1) {
            let connection-body = if typography-small-caps-connections { smallcaps(connection) } else { connection }
            box(connection-body, width: auto)
            line-width = line-width + measure(connection-body).width * 1.2 + separator-width
            if line-width > page.width - page-left-margin - page-right-margin {
              line-width = 0cm
              linebreak()
            } else {
              separator
            }
          }
          let last-connection = connections.pos().last()
          let last-connection-body = if typography-small-caps-connections { smallcaps(last-connection) } else {
            last-connection
          }
          box(last-connection-body, width: auto)
        },
      )
    }
    v(header-space-below-connections - section-titles-space-above)
  }
}

#let original-link = link
#let link(dest, body, icon: none, if-underline: none, if-color: none) = context {
  let config = rendercv-config.get()
  let links-underline = config.at("links-underline")
  let links-show-external-link-icon = config.at("links-show-external-link-icon")
  let typography-font-size-body = config.at("typography-font-size-body")
  let colors-links = config.at("colors-links")

  let icon = icon
  if icon == none {
    if links-show-external-link-icon {
      icon = true
    } else {
      icon = false
    }
  }
  let if-underline = if-underline
  if if-underline == none {
    if links-underline {
      if-underline = true
    } else {
      if-underline = false
    }
  }
  let if-color = if-color
  if if-color == none {
    if-color = true
  }

  let body = [#if if-underline [#underline(body)] else [#body]]
  if icon {
    body = [#body#h(typography-font-size-body / 4)#box(
        fa-icon("external-link", size: 0.7em),
        baseline: -10%,
      )#h(typography-font-size-body / 5)]
  }
  body = [#if if-color [#set text(fill: colors-links); #body] else [#body]]
  original-link(dest, body)
}

#let connection-with-icon(icon-name, body) = [
  #fa-icon(icon-name, size: 0.9em) #h(0.05cm) #body
]

#let content-area(content) = context {
  let config = rendercv-config.get()
  let entries-side-space = config.at("entries-side-space")
  let entries-date-and-location-width = config.at("entries-date-and-location-width")
  let entries-space-between-columns = config.at("entries-space-between-columns")
  let entries-allow-page-break = config.at("entries-allow-page-break")
  let sections-space-between-entries = config.at("sections-space-between-entries")
  let section-titles-type = config.at("section-titles-type")
  let typography-line-spacing = config.at("typography-line-spacing")
  let justify = config.at("justify")
  let entries-highlights-bullet = config.at("entries-highlights-bullet")
  let entries-highlights-nested-bullet = config.at("entries-highlights-nested-bullet")
  let entries-highlights-space-between-bullet-and-text = config.at(
    "entries-highlights-space-between-bullet-and-text",
  )

  let left-space = entries-side-space
  if section-titles-type == "moderncv" {
    left-space = (
      left-space + entries-date-and-location-width + entries-space-between-columns
    )
  }

  set par(
    spacing: sections-space-between-entries,
    leading: typography-line-spacing,
    justify: justify,
  )
  set align(left)
  set enum(
    spacing: sections-space-between-entries,
  )
  set list(
    marker: (entries-highlights-bullet, entries-highlights-nested-bullet),
    indent: 0cm,
    spacing: sections-space-between-entries,
    body-indent: entries-highlights-space-between-bullet-and-text,
  )

  block(
    content,
    breakable: entries-allow-page-break,
    below: sections-space-between-entries,
    inset: (
      left: left-space,
      right: entries-side-space,
    ),
    width: 100%,
  )
}

#let summary(summary) = {
  context {
    let config = rendercv-config.get()
    let entries-summary-space-left = config.at("entries-summary-space-left")
    block(summary, inset: (left: entries-summary-space-left))
  }
}

#let regular-entry(main-column, date-and-location-column, main-column-second-row: none) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()
    let section-titles-type = config.at("section-titles-type")
    let entries-date-and-location-width = config.at("entries-date-and-location-width")
    let entries-space-between-columns = config.at("entries-space-between-columns")
    let entries-highlights-bullet = config.at("entries-highlights-bullet")
    let entries-highlights-nested-bullet = config.at("entries-highlights-nested-bullet")
    let entries-highlights-space-between-items = config.at(
      "entries-highlights-space-between-items",
    )
    let entries-highlights-space-between-bullet-and-text = config.at(
      "entries-highlights-space-between-bullet-and-text",
    )
    let entries-highlights-space-above = config.at("entries-highlights-space-above")
    let typography-line-spacing = config.at("typography-line-spacing")
    let entries-allow-page-break = config.at("entries-allow-page-break")
    let sections-space-between-entries = config.at("sections-space-between-entries")
    let entries-side-space = config.at("entries-side-space")
    let justify = config.at("justify")
    let typography-date-and-location-column-alignment = config.at("typography-date-and-location-column-alignment")
    let entries-highlights-space-left = config.at("entries-highlights-space-left")

    set list(
      marker: (entries-highlights-bullet, entries-highlights-nested-bullet),
      indent: entries-highlights-space-left,
      spacing: entries-highlights-space-between-items,
      body-indent: entries-highlights-space-between-bullet-and-text,
    )
    let list-depth = state("list-depth", 0)
    show list.item: i => {
      list-depth.update(d => d + 1)
      i
      list-depth.update(d => d - 1)
    }
    show list: l => {
      context if list-depth.get() == 1 {
        v(entries-highlights-space-above)
      }
      context if list-depth.get() == 2 {
        v(entries-highlights-space-between-items - typography-line-spacing)
      }
      l
    }
    set par(
      spacing: typography-line-spacing,
      leading: typography-line-spacing,
      justify: justify,
    )
    block(
      {
        if section-titles-type == "moderncv" {
          grid(
            columns: (entries-date-and-location-width, 1fr),
            column-gutter: entries-space-between-columns,
            align: (typography-date-and-location-column-alignment, left),
            [
              #date-and-location-column
            ],
            [
              #main-column
            ],
          )
        } else {
          grid(
            columns: (1fr, entries-date-and-location-width),
            column-gutter: entries-space-between-columns,
            align: (left, typography-date-and-location-column-alignment),
            [
              #main-column
            ],
            [
              #date-and-location-column
            ],
          )
          set align(left)
          main-column-second-row
        }
      },
      breakable: entries-allow-page-break,
      below: sections-space-between-entries,
      inset: (
        left: entries-side-space,
        right: entries-side-space,
      ),
      width: 100%,
    )
  }
}

#let education-entry(main-column, date-and-location-column, degree-column: none, main-column-second-row: none) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()
    let entries-space-between-columns = config.at("entries-space-between-columns")

    // Fixed width for degree column (GPA, etc.)
    let degree-column-width = 1cm

    regular-entry(
      if degree-column != none {
        grid(
          columns: (degree-column-width, 1fr),
          column-gutter: entries-space-between-columns,
          align: (left, auto),
          [
            #degree-column
          ],
          [
            #main-column
          ],
        )
      } else {
        main-column
      },
      date-and-location-column,
      main-column-second-row: [
        #block(
          main-column-second-row,
          inset: (
            left: degree-column-width + entries-space-between-columns,
            right: 0cm,
          ),
        )
      ],
    )
  }
}

#let reversed-numbered-entries(entries) = {
  set enum(reversed: true)
  entries
}

#let rendercv(
  doc,
  name: "John Doe",
  footer: context { "Page " + str(here().page()) + " of " + str(counter(page).final().first()) + "" },
  top-note: "Last updated in Oct 2025",
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
  links-show-external-link-icon: true,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.3cm,
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
  entries-highlights-space-left: 0.4cm,
  entries-highlights-space-above: 0.25cm,
  entries-highlights-space-between-items: 0.25cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime.today(),
) = [
  #let (justify, hyphenate) = (
    "justified": (true, true),
    "left": (false, false),
    "justified-with-no-hyphenation": (true, false),
  ).at(typography-alignment)


  // Initialize state with all configuration parameters
  #rendercv-config.update((
    // Page
    page-left-margin: page-left-margin,
    page-right-margin: page-right-margin,
    // Colors
    colors-text: colors-text,
    colors-name: colors-name,
    colors-headline: colors-headline,
    colors-connections: colors-connections,
    colors-section-titles: colors-section-titles,
    colors-links: colors-links,
    colors-footer: colors-footer,
    colors-top-note: colors-top-note,
    // Typography
    typography-line-spacing: typography-line-spacing,
    typography-alignment: typography-alignment,
    typography-date-and-location-column-alignment: typography-date-and-location-column-alignment,
    typography-font-family-body: typography-font-family-body,
    typography-font-family-name: typography-font-family-name,
    typography-font-family-headline: typography-font-family-headline,
    typography-font-family-connections: typography-font-family-connections,
    typography-font-family-section-titles: typography-font-family-section-titles,
    typography-font-size-body: typography-font-size-body,
    typography-font-size-name: typography-font-size-name,
    typography-font-size-headline: typography-font-size-headline,
    typography-font-size-connections: typography-font-size-connections,
    typography-font-size-section-titles: typography-font-size-section-titles,
    typography-small-caps-name: typography-small-caps-name,
    typography-small-caps-headline: typography-small-caps-headline,
    typography-small-caps-connections: typography-small-caps-connections,
    typography-small-caps-section-titles: typography-small-caps-section-titles,
    typography-bold-name: typography-bold-name,
    typography-bold-headline: typography-bold-headline,
    typography-bold-connections: typography-bold-connections,
    typography-bold-section-titles: typography-bold-section-titles,
    // Links
    links-underline: links-underline,
    links-show-external-link-icon: links-show-external-link-icon,
    // Header
    header-alignment: header-alignment,
    header-photo-width: header-photo-width,
    header-space-below-name: header-space-below-name,
    header-space-below-headline: header-space-below-headline,
    header-space-below-connections: header-space-below-connections,
    header-connections-hyperlink: header-connections-hyperlink,
    header-connections-show-icons: header-connections-show-icons,
    header-connections-display-urls-instead-of-usernames: header-connections-display-urls-instead-of-usernames,
    header-connections-separator: header-connections-separator,
    header-connections-space-between-connections: header-connections-space-between-connections,
    // Section titles
    section-titles-type: section-titles-type,
    section-titles-line-thickness: section-titles-line-thickness,
    section-titles-space-above: section-titles-space-above,
    section-titles-space-below: section-titles-space-below,
    // Sections
    sections-allow-page-break: sections-allow-page-break,
    sections-space-between-entries: sections-space-between-entries,
    // Entries
    entries-date-and-location-width: entries-date-and-location-width,
    entries-side-space: entries-side-space,
    entries-space-between-columns: entries-space-between-columns,
    entries-allow-page-break: entries-allow-page-break,
    entries-short-second-row: entries-short-second-row,
    entries-summary-space-left: entries-summary-space-left,
    entries-highlights-bullet: entries-highlights-bullet,
    entries-highlights-nested-bullet: entries-highlights-nested-bullet,
    entries-highlights-space-left: entries-highlights-space-left,
    entries-highlights-space-above: entries-highlights-space-above,
    entries-highlights-space-between-items: entries-highlights-space-between-items,
    entries-highlights-space-between-bullet-and-text: entries-highlights-space-between-bullet-and-text,
    // Internal computed values
    justify: justify,
  ))

  // Metadata:
  #set document(author: name, title: name + "'s CV", date: date)

  // Page:
  #set page(
    margin: (
      top: page-top-margin,
      bottom: page-bottom-margin,
      left: page-left-margin,
      right: page-right-margin,
    ),
    paper: page-size,
    footer: if footer != none and footer != "" {
      text(
        fill: colors-footer,
        align(center, [_#footer _]),
        size: 0.9em,
      )
    } else {
      none
    },
    footer-descent: 0% - 0.6em + page-bottom-margin / 2,
  )

  // Text:
  #set text(
    font: typography-font-family-body,
    size: typography-font-size-body,
    lang: locale-catalog-language,
    hyphenate: hyphenate,
    fill: colors-text,
    // Disable ligatures for better ATS compatibility:
    ligatures: true,
  )

  // Main heading (name):
  #show heading.where(level: 1): it => [
    #set par(spacing: 0pt)
    #set align(header-alignment)
    #set text(
      font: typography-font-family-name,
      size: typography-font-size-name,
      fill: colors-name,
      weight: if typography-bold-name { 700 } else { 400 },
    )
    #let body
    #if typography-small-caps-name {
      body = [#smallcaps(it.body)]
    } else {
      body = [#it.body]
    }
    #body
    // Vertical space after the name
    #v(header-space-below-name, weak: true)
  ]

  // Section titles:
  #show heading.where(level: 2): it => [
    #set align(left)
    #set text(size: (1em / 1.2)) // reset
    #set text(
      font: typography-font-family-section-titles,
      size: (typography-font-size-section-titles),
      weight: if typography-bold-section-titles { 700 } else { 400 },
      fill: colors-section-titles,
    )
    #let section-title = (
      if typography-small-caps-section-titles [
        #smallcaps(it.body)
      ] else [
        #it.body
      ]
    )
    // Vertical space above the section title
    #v(section-titles-space-above, weak: true)

    #block(
      breakable: false,
      width: 100%,
      [
        #if section-titles-type == "moderncv" [
          #grid(
            columns: (entries-date-and-location-width + entries-space-between-columns, 1fr),
            column-gutter: entries-space-between-columns,
            align: (right, left),
            [
              #align(horizon, box(
                width: 1fr,
                height: section-titles-line-thickness,
                fill: colors-section-titles,
              ))
            ],
            [
              #section-title
            ],
          )
        ] else [
          #section-title
          #if section-titles-type == "with_partial_line" [
            #box(width: 1fr, height: section-titles-line-thickness, fill: colors-section-titles)
          ] else if section-titles-type == "with_full_line" [
            #box[#place(
              dy: typography-font-size-body * 0.4,
              dx: -measure(section-title).width * 1.2,
              box(width: 1fr, height: section-titles-line-thickness, fill: colors-section-titles),
            )]
          ]
        ]
      ],
    )

    // Compensation for the full line section title
    #if section-titles-type == "with_full_line" [
      #v(typography-font-size-body * 0.4)
    ]

    // Vertical space after the section title
    #v(section-titles-space-below - 0.5em)
  ]

  // Top note:
  #if top-note != none and top-note != "" {
    let dx = -entries-side-space
    place(
      top + right,
      dy: -page-top-margin / 2,
      dx: dx,
      text(
        [_#top-note _],
        fill: colors-top-note,
        size: 0.9em,
      ),
    )
  }

  // From: https://github.com/typst/typst/issues/2666
  #let group-sections(content) = {
    let sections = content
      .children
      .fold((), (arr, element) => {
        if element.func() == heading {
          // push a new section with the elements
          arr.push((element, ()))
        } else if arr.len() > 0 {
          // add this content to the current section
          arr.last().at(1).push(element)
        }
        arr
      }) // join the content following the selector:
      .map(it => {
        let (title, content) = it
        (title, content.join())
      })
    sections
  }

  #set par(spacing: 0cm)
  #set align(center)

  #for (section-title, section-content) in group-sections(doc) [
    #section-title
    // Check if section-content has skip-content-area metadata
    #let should-skip = {
      let skip = false
      if section-content.has("children") {
        for child in section-content.children {
          if child.func() == metadata and child.value == "skip-content-area" {
            skip = true
            break
          }
        }
      }
      skip
    }
    #if section-content.func() != parbreak [
      #block(
        breakable: sections-allow-page-break,
      )[
        #if should-skip [
          #section-content
        ] else [
          #content-area(section-content)
        ]
      ]
    ]
  ]
]

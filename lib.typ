
#import "@preview/fontawesome:0.5.0": fa-icon

// State to hold rendercv configuration for use by components
#let rendercv-config = state("rendercv-config", (:))

#let connections(..connections) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()
    let text-leading = config.at("text-leading")
    let header-horizontal-space-between-connections = config.at("header-horizontal-space-between-connections")
    let header-separator-between-connections = config.at("header-separator-between-connections")
    let page-left-margin = config.at("page-left-margin")
    let page-right-margin = config.at("page-right-margin")
    let header-vertical-space-between-connections-and-first-section = config.at(
      "header-vertical-space-between-connections-and-first-section",
    )
    let header-vertical-space-between-name-and-connections = config.at(
      "header-vertical-space-between-name-and-connections",
    )
    let section-titles-vertical-space-above = config.at("section-titles-vertical-space-above")
    let colors-connections = config.at("colors-connections")
    let header-connections-font-family = config.at("header-connections-font-family")
    let header-alignment = config.at("header-alignment")

    set par(spacing: 0pt, leading: text-leading * 1.7, justify: false)
    set text(fill: colors-connections, font: header-connections-font-family)
    let separator = (
      h(header-horizontal-space-between-connections / 2, weak: true)
        + header-separator-between-connections
        + h(header-horizontal-space-between-connections / 2, weak: true)
    )
    let line-width = 0cm
    let separator-width = (
      measure(header-separator-between-connections).width + header-horizontal-space-between-connections
    )
    v(header-vertical-space-between-name-and-connections, weak: true)
    align(
      header-alignment,
      {
        for connection in connections.pos().slice(0, -1) {
          box(connection, width: auto)
          line-width = line-width + measure(connection).width * 1.2 + separator-width
          if line-width > page.width - page-left-margin - page-right-margin {
            line-width = 0cm
            linebreak()
          } else {
            separator
          }
        }
        box(connections.pos().last(), width: auto)
      },
    )
    v(header-vertical-space-between-connections-and-first-section - section-titles-vertical-space-above)
  }
}

#let original-link = link
#let link(dest, body, icon: none, if-underline: none, if-color: none) = context {
  let config = rendercv-config.get()
  let links-underline = config.at("links-underline")
  let links-use-external-link-icon = config.at("links-use-external-link-icon")
  let text-font-size = config.at("text-font-size")
  let colors-links = config.at("colors-links")

  let icon = icon
  if icon == none {
    if links-use-external-link-icon {
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
    body = [#body#h(text-font-size / 4)#box(
        fa-icon("external-link", size: 0.7em),
        baseline: -10%,
      )#h(text-font-size / 5)]
  }
  body = [#if if-color [#set text(fill: colors-links); #body] else [#body]]
  original-link(dest, body)
}

#let connection-with-icon(icon-name, body) = [
  #fa-icon(icon-name, size: 0.9em) #h(0.05cm) #body
]

#let content-area(content) = context {
  let config = rendercv-config.get()
  let entries-left-and-right-margin = config.at("entries-left-and-right-margin")
  let entries-date-and-location-width = config.at("entries-date-and-location-width")
  let entries-horizontal-space-between-columns = config.at("entries-horizontal-space-between-columns")
  let entries-allow-page-break-in-entries = config.at("entries-allow-page-break-in-entries")
  let entries-vertical-space-between-entries = config.at("entries-vertical-space-between-entries")
  let section-titles-type = config.at("section-titles-type")
  let text-leading = config.at("text-leading")
  let justify = config.at("justify")
  let highlights-bullet = config.at("highlights-bullet")
  let highlights-nested-bullet = config.at("highlights-nested-bullet")
  let highlights-horizontal-space-between-bullet-and-highlights = config.at(
    "highlights-horizontal-space-between-bullet-and-highlights",
  )

  let left-space = entries-left-and-right-margin
  if section-titles-type == "moderncv" {
    left-space = (
      left-space + entries-date-and-location-width + entries-horizontal-space-between-columns
    )
  }

  set par(
    spacing: entries-vertical-space-between-entries,
    leading: text-leading,
    justify: justify,
  )
  set align(left)
  set enum(
    spacing: entries-vertical-space-between-entries,
  )
  set list(
    marker: (highlights-bullet, highlights-nested-bullet),
    indent: 0cm,
    spacing: entries-vertical-space-between-entries,
    body-indent: highlights-horizontal-space-between-bullet-and-highlights,
  )

  block(
    content,
    breakable: entries-allow-page-break-in-entries,
    below: entries-vertical-space-between-entries,
    inset: (
      left: left-space,
      right: entries-left-and-right-margin,
    ),
    width: 100%,
  )
}

#let regular-entry(main-column, date-and-location-column, main-column-second-row: none) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()
    let section-titles-type = config.at("section-titles-type")
    let entries-date-and-location-width = config.at("entries-date-and-location-width")
    let entries-horizontal-space-between-columns = config.at("entries-horizontal-space-between-columns")
    let highlights-bullet = config.at("highlights-bullet")
    let highlights-nested-bullet = config.at("highlights-nested-bullet")
    let highlights-vertical-space-between-highlights = config.at(
      "highlights-vertical-space-between-highlights",
    )
    let highlights-horizontal-space-between-bullet-and-highlights = config.at(
      "highlights-horizontal-space-between-bullet-and-highlights",
    )
    let highlights-top-margin = config.at("highlights-top-margin")
    let text-leading = config.at("text-leading")
    let entries-allow-page-break-in-entries = config.at("entries-allow-page-break-in-entries")
    let entries-vertical-space-between-entries = config.at("entries-vertical-space-between-entries")
    let entries-left-and-right-margin = config.at("entries-left-and-right-margin")
    let justify = config.at("justify")
    let text-date-and-location-column-alignment = config.at("text-date-and-location-column-alignment")

    set list(
      marker: (highlights-bullet, highlights-nested-bullet),
      indent: 0cm,
      spacing: highlights-vertical-space-between-highlights,
      body-indent: highlights-horizontal-space-between-bullet-and-highlights,
    )
    set par(
      spacing: highlights-top-margin,
      leading: text-leading,
      justify: justify,
    )
    block(
      {
        if section-titles-type == "moderncv" {
          grid(
            columns: (entries-date-and-location-width, 1fr),
            column-gutter: entries-horizontal-space-between-columns,
            align: (text-date-and-location-column-alignment, left),
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
            column-gutter: entries-horizontal-space-between-columns,
            align: (left, text-date-and-location-column-alignment),
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
      breakable: entries-allow-page-break-in-entries,
      below: entries-vertical-space-between-entries,
      inset: (
        left: entries-left-and-right-margin,
        right: entries-left-and-right-margin,
      ),
      width: 100%,
    )
  }
}

#let education-entry(main-column, date-and-location-column, degree-column: none, main-column-second-row: none) = {
  metadata("skip-content-area")

  context {
    let config = rendercv-config.get()

    let entry-types-education-entry-degree-column-width = config.at("entry-types-education-entry-degree-column-width")
    let entries-horizontal-space-between-columns = config.at("entries-horizontal-space-between-columns")

    regular-entry(
      if degree-column != none {
        grid(
          columns: (entry-types-education-entry-degree-column-width, 1fr),
          column-gutter: entries-horizontal-space-between-columns,
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
            left: entry-types-education-entry-degree-column-width + entries-horizontal-space-between-columns,
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
  footer-text: "Page 1 of 1",
  last-updated-date-text: "Last updated in Oct 2025",
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
  text-date-and-location-column-alignment: right,
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
  highlights-bullet: "•",
  highlights-nested-bullet: "-",
  highlights-top-margin: 0.25cm,
  highlights-left-margin: 0.4cm,
  highlights-vertical-space-between-highlights: 0.25cm,
  highlights-horizontal-space-between-bullet-and-highlights: 0.5em,
  highlights-summary-left-margin: 0cm,
  entry-types-education-entry-degree-column-width: 1cm,
  date: datetime.today(),
) = [
  #let (justify, hyphenate) = (
    "justified": (true, true),
    "left": (false, false),
    "justified-with-no-hyphenation": (true, false),
  ).at(text-alignment)


  // Initialize state with all configuration parameters
  #rendercv-config.update((
    entries-left-and-right-margin: entries-left-and-right-margin,
    section-titles-type: section-titles-type,
    section-titles-vertical-space-above: section-titles-vertical-space-above,
    entries-date-and-location-width: entries-date-and-location-width,
    entries-horizontal-space-between-columns: entries-horizontal-space-between-columns,
    text-leading: text-leading,
    entries-allow-page-break-in-entries: entries-allow-page-break-in-entries,
    text-date-and-location-column-alignment: text-date-and-location-column-alignment,
    entries-vertical-space-between-entries: entries-vertical-space-between-entries,
    highlights-bullet: highlights-bullet,
    highlights-nested-bullet: highlights-nested-bullet,
    highlights-vertical-space-between-highlights: highlights-vertical-space-between-highlights,
    highlights-horizontal-space-between-bullet-and-highlights: highlights-horizontal-space-between-bullet-and-highlights,
    highlights-top-margin: highlights-top-margin,
    entry-types-education-entry-degree-column-width: entry-types-education-entry-degree-column-width,
    header-horizontal-space-between-connections: header-horizontal-space-between-connections,
    header-separator-between-connections: header-separator-between-connections,
    header-alignment: header-alignment,
    page-left-margin: page-left-margin,
    page-right-margin: page-right-margin,
    header-vertical-space-between-connections-and-first-section: header-vertical-space-between-connections-and-first-section,
    header-vertical-space-between-name-and-connections: header-vertical-space-between-name-and-connections,
    header-connections-font-family: header-connections-font-family,
    links-underline: links-underline,
    links-use-external-link-icon: links-use-external-link-icon,
    text-font-size: text-font-size,
    colors-links: colors-links,
    colors-connections: colors-connections,
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
    footer: if page-show-page-numbering {
      text(
        fill: colors-last-updated-date-and-page-numbering,
        align(center, [_#footer-text _]),
        size: 0.9em,
      )
    } else {
      none
    },
    footer-descent: 0% - 0.6em + page-bottom-margin / 2,
  )

  // Text:
  #set text(
    font: text-font-family,
    size: text-font-size,
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
      font: header-name-font-family,
      size: header-name-font-size,
      fill: colors-name,
      weight: if header-name-bold { 700 } else { 400 },
    )
    #let body
    #if header-small-caps-for-name {
      body = [#smallcaps(it.body)]
    } else {
      body = [#it.body]
    }
    #body
    // Vertical space after the name
    #v(header-vertical-space-between-name-and-connections, weak: true)
  ]

  // Section titles:
  #show heading.where(level: 2): it => [
    #set align(left)
    #set text(size: (1em / 1.2)) // reset
    #set text(
      font: section-titles-font-family,
      size: (section-titles-font-size),
      weight: if section-titles-bold { 700 } else { 400 },
      fill: colors-section-titles,
    )
    #let section-title = (
      if section-titles-small-caps [
        #smallcaps(it.body)
      ] else [
        #it.body
      ]
    )
    // Vertical space above the section title
    #v(section-titles-vertical-space-above, weak: true)

    #block(
      breakable: false,
      width: 100%,
      [
        #if section-titles-type == "moderncv" [
          #grid(
            columns: (entries-date-and-location-width + entries-horizontal-space-between-columns, 1fr),
            column-gutter: entries-horizontal-space-between-columns,
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
          #if section-titles-type == "with-partial-line" [
            #box(width: 1fr, height: section-titles-line-thickness, fill: colors-section-titles)
          ] else if section-titles-type == "with-full-line" [
            #box[#place(
              dy: text-font-size * 0.4,
              dx: -measure(section-title).width * 1.2,
              box(width: 1fr, height: section-titles-line-thickness, fill: colors-section-titles),
            )]
          ]
        ]
      ],
    )

    // Compensation for the full line section title
    #if section-titles-type == "with-full-line" [
      #v(text-font-size * 0.4)
    ]

    // Vertical space after the section title
    #v(section-titles-vertical-space-below - 0.5em)
  ]

  // Last updated date text:
  #if page-show-last-updated-date {
    let dx = -entries-left-and-right-margin
    place(
      top + right,
      dy: -page-top-margin / 2,
      dx: dx,
      text(
        [_#last-updated-date-text _],
        fill: colors-last-updated-date-and-page-numbering,
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
        breakable: entries-allow-page-break-in-sections,
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

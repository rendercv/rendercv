
((* set page_numbering_template_placeholders = {
    "NAME": cv.name,
    "PAGE_NUMBER": "\" + str(here().page()) + \"",
    "TOTAL_PAGES": "\" + str(counter(page).final().first()) + \"",
    "TODAY": today
} *))
((* set last_updated_date_template_placeholders = {
    "TODAY": today,
} *))
#import "@preview/fontawesome:0.5.0": fa-icon

#let name = "<<cv.name|remove_typst_commands>>"
#let locale-catalog-page-numbering-style = context { "<<locale.page_numbering_template|replace_placeholders_with_actual_values(page_numbering_template_placeholders)>>" }
#let locale-catalog-last-updated-date-style = "<<locale.last_updated_date_template|replace_placeholders_with_actual_values(last_updated_date_template_placeholders)>>"
#let locale-catalog-language = "<<locale.language>>"
#let design-page-size = "<<design.page.size>>"
#let design-colors-text = <<design.colors.text.as_rgb()>>
#let design-colors-section-titles = <<design.colors.section_titles.as_rgb()>>
#let design-colors-last-updated-date-and-page-numbering = <<design.colors.last_updated_date_and_page_numbering.as_rgb()>>
#let design-colors-name = <<design.colors.name.as_rgb()>>
#let design-colors-connections = <<design.colors.connections.as_rgb()>>
#let design-colors-links = <<design.colors.links.as_rgb()>>
#let design-colors-custom = <<design.colors.custom.as_rgb()>>
#let design-section-titles-font-family = "<<design.section_titles.font_family>>"
#let design-section-titles-bold = <<design.section_titles.bold|lower>>
#let design-section-titles-line-thickness = <<design.section_titles.line_thickness>>
#let design-section-titles-font-size = <<design.section_titles.font_size>>
#let design-section-titles-type = "<<design.section_titles.type>>"
#let design-section-titles-vertical-space-above = <<design.section_titles.vertical_space_above>>
#let design-section-titles-vertical-space-below = <<design.section_titles.vertical_space_below>>
#let design-section-titles-small-caps = <<design.section_titles.small_caps|lower>>
#let design-links-use-external-link-icon = <<design.links.use_external_link_icon|lower>>
#let design-text-font-size = <<design.text.font_size>>
#let design-text-leading = <<design.text.leading>>
#let design-text-font-family = "<<design.text.font_family>>"
#let design-text-alignment = "<<design.text.alignment>>"
#let design-text-date-and-location-column-alignment = <<design.text.date_and_location_column_alignment>>
#let design-header-photo-width = <<design.header.photo_width>>
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-header-name-font-family = "<<design.header.name_font_family>>"
#let design-header-name-font-size = <<design.header.name_font_size>>
#let design-header-name-bold = <<design.header.name_bold|lower>>
#let design-header-small-caps-for-name = <<design.header.small_caps_for_name|lower>>
#let design-header-connections-font-family = "<<design.header.connections_font_family>>"
#let design-header-vertical-space-between-name-and-connections = <<design.header.vertical_space_between_name_and_connections>>
#let design-header-vertical-space-between-connections-and-first-section = <<design.header.vertical_space_between_connections_and_first_section>>
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-header-horizontal-space-between-connections = <<design.header.horizontal_space_between_connections>>
#let design-header-separator-between-connections = "<<design.header.separator_between_connections>>"
#let design-header-alignment = <<design.header.alignment>>
#let design-highlights-summary-left-margin = <<design.highlights.summary_left_margin>>
#let design-highlights-bullet = "<<design.highlights.bullet>>"
#let design-highlights-nested-bullet = "<<design.highlights.nested_bullet>>"
#let design-highlights-top-margin = <<design.highlights.top_margin>>
#let design-highlights-left-margin = <<design.highlights.left_margin>>
#let design-highlights-vertical-space-between-highlights = <<design.highlights.vertical_space_between_highlights>>
#let design-highlights-horizontal-space-between-bullet-and-highlights = <<design.highlights.horizontal_space_between_bullet_and_highlight>>
#let design-entries-vertical-space-between-entries = <<design.entries.vertical_space_between_entries>>
#let design-entries-date-and-location-width = <<design.entries.date_and_location_width>>
#let design-entries-allow-page-break-in-entries = <<design.entries.allow_page_break_in_entries|lower>>
#let design-entries-horizontal-space-between-columns = <<design.entries.horizontal_space_between_columns>>
#let design-entries-left-and-right-margin = <<design.entries.left_and_right_margin>>
#let design-page-top-margin = <<design.page.top_margin>>
#let design-page-bottom-margin = <<design.page.bottom_margin>>
#let design-page-left-margin = <<design.page.left_margin>>
#let design-page-right-margin = <<design.page.right_margin>>
#let design-page-show-last-updated-date = <<design.page.show_last_updated_date|lower>>
#let design-page-show-page-numbering = <<design.page.show_page_numbering|lower>>
#let design-links-underline = <<design.links.underline|lower>>
#let design-entry-types-education-entry-degree-column-width = <<design.entry_types.education_entry.degree_column_width>>
#let date = datetime.today()

// Metadata:
#set document(author: name, title: name + "'s CV", date: date)

// Page settings:
#set page(
  margin: (
    top: design-page-top-margin,
    bottom: design-page-bottom-margin,
    left: design-page-left-margin,
    right: design-page-right-margin,
  ),
  paper: design-page-size,
  footer: if design-page-show-page-numbering {
    text(
      fill: design-colors-last-updated-date-and-page-numbering,
      align(center, [_#locale-catalog-page-numbering-style _]),
      size: 0.9em,
    )
  } else {
    none
  },
  footer-descent: 0% - 0.3em + design-page-bottom-margin / 2,
)
// Text settings:
#let justify
#let hyphenate
#if design-text-alignment == "justified" {
  justify = true
  hyphenate = true
} else if design-text-alignment == "left" {
  justify = false
  hyphenate = false
} else if design-text-alignment == "justified-with-no-hyphenation" {
  justify = true
  hyphenate = false
}
#set text(
  font: design-text-font-family,
  size: design-text-font-size,
  lang: locale-catalog-language,
  hyphenate: hyphenate,
  fill: design-colors-text,
  // Disable ligatures for better ATS compatibility:
  ligatures: true,
)
#set par(
  spacing: 0pt,
  leading: design-text-leading,
  justify: justify,
)
#set enum(
  spacing: design-entries-vertical-space-between-entries,
)

// Highlights settings:
#let highlights(..content) = {
  list(
    ..content,
    marker: design-highlights-bullet,
    spacing: design-highlights-vertical-space-between-highlights,
    indent: design-highlights-left-margin,
    body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
  )
}
#show list: set list(
  marker: design-highlights-nested-bullet,
  spacing: design-highlights-vertical-space-between-highlights,
  indent: 0pt,
  body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
)

// Entry utilities:
#let bullet-entry(..content) = {
  list(
    ..content,
    marker: design-highlights-bullet,
    spacing: 0pt,
    indent: 0pt,
    body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
  )
}
#let three-col(
  left-column-width: 1fr,
  middle-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  middle-content: "",
  right-content: "",
  alignments: (auto, auto, auto),
) = [
  #block(
    grid(
      columns: (left-column-width, middle-column-width, right-column-width),
      column-gutter: design-entries-horizontal-space-between-columns,
      align: alignments,
      ([#set par(spacing: design-text-leading); #left-content]),
      ([#set par(spacing: design-text-leading); #middle-content]),
      ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

#let two-col(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  right-content: "",
  alignments: (auto, auto),
  column-gutter: design-entries-horizontal-space-between-columns,
) = [
  #block(
    grid(
      columns: (left-column-width, right-column-width),
      column-gutter: column-gutter,
      align: alignments,
      ([#set par(spacing: design-text-leading); #left-content]),
      ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

// Main heading settings:
#let header-font-weight
#if design-header-name-bold {
  header-font-weight = 700
} else {
  header-font-weight = 400
}
#show heading.where(level: 1): it => [
  #set par(spacing: 0pt)
  #set align(design-header-alignment)
  #set text(
    font: design-header-name-font-family,
    weight: header-font-weight,
    size: design-header-name-font-size,
    fill: design-colors-name,
  )
  #if design-header-small-caps-for-name [
    #smallcaps(it.body)
  ] else [
    #it.body
  ]
  // Vertical space after the name
  #v(design-header-vertical-space-between-name-and-connections)
]

#let section-title-font-weight
#if design-section-titles-bold {
  section-title-font-weight = 700
} else {
  section-title-font-weight = 400
}

#show heading.where(level: 2): it => [
  #set align(left)
  #set text(size: (1em / 1.2)) // reset
  #set text(
    font: design-section-titles-font-family,
    size: (design-section-titles-font-size),
    weight: section-title-font-weight,
    fill: design-colors-section-titles,
  )
  #let section-title = (
    if design-section-titles-small-caps [
      #smallcaps(it.body)
    ] else [
      #it.body
    ]
  )
  // Vertical space above the section title
  #v(design-section-titles-vertical-space-above, weak: true)
  #block(
    breakable: false,
    width: 100%,
    [
      #if design-section-titles-type == "moderncv" [
        #two-col(
          alignments: (right, left),
          left-column-width: design-entries-date-and-location-width,
          right-column-width: 1fr,
          left-content: [
            #align(horizon, box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles))
          ],
          right-content: [
            #section-title
          ]
        )

      ] else [
        #box(
          [
            #section-title
            #if design-section-titles-type == "with-partial-line" [
              #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
            ] else if design-section-titles-type == "with-full-line" [

              #v(design-text-font-size * 0.4)
              #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
            ]
          ]
        )
      ]
     ] + v(1em),
  )
  #v(-1em)
  // Vertical space after the section title
  #v(design-section-titles-vertical-space-below - 0.5em)
]

// Links:
#let original-link = link
#let link(url, body) = {
  body = [#if design-links-underline [#underline(body)] else [#body]]
  body = [#if design-links-use-external-link-icon [#body#h(design-text-font-size/4)#box(
        fa-icon("external-link", size: 0.7em),
        baseline: -10%,
      )] else [#body]]
  body = [#set text(fill: design-colors-links);#body]
  original-link(url, body)
}

// Last updated date text:
#if design-page-show-last-updated-date {
  let dx
  if design-section-titles-type == "moderncv" {
    dx = 0cm
  } else {
    dx = -design-entries-left-and-right-margin
  }
  place(
    top + right,
    dy: -design-page-top-margin / 2,
    dx: dx,
    text(
      [_#locale-catalog-last-updated-date-style _],
      fill: design-colors-last-updated-date-and-page-numbering,
      size: 0.9em,
    ),
  )
}

#let connections(connections-list) = context {
  set text(fill: design-colors-connections, font: design-header-connections-font-family)
  set par(leading: design-text-leading*1.7, justify: false)
  let list-of-connections = ()
  let separator = (
    h(design-header-horizontal-space-between-connections / 2, weak: true)
      + design-header-separator-between-connections
      + h(design-header-horizontal-space-between-connections / 2, weak: true)
  )
  let starting-index = 0
  while (starting-index < connections-list.len()) {
    let left-sum-right-margin
    if type(page.margin) == "dictionary" {
      left-sum-right-margin = page.margin.left + page.margin.right
    } else {
      left-sum-right-margin = page.margin * 4
    }

    let ending-index = starting-index + 1
    while (
      measure(connections-list.slice(starting-index, ending-index).join(separator)).width
      ((* if cv.photo *))
        < page.width - left-sum-right-margin - design-header-photo-width * 1.1
      ((* else *))
        < page.width - left-sum-right-margin
      ((* endif *))
    ) {
      ending-index = ending-index + 1
      if ending-index > connections-list.len() {
        break
      }
    }
    if ending-index > connections-list.len() {
      ending-index = connections-list.len()
    }
    list-of-connections.push(connections-list.slice(starting-index, ending-index).join(separator))
    starting-index = ending-index
  }
  align(list-of-connections.join(linebreak()), design-header-alignment)
  v(design-header-vertical-space-between-connections-and-first-section - design-section-titles-vertical-space-above)
}

#let three-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  middle-content: "",
  right-content: "",
  alignments: (left, auto, right),
) = (
  if design-section-titles-type == "moderncv" [
    #three-col(
      left-column-width: right-column-width,
      middle-column-width: left-column-width,
      right-column-width: 1fr,
      left-content: right-content,
      middle-content: [
        #block(
          [
            #left-content
          ],
          inset: (
            left: design-entries-left-and-right-margin,
            right: design-entries-left-and-right-margin,
          ),
          breakable: design-entries-allow-page-break-in-entries,
          width: 100%,
        )
      ],
      right-content: middle-content,
      alignments: (design-text-date-and-location-column-alignment, left, auto),
    )
  ] else [
    #block(
      [
        #three-col(
          left-column-width: left-column-width,
          right-column-width: right-column-width,
          left-content: left-content,
          middle-content: middle-content,
          right-content: right-content,
          alignments: alignments,
        )
      ],
      inset: (
        left: design-entries-left-and-right-margin,
        right: design-entries-left-and-right-margin,
      ),
      breakable: design-entries-allow-page-break-in-entries,
      width: 100%,
    )
  ]
)

#let two-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  right-content: "",
  alignments: (auto, design-text-date-and-location-column-alignment),
  column-gutter: design-entries-horizontal-space-between-columns,
) = (
  if design-section-titles-type == "moderncv" [
    #two-col(
      left-column-width: right-column-width,
      right-column-width: left-column-width,
      left-content: right-content,
      right-content: [
        #block(
          [
            #left-content
          ],
          inset: (
            left: design-entries-left-and-right-margin,
            right: design-entries-left-and-right-margin,
          ),
          breakable: design-entries-allow-page-break-in-entries,
          width: 100%,
        )
      ],
      alignments: (design-text-date-and-location-column-alignment, auto),
    )
  ] else [
    #block(
      [
        #two-col(
          left-column-width: left-column-width,
          right-column-width: right-column-width,
          left-content: left-content,
          right-content: right-content,
          alignments: alignments,
        )
      ],
      inset: (
        left: design-entries-left-and-right-margin,
        right: design-entries-left-and-right-margin,
      ),
      breakable: design-entries-allow-page-break-in-entries,
      width: 100%,
    )
  ]
)

#let one-col-entry(content: "") = [
  #let left-space = design-entries-left-and-right-margin
  #if design-section-titles-type == "moderncv" [
    #(left-space = left-space + design-entries-date-and-location-width + design-entries-horizontal-space-between-columns)
  ]
  #block(
    [#set par(spacing: design-text-leading); #content],
    breakable: design-entries-allow-page-break-in-entries,
    inset: (
      left: left-space,
      right: design-entries-left-and-right-margin,
    ),
    width: 100%,
  )
]

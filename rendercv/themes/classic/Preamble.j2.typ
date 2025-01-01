
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

#let name = "<<cv.name>>"
#let locale-catalog-page-numbering-style = context { "<<locale.page_numbering_template|replace_placeholders_with_actual_values(page_numbering_template_placeholders)>>" }
#let locale-catalog-last-updated-date-style = "<<locale.last_updated_date_template|replace_placeholders_with_actual_values(last_updated_date_template_placeholders)>>"
#let locale-catalog-language = "<<locale.language>>"
#let design-page-size = "<<design.page.size>>"
#let design-section-titles-font-size = <<design.section_titles.font_size>>
#let design-colors-text = <<design.colors.text.as_rgb()>>
#let design-colors-section-titles = <<design.colors.section_titles.as_rgb()>>
#let design-colors-last-updated-date-and-page-numbering = <<design.colors.last_updated_date_and_page_numbering.as_rgb()>>
#let design-colors-name = <<design.colors.name.as_rgb()>>
#let design-colors-connections = <<design.colors.connections.as_rgb()>>
#let design-colors-links = <<design.colors.links.as_rgb()>>
#let design-section-titles-bold = <<design.section_titles.bold|lower>>
#let design-section-titles-line-thickness = <<design.section_titles.line_thickness>>
#let design-section-titles-font-size = <<design.section_titles.font_size>>
#let design-section-titles-line-type = "<<design.section_titles.line_type>>"
#let design-section-titles-vertical-space-above = <<design.section_titles.vertical_space_above>>
#let design-section-titles-vertical-space-below = <<design.section_titles.vertical_space_below>>
#let design-links-use-external-link-icon = <<design.links.use_external_link_icon|lower>>
#let design-text-font-size = <<design.text.font_size>>
#let design-text-leading = <<design.text.leading>>
#let design-text-font-family = "<<design.text.font_family>>"
#let design-text-alignment = "<<design.text.alignment>>"
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-header-name-font-size = <<design.header.name_font_size>>
#let design-header-name-bold = <<design.header.name_bold|lower>>
#let design-header-vertical-space-between-name-and-connections = <<design.header.vertical_space_between_name_and_connections>>
#let design-header-vertical-space-between-connections-and-first-section = <<design.header.vertical_space_between_connections_and_first_section>>
#let design-header-use-icons-for-connections = <<design.header.use_icons_for_connections|lower>>
#let design-header-horizontal-space-between-connections = <<design.header.horizontal_space_between_connections>>
#let design-header-separator-between-connections = "<<design.header.separator_between_connections>>"
#let design-header-alignment = <<design.header.alignment>>
#let design-highlights-bullet = "<<design.highlights.bullet>>"
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
#let design-theme-specific-education-degree-width = <<design.theme_specific.education_degree_width>>
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
  marker: design-highlights-bullet,
  spacing: design-entries-vertical-space-between-entries,
  indent: 0pt,
  body-indent: design-highlights-horizontal-space-between-bullet-and-highlights,
)

// Main heading settings:
#let header-font-weight
#if design-header-name-bold {
  header-font-weight = 700
} else {
  header-font-weight = 400
}
#show heading.where(level: 1): it => [
  #set align(design-header-alignment)
  #set text(
    weight: header-font-weight,
    size: design-header-name-font-size,
    fill: design-colors-name,
  )
  #set par(spacing: 0pt)
  #it.body
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
    size: (design-section-titles-font-size),
    weight: section-title-font-weight,
    fill: design-colors-section-titles,
  )

  // Vertical space above the section title
  #v(design-section-titles-vertical-space-above, weak: true)
  #block(
    breakable: false,
    width: 100%,
    [
      #box([
        #if true [
          #it.body
        ] else [
          #smallcaps(it.body)
        ]
        #if design-section-titles-line-type == "partial" [
          #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
        ] else if design-section-titles-line-type == "full" [
          #v(-design-text-leading * 0.6)
          #box(width: 1fr, height: design-section-titles-line-thickness, fill: design-colors-section-titles)
        ]
      ])
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
  body = [#if design-links-use-external-link-icon [#body #box(
        fa-icon("external-link", size: 0.7em),
        baseline: -10%,
      )] else [#body]]
  body = [#set text(fill: design-colors-links);#body]
  original-link(url, body)
}

// Last updated date text:
#if design-page-show-last-updated-date {
  place(
    top + right,
    dy: -design-page-top-margin / 2,
    dx: -design-entries-left-and-right-margin,
    text(
      [_#locale-catalog-last-updated-date-style _],
      fill: design-colors-last-updated-date-and-page-numbering,
      size: 0.9em,
    ),
  )
}

#let connections(connections-list) = context {
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
        < page.width - left-sum-right-margin
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
  set text(fill: design-colors-connections)
  set par(leading: design-text-leading*1.7, justify: false)
  align(list-of-connections.join(linebreak()), design-header-alignment)
  v(design-header-vertical-space-between-connections-and-first-section - design-section-titles-vertical-space-above)
}

#let three-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  middle-content: "",
  right-content: "",
  alignments: (left, left, right),
) = [
  #block(
    grid(
      columns: (left-column-width, 1fr, right-column-width),
      column-gutter: design-entries-horizontal-space-between-columns,
      align: alignments,
      left-content, middle-content, ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

#let two-col-entry(
  left-column-width: 1fr,
  right-column-width: design-entries-date-and-location-width,
  left-content: "",
  right-content: "",
  alignments: (left, right),
) = [
  #block(
    grid(
      columns: (left-column-width, right-column-width),
      column-gutter: design-entries-horizontal-space-between-columns,
      align: alignments,
      left-content, ([#set par(spacing: design-text-leading); #right-content]),
    ),
    breakable: true,
    width: 100%,
  )
]

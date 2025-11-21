// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.0.1": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  entries-left-and-right-margin: 0.3cm,
  text-leading: 0.8em,
  entries-vertical-space-between-entries: 2cm,
  section-titles-vertical-space-below: 0cm,
  section-titles-vertical-space-above: 0cm,
  entries-horizontal-space-between-columns: 0.3cm,
  header-vertical-space-between-connections-and-first-section: 1cm,
  header-vertical-space-between-name-and-connections: 0.4cm,
  section-titles-type: "moderncv",
  header-separator-between-connections: "|",
  page-left-margin: 2cm,
  page-right-margin: 2cm,
)= John Doe



#connections(
  [Location],
  [#link(mailto:john.doe@example.com, john.doe@example.com, icon: false)],
  [#link(tel:+1-609-999-9995, (609) 999-9995, icon: false)],
  [#link(https://linkedin.com/in/john.doe, john.doe, icon: false)],
  [#link(https://github.com/john.doe, john.doe, icon: false)],
)== welcome\_to\_RenderCV!



[RenderCV](https://rendercv.com) is a Typst-based CV framework designed for academics and engineers, with Markdown syntax support.
Each section title is arbitrary. Each section contains a list of entries, and there are 7 different entry types to choose from.
== Education



#education-entry(
  [
    
  ],
  [
    
  ],
)
#education-entry(
  [
    
  ],
  [
    
  ],
)
== Experience



#regular-entry(
  [
    
  ],
  [
    
  ],
)
#regular-entry(
  [
    
  ],
  [
    
  ],
)
#regular-entry(
  [
    
  ],
  [
    
  ],
)
== Projects



#regular-entry(
  [
    
  ],
  [
    
  ],
)
#regular-entry(
  [
    
  ],
  [
    
  ],
)
== Skills






== Publications



#regular-entry(
  [
    
  ],
  [
    
  ],
)
== Extracurricular Activities



- There are 7 unique entry types in RenderCV: *BulletEntry*, *TextEntry*, *EducationEntry*, *ExperienceEntry*, *NormalEntry*, *PublicationEntry*, and *OneLineEntry*.
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

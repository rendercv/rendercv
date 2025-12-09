{% if section_title in design.sections.page_break_before %}
#pagebreak()

{% endif %}
== {{section_title}}
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}
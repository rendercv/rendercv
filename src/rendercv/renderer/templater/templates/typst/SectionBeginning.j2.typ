{% if design.section_titles.hidden | default(false) %}
==
{% else %}
== {{ section_title }}
{% endif %}

{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}

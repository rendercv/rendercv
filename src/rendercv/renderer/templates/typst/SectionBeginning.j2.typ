== {{section_title}}
{% if not design.entries.allow_page_break_in_sections %}
#block(
  [
{% endif %}
{% if entry_type in ["NumberedEntry", "ReversedNumberedEntry"] %}
#one-col-entry(
  content: [
  {% if entry_type == "ReversedNumberedEntry" %}
    #let rev-enum-items = (
  {% endif %}
{% endif %}

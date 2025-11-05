{{preamble}}

{{header}}

{% for section_beginning, entries, section_ending, entry_type in sections %}
{{section_beginning}}

    {% for entry in entries %}
{{entry}}
      {% if not loop.last and entry_type not in ["NumberedEntry", "ReversedNumberedEntry"] %}
#v(design-entries-vertical-space-between-entries)
      {% endif %}
    {% endfor %}

{{section_ending}}
{% endfor %}

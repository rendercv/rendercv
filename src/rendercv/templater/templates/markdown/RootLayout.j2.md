{{header}}

{% for section_beginning, entries, section_ending in sections%}
{{section_beginning}}

    {% for entry in entries %}
{{entry}}
    {% endfor %}

{{section_ending}}
{% endfor %}

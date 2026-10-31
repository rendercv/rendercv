{{ entry.main_column.splitlines()[0]|markdown_heading(level) }}

{% for line in entry.date_and_location_column.splitlines() %}
{{ line }}

{% endfor %}
{% for line in entry.main_column.splitlines()[1:] %}
{{ line }}

{% endfor %}

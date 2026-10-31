{% if cv.name %}
# {{ cv.name }}

{% endif %}
{% if cv.headline %}
{{ cv.headline }}

{% endif %}
{% for connection in cv._connections %}
- {{ connection }}
{% endfor %}

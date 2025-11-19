= {{ cv.name }}

{{ cv.label }}

#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)

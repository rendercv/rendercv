= {{ cv.name }}

{% if cv.label %}
  {{ cv.label }}
  
{% endif %}
#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)

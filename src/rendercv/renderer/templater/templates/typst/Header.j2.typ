= {{ cv.name }}

{% if cv.headline %}
  {{ cv.headline }}
  
{% endif %}
#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)

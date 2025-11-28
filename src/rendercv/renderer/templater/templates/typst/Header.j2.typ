= {{ cv.name }}

{% if cv.headline %}
  #headline([{{ cv.headline }}])
  
{% endif %}
#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)

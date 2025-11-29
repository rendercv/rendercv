{% if cv.photo %}
{% set photo = "#image(\"" + cv.photo|string + "\", width: "+ design.header.photo_width + ")" %}
#grid(
  width: ({{ design.header.photo_width }}, 1fr),
  columns: 2,
  column-gutter: 0.4cm,
  align: horizon + left,
{% if design.header.photo_position == "left" %}
  [{{ photo }}],
  [
{% else %}
  [
{% endif %}
{% endif %}
= {{ cv.name }}

{% if cv.headline %}
  #headline([{{ cv.headline }}])
  
{% endif %}
#connections(
{% for connection in cv.connections %}
  [{{ connection }}],
{% endfor %}
)
{% if cv.photo %}
{% if design.header.photo_position == "left" %}
  ]
)
{% else %}
  ],
  [{{ photo }}]
)
{% endif %}
{% endif %}
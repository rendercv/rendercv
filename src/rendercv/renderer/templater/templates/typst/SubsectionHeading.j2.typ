{% if design.subsection_titles.space_above != "0cm" %}
#v({{ design.subsection_titles.space_above }})
{% endif %}
#text(weight: "bold")[{{ subsection_title }}]
{% if design.subsection_titles.space_below != "0cm" %}
#v({{ design.subsection_titles.space_below }})
{% endif %}

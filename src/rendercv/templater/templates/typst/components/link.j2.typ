{%- if entry.doi -%}
#link("{{entry.doi_url}}")[{{entry.doi}}]
{%- elif entry.url and entry.clean_url -%}
#link("{{entry.url}}")[{{entry.clean_url}}]
{%- elif entry.url -%}
#link("{{entry.url}}")[{{entry.url|make_a_url_clean}}]
{%- endif -%}
## <<entry.company>>((* if entry.location *)), <<entry.location>>((* endif *))

((* if entry.overall_date_string *))- <<entry.overall_date_string>>
((* endif *))

### Roles

((* for role in entry.roles *))
- **<<role.position>>** (<<role.date_string_only_years>>)
((* endfor *))

((* if entry.highlights_header *))
### <<entry.highlights_header>>
((* endif *))

((* for item in entry.highlights *))
- <<item>>
((* endfor *))
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

repository_root = Path(__file__).parent.parent.parent
api_reference = repository_root / "docs" / "api_reference"
src_rendercv = repository_root / "src" / "rendercv"
nav[("src", "rendercv")] = "index.md"

# Process each Python file in the objects directory
for path in sorted(src_rendercv.rglob("*.py")):
    # Skip __init__.py files and __main__.py files
    if path.name in ("__init__.py", "__main__.py"):
        continue

    # Get the relative path from the objects directory
    module_path = path.relative_to(src_rendercv).with_suffix("")
    doc_path = module_path.with_suffix(".md")
    parts = (f"rendercv.{module_path.parts[0]}", *module_path.parts[1:])

    # Add to navigation
    nav[("src", *parts)] = doc_path.as_posix()

    # Generate the documentation page
    with mkdocs_gen_files.open(f"api_reference/{doc_path}", "w") as fd:
        module_ident = "rendercv." + ".".join(module_path.parts)
        fd.write(f"::: {module_ident}\n")

    # Set the edit path to the actual source file
    # mkdocs_gen_files.set_edit_path(full_doc_path, full_doc_path.relative_to(docs_path))


# Write the navigation file
with mkdocs_gen_files.open("api_reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

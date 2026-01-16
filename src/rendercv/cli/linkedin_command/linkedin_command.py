import re
from datetime import datetime
from pathlib import Path

import requests
import typer
import yaml
from rich.console import Console
from rich.prompt import Prompt

from ..app import app

console = Console()

# All available LinkedIn domains supported by the Member Snapshot API
AVAILABLE_DOMAINS = [
    "PROFILE",
    "EMAIL_ADDRESSES",
    "PHONE_NUMBERS",
    "POSITIONS",
    "EDUCATION",
    "SKILLS",
    "CERTIFICATIONS",
    "PROJECTS",
    "PUBLICATIONS",
    "VOLUNTEER_EXPERIENCE",
    "HONORS",
    "LANGUAGES",
    "PATENTS",
    "TEST_SCORES",
]

# Default domains to include in the CV if --custom is not used
DEFAULT_DOMAINS = [
    "PROFILE",
    "EMAIL_ADDRESSES",
    "PHONE_NUMBERS",
    "POSITIONS",
    "EDUCATION",
    "CERTIFICATIONS",
]


def parse_date(date_val, is_start_date: bool = False):
    """
    Parses LinkedIn date objects or strings into RenderCV format (YYYY-MM or YYYY).

    Args:
        date_val: The date value from LinkedIn (str or dict).
        is_start_date: If True, returns current date if missing/present (since start date cannot be 'present').
                       If False, returns 'present' (lowercase) for ongoing activities.
    """
    current_ym = datetime.now().strftime("%Y-%m")

    if not date_val or date_val == "Unknown":
        return current_ym if is_start_date else "present"

    # Handle string cases (e.g., "Jan 2025", "2003", "Present")
    if isinstance(date_val, str):
        date_str = date_val.strip()
        date_str_lower = date_str.lower()

        if date_str_lower == "present" or date_str_lower == "":
            return current_ym if is_start_date else "present"

        # Try "Month Year" format (Jan 2025) -> 2025-01
        try:
            return datetime.strptime(date_str, "%b %Y").strftime("%Y-%m")
        except ValueError:
            pass

        # Try "Year" format (2005) -> 2005
        # RenderCV accepts YYYY, so we return the string if it's exactly 4 digits
        if re.match(r"^\d{4}$", date_str):
            return date_str

        # Fallback for unparsable strings
        return current_ym if is_start_date else "present"

    # Handle Dict {year: 2020, month: 1}
    if isinstance(date_val, dict):
        y = date_val.get("year")
        m = date_val.get("month")
        if y and m:
            return f"{y}-{m:02d}"  # Return YYYY-MM
        if y:
            return str(y)  # Return YYYY

    return current_ym if is_start_date else "present"


def clean_description(desc: str) -> list[str]:
    """
    Splits description into a clean list of bullet points.
    Handles newlines and in-line bullets (e.g., 'Text. - Bullet') by forcing splits.
    """
    if not desc:
        return []

    # 1. Force split on bullets inside lines (e.g. "Pipeline by: - Ensuring")
    # Captures preceding char (letter/number/punctuation) and adds newline before bullet
    desc = re.sub(r"([a-zA-Z0-9.?!])\s*[-•*]\s+", r"\1\n", desc)

    # 2. Split by newline
    raw_lines = desc.split("\n")

    clean_lines = []
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            continue

        # 3. Remove leading bullet characters and numbering (e.g. "1. ")
        line = re.sub(r"^[-•*]\s*", "", line)
        line = re.sub(r"^\d+\.\s*", "", line)

        if line:
            clean_lines.append(line)

    return clean_lines


def fetch_linkedin_data(token: str, domains: list[str]):
    """
    Fetches member snapshot data from LinkedIn API for the specified domains.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": "202312",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    all_data = []

    console.print("\n[bold cyan]Fetching LinkedIn Data[/bold cyan]")
    console.print("=" * 50)

    for domain in domains:
        url = "https://api.linkedin.com/rest/memberSnapshotData"
        params = {"q": "criteria", "domain": domain, "start": 0, "count": 100}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                if elements:
                    all_data.extend(elements)
                    console.print(f"  ✓ {domain}: [green]{len(elements)} items[/green]")
                else:
                    console.print(f"  - {domain}: [dim]No data[/dim]")
            elif response.status_code == 403:
                console.print(
                    f"  ✗ {domain}: [yellow]Access denied (check permissions)[/yellow]"
                )
            elif response.status_code == 404:
                console.print(f"  - {domain}: [dim]Not available[/dim]")
            else:
                console.print(f"  ✗ {domain}: [red]HTTP {response.status_code}[/red]")
        except Exception as e:
            console.print(f"  ✗ {domain}: [red]Error - {e}[/red]")

    console.print("=" * 50 + "\n")
    return all_data


def linkedin_to_yaml(data):
    """Converts raw LinkedIn snapshot data to RenderCV YAML structure."""
    cv_model = {}
    cv_model["cv"] = {
        "sections": {
            "name": "Your Name",
            "location": None,
            "email": None,
            "phone": None,
            "social_networks": [],
            "sections": {},
        },
        "design": {"theme": "classic"},
    }

    for record in data:
        domain = record.get("snapshotDomain")
        elements = record.get("snapshotData", [])

        if not elements:
            continue

        # --- PROFILE ---
        if domain == "PROFILE":
            p = elements[0]
            fname = p.get("First Name") or p.get("firstName", "")
            lname = p.get("Last Name") or p.get("lastName", "")
            if fname or lname:
                cv_model["cv"]["name"] = f"{fname} {lname}".strip()

            # Try multiple location keys
            loc = (
                p.get("Geo Location")
                or p.get("locationName")
                or p.get("geoCountryName")
                or p.get("Address", "")
            )
            if loc:
                cv_model["cv"]["location"] = loc

            summary = (
                p.get("Summary")
                or p.get("summary")
                or p.get("Headline")
                or p.get("headline", "")
            )
            if summary:
                cv_model["cv"]["sections"]["summary"] = clean_description(summary)

        # --- EMAILS ---
        elif domain == "EMAIL_ADDRESSES":
            found_email = ""
            for e in elements:
                addr = e.get("Email Address") or e.get("email", "")
                # Prioritize Primary email
                if e.get("Primary") == "Yes":
                    found_email = addr
                    break
                if not found_email and addr:
                    found_email = addr

            if found_email:
                cv_model["cv"]["email"] = found_email

        # --- PHONES ---
        elif domain == "PHONE_NUMBERS":
            for ph in elements:
                num = ph.get("Number") or ph.get("Phone Number") or ph.get("number", "")
                if num:
                    cv_model["cv"]["phone"] = num
                    break

        # --- EXPERIENCE ---
        elif domain == "POSITIONS":
            experience_list = []
            for job in elements:
                company = job.get("Company Name") or job.get("companyName", "Unknown")
                title = job.get("Title") or job.get("title", "Unknown")
                desc = job.get("Description") or job.get("description", "")
                loc = job.get("Location") or job.get("locationName", "")

                # RenderCV requires location to be None if missing, not empty string
                if not loc:
                    loc = None

                start = parse_date(
                    job.get("Started On") or job.get("startDate"), is_start_date=True
                )
                end = parse_date(
                    job.get("Finished On") or job.get("endDate"), is_start_date=False
                )

                entry = {
                    "company": company,
                    "position": title,
                    "start_date": start,
                    "end_date": end,
                    "location": loc,
                    "highlights": [],
                }

                if desc:
                    entry["highlights"] = clean_description(desc)

                experience_list.append(entry)

            if experience_list:
                cv_model["cv"]["sections"]["experience"] = experience_list

        # --- EDUCATION ---
        elif domain == "EDUCATION":
            education_list = []
            for edu in elements:
                school = edu.get("School Name") or edu.get("schoolName", "")
                if not school:
                    school = "Unknown Institution"

                degree = edu.get("Degree Name") or edu.get("degreeName", "")
                notes = edu.get("Notes") or edu.get("Activities", "")

                area = degree
                if notes:
                    area += f", {notes}"

                start = parse_date(
                    edu.get("Start Date") or edu.get("startDate"), is_start_date=True
                )
                end = parse_date(
                    edu.get("End Date") or edu.get("endDate"), is_start_date=False
                )

                entry = {
                    "institution": school,
                    "area": area,
                    "start_date": start,
                    "end_date": end,
                }
                education_list.append(entry)

            if education_list:
                cv_model["cv"]["sections"]["education"] = education_list

        # --- SKILLS ---
        elif domain == "SKILLS":
            skill_list = []
            for s in elements:
                name = s.get("Name") or s.get("name") or s.get("skill", {}).get("name")
                if name:
                    skill_list.append(name)

            if skill_list:
                cv_model["cv"]["sections"]["skills"] = [
                    {"label": "Technical Skills", "details": ", ".join(skill_list)}
                ]

        # --- CERTIFICATIONS ---
        elif domain == "CERTIFICATIONS":
            cert_list = []
            for cert in elements:
                name = cert.get("Name") or cert.get("name", "Unknown")
                authority = cert.get("Authority") or cert.get("authority", "")

                # Certs usually have one date
                date = parse_date(
                    cert.get("Started On") or cert.get("startDate"), is_start_date=True
                )

                entry = {
                    "name": f"{name}" + (f" - {authority}" if authority else ""),
                    "date": date,
                }
                cert_list.append(entry)

            if cert_list:
                cv_model["cv"]["sections"]["certifications"] = cert_list

        # --- PROJECTS ---
        elif domain == "PROJECTS":
            project_list = []
            for proj in elements:
                title = proj.get("Title") or proj.get("title", "Unknown")
                desc = proj.get("Description") or proj.get("description", "")
                url = proj.get("Url") or proj.get("url", "")

                entry = {
                    "name": title,
                    "date": parse_date(
                        proj.get("Started On") or proj.get("startDate"),
                        is_start_date=True,
                    ),
                    "highlights": clean_description(desc) if desc else [],
                }
                if url:
                    entry["url"] = url

                project_list.append(entry)

            if project_list:
                cv_model["cv"]["sections"]["projects"] = project_list

        # --- PUBLICATIONS ---
        elif domain == "PUBLICATIONS":
            pub_list = []
            for pub in elements:
                entry = {
                    "title": pub.get("Name") or pub.get("title", "Unknown"),
                    "authors": [pub.get("Publisher") or "Unknown"],
                    "date": parse_date(
                        pub.get("Published On") or pub.get("date"), is_start_date=True
                    ),
                }
                if pub.get("Url") or pub.get("url"):
                    entry["url"] = pub.get("Url") or pub.get("url")
                pub_list.append(entry)

            if pub_list:
                cv_model["cv"]["sections"]["publications"] = pub_list

        # --- VOLUNTEER EXPERIENCE ---
        elif domain == "VOLUNTEER_EXPERIENCE" or domain == "VOLUNTEERING_EXPERIENCES":
            vol_list = []
            for vol in elements:
                entry = {
                    "company": vol.get("Company Name") or vol.get("company", "Unknown"),
                    "position": vol.get("Role") or vol.get("role", "Volunteer"),
                    "start_date": parse_date(
                        vol.get("Started On") or vol.get("startDate"),
                        is_start_date=True,
                    ),
                    "end_date": parse_date(
                        vol.get("Finished On") or vol.get("endDate"),
                        is_start_date=False,
                    ),
                    "highlights": [],
                }
                desc = vol.get("Description") or vol.get("description", "")
                if desc:
                    entry["highlights"] = clean_description(desc)
                vol_list.append(entry)

            if vol_list:
                cv_model["cv"]["sections"]["volunteer_experience"] = vol_list

        # --- HONORS ---
        elif domain == "HONORS":
            honors_list = []
            for honor in elements:
                entry = {
                    "name": honor.get("Title") or honor.get("title", "Unknown"),
                    "date": parse_date(
                        honor.get("Issued On") or honor.get("date"), is_start_date=True
                    ),
                }
                honors_list.append(entry)

            if honors_list:
                cv_model["cv"]["sections"]["honors_and_awards"] = honors_list

        # --- LANGUAGES ---
        elif domain == "LANGUAGES":
            lang_list = []
            for lang in elements:
                name = lang.get("Name") or lang.get("name", "")
                proficiency = lang.get("Proficiency") or lang.get("proficiency", "")
                if name:
                    lang_list.append(f"{name} ({proficiency})" if proficiency else name)

            if lang_list:
                cv_model["cv"]["sections"]["languages"] = [
                    {"label": "Languages", "details": ", ".join(lang_list)}
                ]

        # --- PATENTS ---
        elif domain == "PATENTS":
            patent_list = []
            for patent in elements:
                entry = {
                    "title": patent.get("Title") or patent.get("title", "Unknown"),
                    "authors": [patent.get("Inventors") or "Unknown"],
                    "date": parse_date(
                        patent.get("Issued On") or patent.get("date"),
                        is_start_date=True,
                    ),
                }
                if patent.get("Number"):
                    entry["journal"] = f"Patent No. {patent['Number']}"
                patent_list.append(entry)

            if patent_list:
                cv_model["cv"]["sections"]["patents"] = patent_list

        # --- TEST SCORES (Optional) ---
        elif domain == "TEST_SCORES":
            pass

    return cv_model


def get_custom_domains() -> list[str]:
    """
    Prompts user to interactively select custom domains.
    Always includes core domains (Profile, Email, Phone).
    """
    core_domains = ["PROFILE", "EMAIL_ADDRESSES", "PHONE_NUMBERS"]
    optional_domains = [d for d in AVAILABLE_DOMAINS if d not in core_domains]

    console.print("\n[bold cyan]Available LinkedIn Sections:[/bold cyan]")
    console.print(f"[dim]{', '.join(optional_domains)}[/dim]\n")

    while True:
        user_input = Prompt.ask(
            "[bold]Enter domains to include[/bold] (comma-separated)",
            default=", ".join([d for d in DEFAULT_DOMAINS if d not in core_domains]),
        )

        requested = [d.strip().upper() for d in user_input.split(",")]

        # Validate input
        invalid = [
            d for d in requested if d not in optional_domains and d not in core_domains
        ]
        if invalid:
            console.print(f"\n[red]❌ Invalid domains: {', '.join(invalid)}[/red]")
            console.print(
                f"[yellow]Please choose from: {', '.join(optional_domains)}[/yellow]\n"
            )
        else:
            return core_domains + [d for d in requested if d not in core_domains]


@app.command(
    name="linkedin",
    help=(
        "Generate a CV from your LinkedIn profile. Requires an OAuth 2.0 Access Token."
        " See the [cyan]documentation[/cyan] for instructions on how to get one."
        " Example: [yellow]rendercv linkedin[/yellow]."
    ),
)
def linkedin_command(
    token: str = typer.Option(
        ...,
        prompt="LinkedIn Access Token",
        help="OAuth 2.0 Access Token with Member Data Portability scope",
    ),
    custom: bool = typer.Option(
        False,
        "--custom",
        help="Interactively select which LinkedIn sections to include",
    ),
    output: str = typer.Option(
        "LinkedIn_CV.yaml", "--output", "-o", help="Output YAML filename"
    ),
):
    """
    Generate a CV from your LinkedIn profile.
    """

    if not token:
        console.print("[red]Error: Token is required.[/red]")
        raise typer.Exit(code=1)

    # Determine which domains to fetch
    if custom:
        domains = get_custom_domains()
    else:
        domains = DEFAULT_DOMAINS
        console.print(
            f"\n[dim]Using default sections: {', '.join([d for d in domains if d not in ['PROFILE', 'EMAIL_ADDRESSES', 'PHONE_NUMBERS']])}[/dim]"
        )

    # 1. Fetch Data
    raw_data = fetch_linkedin_data(token, domains)
    if not raw_data:
        console.print("[red]❌ No data found. Check your token and scopes.[/red]")
        raise typer.Exit(code=1)

    # 2. Parse Data
    cv_data = linkedin_to_yaml(raw_data)

    # 3. Interactive Fallback for Missing Core Info
    cv_inner = cv_data["cv"]
    console.print("\n[bold yellow]Verifying essential details...[/bold yellow]")

    if not cv_inner.get("email"):
        new_email = Prompt.ask(
            "  [yellow]?[/yellow] Email is missing. Enter it (or press Enter to skip)",
            default="",
        )
        cv_inner["email"] = new_email if new_email else None

    if not cv_inner.get("phone"):
        new_phone = Prompt.ask(
            "  [yellow]?[/yellow] Phone is missing. Enter it (or press Enter to skip)",
            default="",
        )
        cv_inner["phone"] = new_phone if new_phone else None

    if not cv_inner.get("location"):
        new_loc = Prompt.ask(
            "  [yellow]?[/yellow] Location is missing. Enter it (or press Enter to skip)",
            default="",
        )
        cv_inner["location"] = new_loc if new_loc else None

    # 4. Save to YAML
    with Path(output).open("w", encoding="utf-8") as f:
        yaml.dump(
            cv_data, f, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    sections_count = len(cv_data["cv"]["sections"])
    console.print(f"\n[bold green]✅ Successfully generated {output}![/bold green]")
    console.print(f"[dim]   Included {sections_count} sections[/dim]\n")
    console.print(f"[bold cyan]Next step:[/bold cyan] rendercv render {output}\n")

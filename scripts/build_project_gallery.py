#!/usr/bin/env python3
"""New-first, privacy-aware GitHub profile project gallery.

Sources:
- verified public repositories: GitHub public API
- pre-approved curated public descriptions: portfolio/curated_projects.json
- optional new private repositories: metadata-only token AND 'portfolio-approved' topic.
No GitHub private source links, source code, commits or secrets are rendered.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from sync_public_repos import discover as discover_public_repos

ROOT = Path(__file__).resolve().parents[1]
OWNER = "razahasnain0300-max"
START = "<!-- AUTO-PROJECT-GALLERY:START -->"
END = "<!-- AUTO-PROJECT-GALLERY:END -->"
PORT_START = "<!-- AUTO-FULL-GALLERY:START -->"
PORT_END = "<!-- AUTO-FULL-GALLERY:END -->"
APPROVED_TOPIC = "portfolio-approved"
SVG_DIR = ROOT / "assets" / "project-cards"


def plain(value, limit=160):
    return "".join(c for c in " ".join(str(value or "").split()) if ord(c) >= 32)[:limit]


def escape(value):
    return html.escape(plain(value), quote=True)


def md(value):
    return html.escape(plain(value), quote=False).replace("|", "&#124;")


def canonical(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def load_curated(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError("Invalid curated project manifest")
    if len(data["projects"]) > 80:
        raise ValueError("Gallery exceeds 80 projects")
    items, seen = [], set()
    for index, raw in enumerate(data["projects"]):
        if not isinstance(raw, dict):
            raise ValueError("Each curated project must be an object")
        title = plain(raw.get("title"), 72)
        summary = plain(raw.get("summary"), 155)
        category = plain(raw.get("category"), 48)
        image = plain(raw.get("image"), 140)
        if not title or not summary or not image.startswith("assets/previews/"):
            raise ValueError("Curated projects need approved title, summary and local preview")
        if not re.fullmatch(r"assets/previews/[a-zA-Z0-9-]+\.(?:svg|png|jpg|jpeg|webp)", image):
            raise ValueError("Invalid curated image path")
        if canonical(title) in seen:
            raise ValueError("Duplicate curated project")
        if not (ROOT / image).is_file():
            raise ValueError("Missing curated concept art: " + image)
        seen.add(canonical(title))
        website_type = plain(raw.get("website_type") or category or "Software platform", 62)
        raw_features = raw.get("features") or []
        if not isinstance(raw_features, list) or len(raw_features) > 24:
            raise ValueError("Project features must be an array of at most 24 items")
        features = [plain(x, 42) for x in raw_features if isinstance(x, str) and plain(x, 42)]
        raw_stack = raw.get("technologies") or []
        if not isinstance(raw_stack, list) or len(raw_stack) > 20:
            raise ValueError("Technologies must be an array of at most 20 entries")
        technologies = [plain(x, 36) for x in raw_stack if isinstance(x, str) and plain(x, 36)]
        short_description = plain(raw.get("short_description") or "", 155)
        description = plain(raw.get("description") or "", 360)
        preview_kind = plain(raw.get("preview_kind") or "concept", 35)
        if preview_kind not in ("concept", "real_website_screenshot"):
            raise ValueError("Unsupported preview kind")
        items.append(dict(
            title=title, summary=summary, category=category or "Software solution",
            preview_kind=preview_kind, website_type=website_type, features=features,
            technologies=technologies, short_description=short_description,
            description=description,
            image="./" + image, public_url="", is_public=False,
            date="", source="curated", order=index,
        ))
    return items


def private_approved():
    """Optional integration. Default requires no token and reveals nothing."""
    token = os.environ.get("GALLERY_PRIVATE_READ_TOKEN", "").strip()
    if not token:
        return []
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "approved-gallery-project-sync",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    items = []
    for page in range(1, 21):
        query = urlencode({"visibility":"private", "affiliation":"owner", "per_page":100, "page":page})
        req = Request("https://api.github.com/user/repos?" + query, headers=headers)
        with urlopen(req, timeout=30) as response:
            chunk = json.load(response)
        if not isinstance(chunk, list):
            raise ValueError("Unexpected private repository metadata response")
        for raw in chunk:
            topics = [str(t).lower() for t in (raw.get("topics") or [])]
            if (APPROVED_TOPIC not in topics or raw.get("private") is not True
                    or (raw.get("owner") or {}).get("login", "").lower() != OWNER):
                continue
            name = plain(raw.get("name"), 66)
            if not re.fullmatch(r"[a-zA-Z0-9_.-]+", name):
                continue
            items.append(dict(
                title=name.replace("-", " ").replace("_", " "),
                summary=plain(raw.get("description") or "Approved software project showcase", 155),
                category=plain(raw.get("language") or "Custom Software", 40),
                date=plain(raw.get("created_at") or "", 30),
                source="approved_private", is_public=False, public_url="", image="",
                repo_name=name,
            ))
        if len(chunk) < 100:
            return items
    raise ValueError("Private repository pagination limit reached")


def live_public(items):
    return [dict(
        title=plain(x["name"], 70),
        summary=plain(x["description"], 155),
        category=plain(x["language"], 40),
        date=plain(x.get("created") or "", 30),
        is_public=True, source="public", image="",
        public_url=x["link"], repo_name=x["name"],
    ) for x in items]


def merge_projects(curated, public_items, private_items=()):
    """Verified dated repos first; undated approved curated project order follows."""
    combined, used = [], set()
    recent = sorted([*public_items, *private_items],
                    key=lambda x: (x.get("date") or "", x["title"].lower()), reverse=True)
    for item in recent:
        k = canonical(item["title"])
        if k in used:
            continue
        used.add(k)
        combined.append(item)
    for item in curated:
        k = canonical(item["title"])
        if k not in used:
            used.add(k)
            combined.append(item)
    return combined


def format_date(value):
    if not value:
        return ""
    try:
        year, month, day = value[:10].split("-")
        if len(year) != 4 or len(month) != 2 or len(day) != 2:
            return ""
        import datetime
        return datetime.date(int(year),int(month),int(day)).strftime("%d %b %Y")
    except (ValueError, TypeError):
        return ""


def generated_card(item):
    """Decorative SVG card for a newly discovered, safely publishable repository."""
    key = re.sub(r"[^A-Za-z0-9_-]", "-", item.get("repo_name", "project"))[:76]
    path = "assets/project-cards/" + key + ".svg"
    title = escape(item["title"])
    short_title = escape(item["title"][:30])
    desc = escape(item["summary"][:76])
    cat = escape(item["category"])
    visibility = "PUBLIC REPOSITORY" if item["is_public"] else "APPROVED CASE STUDY"
    a = "#22D3EE" if item["is_public"] else "#A78BFA"
    art = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="476" viewBox="0 0 920 476" role="img" aria-label="{title} project showcase">
<title>{title} | Project preview</title>
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#070B14"/><stop offset="1" stop-color="#17112D"/></linearGradient><linearGradient id="a"><stop stop-color="#8B5CF6"/><stop offset="1" stop-color="#22D3EE"/></linearGradient></defs>
<rect width="920" height="476" rx="25" fill="url(#b)"/><rect x="1" y="1" width="918" height="474" rx="24" fill="none" stroke="#8B5CF6" stroke-opacity=".55"/>
<path d="M45 2 H302" stroke="url(#a)" stroke-width="5"/>
<text x="48" y="68" font-family="Arial,sans-serif" font-weight="bold" font-size="15" fill="{a}">{visibility} / {cat[:28]}</text>
<text x="48" y="151" font-family="Arial,sans-serif" font-weight="bold" font-size="43" fill="#EEF4FF">{short_title}</text>
<text x="48" y="195" font-family="Arial,sans-serif" font-size="19" fill="#94A3B8">{desc[:49]}</text>
<text x="48" y="228" font-family="Arial,sans-serif" font-size="18" fill="#94A3B8">{desc[49:98]}</text>
<rect x="447" y="104" width="427" height="302" rx="20" fill="#0C142A" stroke="{a}" stroke-opacity=".5"/>
<rect x="468" y="124" width="386" height="34" rx="8" fill="#1A2143"/>
<circle cx="489" cy="141" r="5" fill="#8B5CF6"/><circle cx="510" cy="141" r="5" fill="#22D3EE"/>
<rect x="468" y="177" width="92" height="208" rx="10" fill="#17213B"/>
<rect x="581" y="177" width="273" height="92" rx="11" fill="#19203B"/>
<rect x="581" y="285" width="123" height="100" rx="11" fill="#171E3A"/>
<rect x="719" y="285" width="135" height="100" rx="11" fill="#171E3A"/>
<path d="M602 242 L640 217 L675 228 L713 195 L758 214 L818 185" stroke="{a}" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M491 216 H536 M491 247 H530 M491 278 H537 M491 309 H521" stroke="#8B5CF6" stroke-opacity=".64" stroke-width="8" stroke-linecap="round"/>
<text x="48" y="446" font-family="Arial,sans-serif" fill="#98A5C1" font-size="14">PROJECT OVERVIEW · SOURCE PRIVACY RESPECTED</text></svg>
'''
    return path, art


def card_text(item, link_images=True):
    """GitHub-safe professional card: real image, business category, icon features and tech tags.

    Curated public website screenshots are NEVER hyperlinks. Public source links
    are only generated for actually public repositories.
    """
    path = item["image"].lstrip("./")
    image = f'<img src="./{path}" width="100%" alt="{escape(item["title"])} website or project showcase"/>'
    if item["is_public"] and item["public_url"] and link_images:
        image = f'<a href="{html.escape(item["public_url"], quote=True)}">{image}</a>'
    date = format_date(item.get("date"))
    screenshot = item.get("preview_kind") == "real_website_screenshot"
    kind = ("REAL PUBLIC WEBSITE PREVIEW" if screenshot else
            "PUBLIC REPOSITORY" if item["is_public"] else
            "APPROVED PROJECT" if item["source"] == "approved_private" else
            "ILLUSTRATIVE PORTFOLIO CONCEPT")
    when = (" · Created " + date) if date else ""
    title = escape(item["title"])
    project_type = escape(item.get("website_type") or item.get("category") or "Software")
    summary = escape(item.get("short_description") or item.get("summary") or "")
    features = [escape(x) for x in item.get("features", [])][:8]
    technologies = [escape(x) for x in item.get("technologies", [])][:6]
    details = (
        f'<br/><sub><b>{escape(kind)}</b>{escape(when)}</sub>'
        f'<br/><strong>{title}</strong>'
        f'<br/><sub><b>🏷️ {project_type}</b></sub>'
        f'<br/><sub>{summary}</sub>'
    )
    if features:
        details += '<br/><sub><b>✨ FEATURES</b></sub><br/>' + " ".join(
            '<code>' + f + '</code>' for f in features
        )
    if technologies:
        details += '<br/><sub><b>⚙️ BUILT WITH</b></sub><br/>' + " ".join(
            '<code>' + tech + '</code>' for tech in technologies
        )
    return image + details

def table(items):
    if not items:
        return "No projects are approved for display yet."
    lines = ["<table>"]
    for i in range(0, len(items), 2):
        lines.append("<tr>")
        for item in items[i:i+2]:
            lines.append('<td width="50%" align="center" valign="top">' + card_text(item) + "</td>")
        if len(items[i:i+2]) == 1:
            lines.append('<td width="50%" valign="top"></td>')
        lines.append("</tr>")
    lines.append("</table>")
    return "\n".join(lines)


def block(items, full=False):
    count = len(items)
    public_count = sum(x["is_public"] for x in items)
    if full:
        return "\n".join([
            PORT_START,
            "## Project gallery · Newest first",
            "",
            f"**{count} showcased projects** · {public_count} public-source repositories · "
            f"{count-public_count} approved private-source previews",
            "",
            "Newest discoverable repositories appear first. The remaining private-source projects "
            "follow an intentionally curated order; their exact creation dates are not publicly verified.",
            "",
            table(items),
            "",
            "New public repositories appear at the next hourly GitHub Action refresh. "
            "New private projects require individual permission before their metadata can be shown.",
            PORT_END,
        ])
    first = items[:8]
    new_count = len([x for x in items if x["source"]!="curated"])
    return "\n".join([
        START,
        "## Our latest software projects",
        "",
        f"**{count} showcased projects** · Latest additions first · "
        "Live public-repository discovery",
        "",
        '<div align="center">',
        '<img src="./assets/project-gallery-header.svg" width="100%" alt="Latest team software projects, automatically indexed, with new projects featured first"/>',
        "</div>",
        "",
        table(first),
        "",
        f"**[Explore all {count} projects and case studies →](./PORTFOLIO.md)**",
        "",
        "*Project count is generated from public repositories and approved showcases; "
        "it is not a claim about undisclosed private projects. Public repositories refresh hourly. "
        "Private sources are not linked.*",
        END,
    ])


def swap(source, first_marker, last_marker, content):
    if source.count(first_marker) != 1 or source.count(last_marker) != 1:
        raise ValueError("Missing or duplicate managed project-gallery marker")
    a = source.index(first_marker)
    b = source.index(last_marker, a) + len(last_marker)
    return source[:a] + content + source[b:]


def generate(public=None, private=None):
    featured = load_curated(ROOT / "portfolio" / "curated_projects.json")
    public = live_public(discover_public_repos() if public is None else public)
    private = private_approved() if private is None else private
    items = merge_projects(featured, public, private)
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        if not item["image"]:
            path, card = generated_card(item)
            (ROOT / path).write_text(card, encoding="utf-8")
            item["image"] = "./" + path
    readme_path = ROOT / "README.md"
    portfolio_path = ROOT / "PORTFOLIO.md"
    original_readme = readme_path.read_text(encoding="utf-8")
    original_portfolio = portfolio_path.read_text(encoding="utf-8")
    readme_path.write_text(swap(original_readme, START, END, block(items)), encoding="utf-8")
    portfolio_path.write_text(swap(original_portfolio, PORT_START, PORT_END, block(items, full=True)), encoding="utf-8")
    return len(items), len(public), len(private)


if __name__ == "__main__":
    c, public, private = generate()
    print(f"Portfolio: {c} showcases; {public} public repos, {private} opted-in private repos discovered.")

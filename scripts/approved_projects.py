"""Opt-in public case studies. Does not access private GitHub APIs."""
import json
import html
import hashlib
from pathlib import Path
from urllib.parse import urlparse

OPEN = "<!-- APPROVED-CASESTUDIES:START -->"
CLOSE = "<!-- APPROVED-CASESTUDIES:END -->"


def clean(value, limit=140):
    return " ".join(str(value or "").split())[:limit]


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError("Expected projects array")
    if len(data["projects"]) > 50:
        raise ValueError("Maximum 50 approved projects")
    results = []
    seen = set()
    for raw in data["projects"]:
        if not isinstance(raw, dict) or raw.get("approved_for_public_profile") is not True:
            continue
        if any(field in raw for field in ("private_repo", "private_repository_url",
                                          "repository_slug", "token", "secret", "api_key")):
            raise ValueError("Private identifiers and credentials are prohibited")
        name = clean(raw.get("public_title"), 56)
        description = clean(raw.get("public_summary"), 130)
        tech = clean(raw.get("technologies") or "Software solutions", 65)
        category = clean(raw.get("category") or "Custom Software", 40)
        link = clean(raw.get("public_demo_url") or "", 200)
        if not name or not description or name.lower() in seen:
            raise ValueError("Approved entries need unique public titles and summaries")
        if link:
            u = urlparse(link)
            if (u.scheme != "https" or not u.hostname or u.username or u.password or
                    u.hostname.lower() in {"github.com", "api.github.com", "raw.githubusercontent.com",
                                           "localhost", "127.0.0.1"}):
                raise ValueError("Demo link must be public HTTPS, not private GitHub source")
        seen.add(name.lower())
        results.append({"name": name, "description": description, "tech": tech,
                        "category": category, "link": link})
    return sorted(results, key=lambda r: r["name"].lower())


def card_svg(items):
    if not items:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" viewBox="0 0 1 1"/>\n'
    rows = (min(6, len(items)) + 1) // 2
    height = 155 + rows * 144
    esc = lambda v: html.escape(clean(v), quote=True)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}">',
        '<title>Approved software project showcases</title>',
        '<rect width="1120" height="' + str(height) + '" rx="20" fill="#070B14"/>',
        '<rect x="1" y="1" width="1118" height="' + str(height-2) +
        '" rx="19" fill="none" stroke="#8B5CF6" stroke-opacity=".7"/>',
        '<text x="43" y="48" font-size="14" fill="#22D3EE">APPROVED PROJECT SHOWCASE</text>',
        '<text x="43" y="98" font-size="34" font-weight="bold" fill="#EAF2FF">Software work shared with permission.</text>',
        '<text x="43" y="128" font-size="16" fill="#94A3B8">Private source code and credentials are never published.</text>',
    ]
    for i, item in enumerate(items[:6]):
        x, y = 44 + (i % 2)*536, 150 + (i // 2)*144
        accent = "#22D3EE" if i%2 else "#8B5CF6"
        parts.extend([
            f'<rect x="{x+6}" y="{y+8}" width="501" height="124" rx="14" fill="#040615"/>',
            f'<rect x="{x}" y="{y}" width="501" height="124" rx="14" fill="#101A2E" stroke="{accent}" stroke-opacity=".6"/>',
            f'<text x="{x+17}" y="{y+30}" fill="{accent}" font-size="12">APPROVED / {esc(item["category"])}</text>',
            f'<text x="{x+17}" y="{y+65}" fill="#EAF2FF" font-size="21" font-weight="bold">{esc(item["name"][:32])}</text>',
            f'<text x="{x+17}" y="{y+95}" fill="#94A3B8" font-size="14">{esc(item["description"][:64])}</text>',
        ])
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def apply(readme, projects):
    if readme.count(OPEN) != 1 or readme.count(CLOSE) != 1:
        raise ValueError("Missing approved-project markers in README")
    svg = card_svg(projects)
    if not projects:
        body = OPEN + "\n" + CLOSE
    else:
        digest = hashlib.sha256(svg.encode()).hexdigest()[:10]
        lines = [
            OPEN,
            "## Newly approved project showcases",
            "",
            "These case-study details were approved for public display. The source repositories remain private.",
            "",
            '<div align="center">',
            f'<img src="./assets/approved-case-studies.svg?v={digest}" width="100%" alt="Approved client-safe case studies"/>',
            "</div>", "",
            "| Project | Scope | Technologies |", "|:--|:--|:--|",
        ]
        def md(value):
            s = html.escape(clean(value), quote=False)
            for c in ("\\", "|", "[", "]", "*", "_", chr(96)):
                s = s.replace(c, "\\"+c)
            return s
        for p in projects:
            title = md(p["name"])
            if p["link"]:
                title = "["+title+"]("+p["link"]+")"
            lines.append("| **"+title+"** | "+md(p["description"])+" | "+md(p["tech"])+" |")
        lines += ["", CLOSE]
        body = "\n".join(lines)
    a = readme.index(OPEN)
    z = readme.index(CLOSE, a) + len(CLOSE)
    return readme[:a] + body + readme[z:], svg

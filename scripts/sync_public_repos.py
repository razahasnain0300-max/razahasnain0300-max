#!/usr/bin/env python3
"""Synchronize public GitHub repositories into a client-facing profile."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode, quote
from approved_projects import load as load_approved, apply as apply_approved
from urllib.request import Request, urlopen

OWNER = "razahasnain0300-max"
ROOT = Path(__file__).resolve().parents[1]
START = "<!-- PUBLIC-REPO-AUTO:START -->"
END = "<!-- PUBLIC-REPO-AUTO:END -->"


def text(value, limit=160):
    return " ".join(str(value or "").split())[:limit]


def md(value):
    s = html.escape(text(value), quote=False)
    for ch in "|[]":
        s = s.replace(ch, "\\" + ch)
    return s


def safe_repos(items):
    result = {}
    for r in items:
        if not isinstance(r, dict) or r.get("private") is not False or r.get("visibility", "public") != "public":
            continue
        if (r.get("owner") or {}).get("login", "").lower() != OWNER.lower():
            continue
        name = text(r.get("name"), 99)
        if name == OWNER or not re.fullmatch(r"[a-zA-Z0-9_.-]+", name):
            continue
        result[name.lower()] = {
            "name": name,
            "link": "https://github.com/" + OWNER + "/" + quote(name, safe="-._"),
            "description": text(r.get("description") or "Public repository", 160),
            "language": text(r.get("language") or "Project", 45),
            "created": text(r.get("created_at"), 40),
        }
    return sorted(result.values(), key=lambda r: (r["created"], r["name"]), reverse=True)


def discover():
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-public-repo-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    collected = []
    for page in range(1, 21):
        query = urlencode({"type": "owner", "per_page": 100, "page": page})
        request = Request("https://api.github.com/users/" + OWNER + "/repos?" + query, headers=headers)
        with urlopen(request, timeout=25) as response:
            chunk = json.load(response)
        if not isinstance(chunk, list):
            raise ValueError("Unexpected GitHub repositories response")
        collected.extend(chunk)
        if len(chunk) < 100:
            return safe_repos(collected)
    raise ValueError("Repository count exceeds configured pagination")


def make_svg(repos):
    shown = repos[:6]
    rows = max(1, (len(shown) + 1) // 2)
    height = 151 + rows * 145
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="' + str(height) +
           '" viewBox="0 0 1120 ' + str(height) + '" role="img" aria-label="Automatically updated public repository showcase">',
           '<title>Public GitHub repository showcase</title>',
           '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#070B14"/><stop offset=".5" stop-color="#0B1020"/><stop offset="1" stop-color="#070B14"/></linearGradient>',
           '<linearGradient id="edge"><stop stop-color="#8B5CF6"/><stop offset=".5" stop-color="#22D3EE"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient>',
           '<style>text{font-family:Arial,sans-serif}.float{animation:levitate 7s ease-in-out infinite}@keyframes levitate{0%,100%{opacity:1}50%{opacity:.82}}@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style></defs>',
           '<rect width="1120" height="' + str(height) + '" rx="20" fill="url(#bg)"/>',
           '<rect x="1" y="1" width="1118" height="' + str(height - 2) + '" rx="19" fill="none" stroke="#8B5CF6" stroke-opacity=".5"/>',
           '<rect x="40" width="190" height="3" fill="url(#edge)"/>',
           '<text x="42" y="48" font-size="14" fill="#22D3EE">AUTO-SYNC  /  PUBLIC REPOSITORY RADAR</text>',
           '<text x="42" y="95" font-size="37" font-weight="bold" fill="#EAF2FF">New projects, automatically featured.</text>',
           '<text x="42" y="127" font-size="16" fill="#94A3B8">Purple + cyan design. Real GitHub metadata. Private projects remain private.</text>']
    if not shown:
        out.extend(['<rect x="42" y="154" width="1036" height="115" rx="17" fill="#111B2E" stroke="#8B5CF6" stroke-opacity=".5"/>',
                    '<text x="66" y="202" font-size="22" font-weight="bold" fill="#EAF2FF">Your next public repository will appear here.</text>',
                    '<text x="66" y="236" font-size="16" fill="#94A3B8">The profile currently has no additional public repositories.</text>'])
    for i, item in enumerate(shown):
        x, y = 41 + (i % 2) * 536, 151 + (i // 2) * 145
        color = "#8B5CF6" if i % 2 == 0 else "#22D3EE"
        name = html.escape(item["name"][:32], quote=True)
        language = html.escape(item["language"][:28], quote=True)
        description = html.escape(item["description"][:63], quote=True)
        out.extend([
            '<g class="float">',
            '<rect x="' + str(x+6) + '" y="' + str(y+8) + '" width="501" height="123" rx="15" fill="#03050D"/>',
            '<rect x="' + str(x) + '" y="' + str(y) + '" width="501" height="123" rx="15" fill="#101A2E" stroke="' + color + '" stroke-opacity=".65"/>',
            '<text x="' + str(x+19) + '" y="' + str(y+31) + '" font-size="12" fill="' + color + '">PUBLIC / ' + language + '</text>',
            '<text x="' + str(x+19) + '" y="' + str(y+65) + '" font-size="22" font-weight="bold" fill="#EAF2FF">' + name + '</text>',
            '<text x="' + str(x+19) + '" y="' + str(y+94) + '" font-size="14" fill="#94A3B8">' + description + '</text>',
            '</g>'])
    out.append("</svg>")
    return "\n".join(out) + "\n"


def make_block(repos, svg_version):
    lines = [
        START,
        "## Latest public project previews · Automatically updated",
        "",
        '<div align="center">',
        '<img src="./assets/auto-repos.svg?v=' + svg_version + '" width="100%" alt="Auto-updated purple and cyan public repository cards"/>',
        "</div>",
        "",
    ]
    if repos:
        lines.extend(["| Project | Main language | Focus |", "|:--|:--|:--|"])
        for r in repos[:8]:
            lines.append("| **" + md(r["name"]) + "** | " +
                         md(r["language"]) + " | " + md(r["description"]) + " |")
    else:
        lines.append("There are no additional **public** repositories currently. New public repositories will appear automatically after the next sync.")
    lines.extend(["", "Project cards above show previews only.",
                  "", "*Updated approximately hourly. Project cards do not link to source code. Private repositories remain protected.*", END])
    return "\n".join(lines)


def make_index(repos):
    parts = ["# Automatically Synced Public Repositories", "",
             "[← Main Profile](./README.md) · [Curated Portfolio](./PORTFOLIO.md)", "",
             "This index automatically refreshes from public GitHub repository metadata. Private repository names and descriptions are excluded.",
             ""]
    if repos:
        parts += ["| Project | Main language | Description |", "|:--|:--|:--|"]
        for r in repos:
            parts.append("| **" + md(r["name"]) + "** | " +
                         md(r["language"]) + " | " + md(r["description"]) + " |")
    else:
        parts.append("No additional public repositories. The profile repository itself is intentionally excluded.")
    return "\n".join(parts) + "\n"


def main():
    repos = discover()
    svg = make_svg(repos)
    digest = hashlib.sha256(svg.encode()).hexdigest()[:10]
    readme_path = ROOT / "README.md"
    old = readme_path.read_text(encoding="utf-8")
    if old.count(START) != 1 or old.count(END) != 1:
        raise ValueError("Expected exactly one protected repository-sync section")
    begin = old.index(START)
    finish = old.index(END, begin) + len(END)
    next_readme = old[:begin] + make_block(repos, digest) + old[finish:]
    approved_items = load_approved(ROOT / "portfolio" / "approved_private_projects.json")
    next_readme, approved_art = apply_approved(next_readme, approved_items)
    (ROOT / "assets" / "auto-repos.svg").write_text(svg, encoding="utf-8")
    (ROOT / "AUTO_REPOSITORIES.md").write_text(make_index(repos), encoding="utf-8")
    (ROOT / "assets" / "approved-case-studies.svg").write_text(approved_art, encoding="utf-8")
    readme_path.write_text(next_readme, encoding="utf-8")
    print("Synchronized", len(repos), "public repositories; private repositories not fetched.")


if __name__ == "__main__":
    main()

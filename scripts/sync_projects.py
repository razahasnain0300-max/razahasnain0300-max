#!/usr/bin/env python3
"""Build public-repository showcase cards without modifying hand-curated projects."""
import html
import json
import os
import re
import urllib.request
from pathlib import Path

OWNER = "razahasnain0300-max"
PROFILE_REPO = OWNER
ROOT = Path(__file__).resolve().parents[1]
START = "<!-- AUTO-PROJECTS:START -->"
END = "<!-- AUTO-PROJECTS:END -->"
LIMIT = 5
API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")

def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "SyedsTech-Portfolio-Automation"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)

def clean(s, maximum=180):
    return html.escape(str(s or "").strip()[:maximum], quote=True)

def get_repos():
    repos = []
    for page in range(1, 11):
        batch = get_json(f"{API}/users/{OWNER}/repos?type=owner&sort=updated&per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return [r for r in repos if not r.get("private") and not r.get("fork") and not r.get("archived") and r["name"] != PROFILE_REPO and not r["name"].startswith(".")]

def svg_card(repo, index):
    name = clean(repo["name"].replace("-", " ").replace("_", " ").title(), 52)
    description = clean(repo.get("description") or "Explore the repository, architecture and source code.", 86)
    tech = clean(repo.get("language") or "Software Engineering", 28)
    number = f"{index:02d}"
    # XML-safe text; no unescaped ampersands or custom web fonts required.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#040E09"/><stop offset="1" stop-color="#10281A"/></linearGradient><linearGradient id="accent"><stop stop-color="#B6FF2A"/><stop offset="1" stop-color="#20C95C"/></linearGradient><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#346044" stroke-opacity=".20"/></pattern></defs>
<rect width="1000" height="300" rx="22" fill="url(#bg)"/><rect width="1000" height="300" rx="22" fill="url(#grid)"/>
<rect x="12" y="12" width="976" height="276" rx="18" fill="none" stroke="url(#accent)" stroke-width="2"/>
<text x="48" y="63" font-family="Arial,sans-serif" font-size="17" letter-spacing="3" fill="#B6FF2A">SYEDSTECH / AUTO-SYNCED PROJECT {number}</text>
<text x="48" y="125" font-family="Georgia,serif" font-weight="bold" font-size="43" fill="#F7FFF7">{name}</text>
<text x="48" y="170" font-family="Arial,sans-serif" font-size="20" fill="#B6FF2A">{tech}</text>
<text x="48" y="216" font-family="Arial,sans-serif" font-size="18" fill="#C6DCCB">{description}</text>
<text x="48" y="260" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="#B6FF2A">VIEW REPOSITORY  &#8594;</text>
<path d="M855 55L920 120L855 185" fill="none" stroke="#45D967" stroke-width="14" opacity=".3"/>
</svg>'''

def main():
    repos = get_repos()
    # Keep hand-curated projects intact; auto cards are for new public repositories.
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    # Existing projects are represented by their public repository names in the README.
    curated = readme.split(START)[0]
    selected = []
    for repo in repos:
        name = repo["name"]
        # Only skip projects already linked explicitly in the curated section.
        if f"github.com/{OWNER}/{name}" in curated:
            continue
        selected.append(repo)
    output = ROOT / "assets" / "auto-projects"
    output.mkdir(parents=True, exist_ok=True)
    existing = set(output.glob("*.svg"))
    generated = set()
    lines = ["### Automatically synced public repositories", "",
             "Premium cards are generated from public GitHub repository metadata. Descriptions and technologies reflect repository metadata, not independently verified deployments.", ""]
    for i, repo in enumerate(selected, 1):
        name = repo["name"]
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
        path = output / f"{slug}.svg"
        path.write_text(svg_card(repo, i), encoding="utf-8")
        generated.add(path)
        if (i - 1) % LIMIT == 0 and i > 1:
            lines.append("<details>")
            lines.append(f"<summary><b>LOAD MORE PROJECTS — Show projects {i}–{min(i+LIMIT-1, len(selected))}</b></summary>")
            lines.append("")
        title = clean(name.replace("-", " ").replace("_", " ").title())
        url = repo["html_url"]
        lines.append(f'[![{title} premium project card](https://raw.githubusercontent.com/{OWNER}/{PROFILE_REPO}/main/assets/auto-projects/{slug}.svg)]({url})')
        lines.append("")
        lines.append(f"**[{title}]({url})** · {clean(repo.get('language') or 'Software')} · [Source code]({url})")
        lines.append("")
        if i % LIMIT == 0 and i > LIMIT:
            lines.append("</details>")
            lines.append("")
    if len(selected) > LIMIT and len(selected) % LIMIT:
        lines.extend(["</details>", ""])
    if not selected:
        lines.append("New public repositories will appear here automatically.")
    section = START + "\n" + "\n".join(lines) + "\n" + END
    if START in readme and END in readme:
        readme = readme[:readme.index(START)] + section + readme[readme.index(END)+len(END):]
    else:
        marker = '<table><tr><td width="100%" bgcolor="#07120B"><h2><font color="#8EFF24">04 / Delivery process</font>'
        idx = readme.find(marker)
        if idx < 0:
            idx = len(readme)
        readme = readme[:idx] + "\n\n" + section + "\n\n" + readme[idx:]
    readme_path.write_text(readme, encoding="utf-8")
    for path in existing - generated:
        path.unlink()
    print(f"Generated {len(selected)} premium cards")

if __name__ == "__main__":
    main()

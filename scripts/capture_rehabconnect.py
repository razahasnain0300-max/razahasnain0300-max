#!/usr/bin/env python3
"""Capture APPROVED PUBLIC RehabConnect webpages as real, non-linked portfolio images.

Only fixed public routes on rehabconnect.pk. No forms, login, admin or patient pages.
Source software repo and website production deployment are never modified.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "previews"
PROFILE = ROOT / "PORTFOLIO.md"
MANIFEST = ROOT / "portfolio" / "curated_projects.json"
BASE = "https://rehabconnect.pk/"
START = "<!-- REHABCONNECT-PUBLIC-PAGES:START -->"
END = "<!-- REHABCONNECT-PUBLIC-PAGES:END -->"
ROUTES = [
    ("home", "/", "Homepage", True),
    ("finder", "/get-help", "Find Help — Care Finder", False),
    ("rehabs", "/rehabs", "Rehabilitation Directory", False),
    ("professionals", "/professionals", "Healthcare Professionals", False),
    ("research", "/research", "Research & Insights", False),
    ("resources", "/resources", "Resources & Guides", False),
    ("facilities", "/for-facilities", "For Treatment Facilities", False),
    ("doctors", "/for-professionals", "For Professionals", False),
    ("compare", "/compare-centres", "Compare Rehab Centres", False),
    ("family", "/family-support", "Family Support", False),
    ("blog", "/blog", "Articles & Blogs", False),
    ("about", "/about", "About RehabConnect", False),
    ("matcher", "/care-matcher", "Care Matcher", False),
]
# User explicitly approved these public pages for screenshot display.
MAX_PAGES = 10
MIN_PAGES = 4

# Public-safe, verified project descriptors. Do not add patient or staff records.
PROJECT_TYPE = "Healthcare Directory · Rehab Finder · Facility Operations"
PROJECT_SUMMARY = "Rehab and mental-health discovery platform with smart search, centre comparison, research and facility tools"
PROJECT_SHORT = "Find rehabilitation centres and mental-health professionals, compare services and access recovery resources."
PROJECT_DESCRIPTION = (
    "A multi-portal healthcare discovery and facility-operations platform. "
    "Public pages offer rehabilitation and professional directories, city/town search, "
    "centre comparisons and mental-health resources. Separate private tools "
    "support facility staff and admission workflows."
)
TECHNOLOGIES = ["React","TypeScript","TanStack Start","Node.js","Express","MySQL","Tailwind CSS"]
PUBLIC_FEATURES = [
    "🏥 Rehab Centre Directory",
    "🩺 Professional Profiles",
    "🔎 Smart Care Finder",
    "📍 City & Town Filters",
    "⚖️ Centre Comparison",
    "🧭 Care Matcher",
    "📚 Recovery Resources",
    "🧪 Research & Insights",
    "👨‍👩‍👧 Family Support",
    "📝 Health Articles",
    "🏢 Facility Onboarding",
    "📅 Appointment Flows",
    "💻 Responsive Web Platform"
]
OPERATIONS_FEATURES = [
    "🔐 Role-Based Admin",
    "🛏️ Inpatient Management",
    "📊 Facility Reporting",
    "👥 Staff Portals",
    "🗂️ Content Management"
]
FEATURES = PUBLIC_FEATURES + OPERATIONS_FEATURES

BLOCKED = ("/admin", "/patient", "/provider/", "/login", "/register",
           "/booking", "/dashboard", "/api/", "/checkout", "/account")


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(p), size)


def target_url(path):
    if not path.startswith("/") or path.startswith("//") or "?" in path or "#" in path:
        raise ValueError("Only static, approved public routes are permitted")
    url = urljoin(BASE, path.lstrip("/"))
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname != "rehabconnect.pk"
            or any(block in parsed.path.lower() for block in BLOCKED)):
        raise ValueError("Unsafe or non-public URL")
    return url


def valid_screenshot(path):
    with Image.open(path) as pic:
        pic.verify()
    with Image.open(path) as pic:
        if pic.width < 1100 or pic.height < 650:
            raise ValueError("Screenshot is too small")
        rgb = pic.convert("RGB").resize((128, 90))
        if max(ImageStat.Stat(rgb).stddev) < 8:
            raise ValueError("Screenshot appears blank or almost uniform")


def capture():
    shots = {}
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1440, "height": 900}, device_scale_factor=1,
            color_scheme="light", reduced_motion="reduce", locale="en-US",
            timezone_id="Asia/Karachi", service_workers="block"
        )
        page = context.new_page()
        page.set_default_timeout(15000)
        for slug, route, title, required in ROUTES:
            if len(shots) >= MAX_PAGES:
                break
            try:
                url = target_url(route)
                response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                if response is None or response.status >= 400:
                    raise ValueError(f"Unsuccessful response {response.status if response else 'none'}")
                target = urlparse(page.url)
                if target.hostname not in ("rehabconnect.pk", "www.rehabconnect.pk"):
                    raise ValueError("Redirect off approved website")
                if any(bad in target.path.lower() for bad in BLOCKED):
                    raise ValueError("Redirect into an inappropriate page")
                page.wait_for_timeout(2400)
                try:
                    page.evaluate("() => document.fonts.ready")
                except Exception:
                    pass
                visible = " ".join(page.locator("body").inner_text(timeout=10000).split())
                heading = page.locator("h1").count()
                if (len(visible) < 180 and not heading) or any(
                    failure in page.title().lower()
                    for failure in ("404", "not found", "just a moment", "access denied", "error 5")
                ):
                    raise ValueError("Page content incomplete or error response")
                tmp = OUT / ("_tmp-rehabconnect-" + slug + ".png")
                page.screenshot(path=str(tmp), full_page=False, animations="disabled")
                valid_screenshot(tmp)
                shots[slug] = tmp
                print(f"CAPTURED: {title} HTTP {response.status}", flush=True)
            except Exception as exc:
                print(f"SKIPPED: {title} - {type(exc).__name__}: {str(exc)[:180]}", flush=True)
                if required:
                    raise
        browser.close()
    if len(shots) < MIN_PAGES:
        raise RuntimeError(f"Only {len(shots)} quality public pages captured; refusing an incomplete gallery")
    return shots


def picture_frame(raw, title, destination):
    """Real page screenshot with only a small branded browser-style frame."""
    output = Image.new("RGB", (1280, 795), "#081020")
    d = ImageDraw.Draw(output)
    d.rounded_rectangle((11, 11, 1269, 784), radius=21,
                        outline="#7e59d8", fill="#10182e", width=3)
    d.rectangle((39, 31, 270, 35), fill="#22d3ee")
    d.text((42, 48), "REHABCONNECT.PK", font=font(27, True), fill="#eef5ff")
    d.text((42, 92), title + " / Actual public website screenshot",
           font=font(18), fill="#22d3ee")
    with Image.open(raw) as src:
        # Scale the real 1440×900 viewport to fit. Do not replace real UI with mockups.
        snap = src.convert("RGB").resize((1194, 638), Image.Resampling.LANCZOS)
        output.paste(snap, (43, 137))
    d.rounded_rectangle((42, 136, 1238, 776), radius=8,
                        outline="#4a5788", width=2)
    output.save(destination, "WEBP", quality=87, method=6)
    valid_screenshot(destination)


def build_hero(shots):
    """Premium preview: ONLY genuine public screenshots, with branded feature labels."""
    hero = Image.new("RGB", (1280, 916), "#080d1b")
    d = ImageDraw.Draw(hero)
    d.rounded_rectangle((9, 9, 1271, 907), radius=23,
                        fill="#11172d", outline="#8b5cf6", width=3)
    d.rectangle((42, 30, 273, 35), fill="#22d3ee")
    d.text((45, 51), "REHABCONNECT.PK", font=font(30, True), fill="#f0f5ff")
    d.text((45, 101), "Healthcare discovery  /  Rehab & professional search",
           font=font(18), fill="#adebf4")
    d.rounded_rectangle((1000, 63, 1233, 103), radius=12,
                        fill="#1d2443", outline="#665aa8", width=2)
    d.text((1022, 74), "REAL SITE PREVIEW", font=font(15, True), fill="#d5c6ff")
    with Image.open(shots["home"]) as image:
        actual_home = image.convert("RGB")
        large = ImageOps.fit(actual_home, (1186, 465),
                             method=Image.Resampling.LANCZOS,
                             centering=(.5, .12))
        hero.paste(large, (47, 141))
    d.rectangle((47, 141, 1233, 607), outline="#6454a1", width=2)
    thumbnail_labels = {
        "finder": "CARE FINDER", "rehabs": "REHAB DIRECTORY",
        "professionals": "PROFESSIONALS", "research": "RESEARCH",
        "resources": "RESOURCES", "compare": "COMPARE CENTRES",
        "family": "FAMILY SUPPORT",
    }
    picks = [slug for slug in ("finder", "rehabs", "professionals", "compare", "research")
             if slug in shots][:3]
    for i, slug in enumerate(picks):
        x = 47 + i * 403
        with Image.open(shots[slug]) as image:
            thumb = ImageOps.fit(image.convert("RGB"), (379, 125),
                                 method=Image.Resampling.LANCZOS,
                                 centering=(.5, .12))
            hero.paste(thumb, (x, 626))
        d.rectangle((x, 626, x + 379, 751), outline="#4b6492", width=2)
        d.rounded_rectangle((x + 10, 638, x + 188, 665), radius=8,
                            fill="#0a1530")
        d.text((x + 20, 645), thumbnail_labels.get(slug, slug.upper()),
               font=font(12, True), fill="#ecf4ff")
    # A restrained row of service badges replaces decorative dashboard art.
    badges = [
        "REHAB & DOCTOR SEARCH", "CITY / TOWN FILTERS",
        "CENTRE COMPARISON", "FACILITY WORKFLOWS",
    ]
    for i, label in enumerate(badges):
        x = 47 + i * 302
        accent = "#22d3ee" if i % 2 == 0 else "#a78bfa"
        d.rounded_rectangle((x, 777, x + 283, 832), radius=14,
                            fill="#1b2440", outline=accent, width=2)
        d.text((x + 13, 795), label, font=font(15, True), fill="#f0f5ff")
    d.text((47, 876),
           "AUTHENTIC WEBSITE PAGES  •  NO PATIENT DATA  •  PREVIEW ONLY",
           font=font(17), fill="#bac6dd")
    path = OUT / "rehabconnect-live.webp"
    hero.save(path, "WEBP", quality=88, method=6)
    valid_screenshot(path)


def update_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    matches = [p for p in data["projects"] if p.get("title") == "REHABCONNECT"]
    if len(matches) != 1:
        raise ValueError("Expected exactly one RehabConnect curated project")
    item = matches[0]
    item["image"] = "assets/previews/rehabconnect-live.webp"
    item["preview_kind"] = "real_website_screenshot"
    item["summary"] = PROJECT_SUMMARY
    item["category"] = "Healthcare Discovery Platform"
    item["website_type"] = PROJECT_TYPE
    item["short_description"] = PROJECT_SHORT
    item["description"] = PROJECT_DESCRIPTION
    item["technologies"] = TECHNOLOGIES
    item["features"] = FEATURES
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_full_portfolio(shots):
    original = PROFILE.read_text(encoding="utf-8")
    rows = [
        START,
        "## RehabConnect — Healthcare Discovery & Facility Operations",
        "",
        "**Platform type:** " + PROJECT_TYPE,
        "",
        "**Short description:** " + PROJECT_SHORT,
        "",
        "**Project overview:** " + PROJECT_DESCRIPTION,
        "",
        "**PUBLIC EXPERIENCE · FEATURE BADGES**",
        "",
        " ".join("<kbd>" + x + "</kbd>" for x in PUBLIC_FEATURES),
        "",
        "**FACILITY OPERATIONS · PRIVATE WORKFLOWS**",
        "",
        " ".join("<kbd>" + x + "</kbd>" for x in OPERATIONS_FEATURES),
        "",
        "**TECHNOLOGY STACK**",
        "",
        " ".join("<kbd>" + x + "</kbd>" for x in TECHNOLOGIES),
        "",
        "*The public features reflect site pages; staff, admissions and operations functions are high-level capabilities found in the private application, not screenshots of live patient or administration data.*",
        "",
        "**Website screenshot previews — no external redirects**",
        "",
        '<img src="./assets/previews/rehabconnect-live.webp" width="100%" '
        'alt="Real RehabConnect homepage with selected public-page previews" />',
        "",
        "### Selected Public Website Pages",
        "",
        "<table>",
    ]
    captured = [(slug, title) for slug, _, title, _ in ROUTES if slug in shots]
    for i in range(0, len(captured), 2):
        rows.append("<tr>")
        for slug, title in captured[i:i+2]:
            rows.append(
                '<td align="center" valign="top" width="50%">'
                '<img src="./assets/previews/rehabconnect-' + slug + '.webp" width="100%" '
                'alt="Actual public RehabConnect ' + title.replace('"', '&quot;') + ' webpage" />'
                '<sub><b>' + title.replace("&", "&amp;") + '</b> · Public website screenshot</sub>'
                "</td>"
            )
        if len(captured[i:i+2]) == 1:
            rows.append('<td width="50%"></td>')
        rows.append("</tr>")
    rows += [
        "</table>",
        "",
        "*Only approved, anonymous public-facing website pages are captured. "
        "No patient portal, staff dashboard, forms or private data are included. "
        "The screenshots refresh weekly; live pages can change between captures. Features are project capabilities, not claims of external clinical verification.*",
        END,
    ]
    section = "\n".join(rows)
    if original.count(START) > 1 or original.count(END) > 1:
        raise ValueError("Duplicate RehabConnect preview markers")
    if START in original and END in original:
        a = original.index(START)
        b = original.index(END, a) + len(END)
        output = original[:a] + section + original[b:]
    else:
        before = "## Source code, examples and confidentiality"
        if before not in original:
            raise ValueError("Portfolio insertion anchor missing")
        output = original.replace(before, section + "\n\n" + before)
    PROFILE.write_text(output, encoding="utf-8")


def main():
    shots = capture()
    for slug, _, title, _ in ROUTES:
        if slug in shots:
            picture_frame(shots[slug], title, OUT / ("rehabconnect-" + slug + ".webp"))
    build_hero(shots)
    # Only publish manifest when the real landing-page screenshot is complete.
    update_manifest()
    update_full_portfolio(shots)
    for source in shots.values():
        source.unlink(missing_ok=True)
    print(f"DONE: {len(shots)} real RehabConnect pages saved as non-linked website previews", flush=True)


if __name__ == "__main__":
    main()

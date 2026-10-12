#!/usr/bin/env python3
"""Capture genuine, public, unauthenticated Dr Shoaib website screenshots for profile.
No private data, no clicks, no forms, no external site hyperlinks in the gallery.
"""
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "previews"
BASE = "https://drshoaibpsychiatrist.com/"
ROUTES = [
    ("home", "/", "Homepage", True),
    ("why", "/why-dr-shoaib", "Why Dr. Shoaib?", False),
    ("blog", "/blog", "Mental Health Articles", False),
    ("pathways", "/recovery-pathways", "Recovery Pathways", False),
    ("adult", "/adult-psychiatry", "Adult Psychiatry", False),
    ("child", "/child-psychiatry", "Child & Adolescent Care", False),
    ("research", "/research", "Research & Insights", False),
    ("telepsychiatry", "/telepsychiatry", "Online Consultation Information", False),
    ("services", "/services", "Psychiatry Services", False),
    ("about", "/about", "About the Clinic", False),
]
MANIFEST = ROOT / "portfolio" / "curated_projects.json"

# Safe public-facing portfolio copy. Application capabilities do not imply all
# features are currently enabled in the live manually deployed website.
PROJECT_TYPE = "Psychiatry Clinic Website · CMS · Patient Services"
PROJECT_SUMMARY = "Psychiatry and mental-health website with specialist pathways, articles, research and appointment services"
PROJECT_SHORT = "Professional psychiatry website with care pathways, appointment access, specialist information and educational resources."
PROJECT_DESCRIPTION = (
    "A multi-module psychiatry website and clinic system with public mental-health content, "
    "adult and child psychiatry pathways, recovery guidance, telepsychiatry information, "
    "research and articles. The private application also includes editorial, patient and "
    "clinic-management tools."
)
TECHNOLOGIES = ["React","TypeScript","TanStack Start","Node.js","Express","MySQL","Tailwind CSS"]
PUBLIC_FEATURES = [
    "👨‍⚕️ Doctor Profile",
    "🧠 Adult Psychiatry",
    "🧒 Child & Adolescent Care",
    "🧭 Recovery Pathways",
    "🧩 Addiction Information",
    "💬 Psychotherapy Services",
    "💻 Telepsychiatry",
    "📰 Mental-Health Articles",
    "🔬 Research & Insights",
    "📅 Appointment Access",
    "📚 Treatment Information",
    "🔎 Service Discovery",
    "📱 Responsive Website"
]
PRIVATE_CAPABILITIES = [
    "📝 Content Management",
    "✅ Editorial Review",
    "👤 Patient Portal",
    "👩‍⚕️ Doctor Portal",
    "🏥 Clinic Administration",
    "📦 MediStock / Inventory",
    "🔐 Role-Based Access"
]
FEATURES = PUBLIC_FEATURES + PRIVATE_CAPABILITIES
MAX_PAGES = 9
MIN_PAGES = 3



def font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf"
    return ImageFont.truetype(p, size)


def check_image(path):
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.width < 1100 or image.height < 650:
            raise ValueError("Invalid or tiny screenshot")


def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    shots = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 900},
                                device_scale_factor=1, color_scheme="light",
                                reduced_motion="reduce", locale="en-US")
        for slug,route,title,required in ROUTES:
            if len(shots) >= MAX_PAGES:
                break
            url = urljoin(BASE, route.lstrip("/"))
            u = urlparse(url)
            if (u.hostname != "drshoaibpsychiatrist.com" or
                u.scheme != "https" or
                any(s in route.lower() for s in ("login", "admin", "patient", "dashboard", "booking", "?"))):
                raise ValueError("Route must be a whitelisted public content page")
            try:
                response = page.goto(url,wait_until="domcontentloaded",timeout=60000)
                if response is None or response.status >= 400:
                    raise ValueError("Unsuccessful public page response")
                if urlparse(page.url).hostname not in ("drshoaibpsychiatrist.com","www.drshoaibpsychiatrist.com"):
                    raise ValueError("Redirected off the approved website")
                page.wait_for_timeout(3500)
                if not page.locator("h1").count():
                    raise ValueError("No visible page heading")
                if any(x in page.title().lower() for x in
                       ("404", "not found", "access denied", "just a moment", "server error")):
                    raise ValueError("Invalid public page")
                path = OUT / ("_tmp-shoaib-" + slug + ".png")
                page.screenshot(path=str(path), full_page=False,animations="disabled")
                check_image(path)
                shots[slug] = path
                print("CAPTURED", title, response.status)
            except Exception as exc:
                print("SKIPPED", slug, type(exc).__name__, str(exc)[:150])
                if required:
                    raise
        browser.close()
    if "home" not in shots or len(shots) < MIN_PAGES:
        raise RuntimeError("At least three approved public page screenshots, including homepage, are required")
    return shots


def page_frame(path, title, dest):
    screen = Image.open(path).convert("RGB")
    box = Image.new("RGB", (1280, 785), "#080e20")
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((12, 12, 1268, 773), radius=20,
                        fill="#101729", outline="#855dd8",width=3)
    d.text((45,43),"DR. MUHAMMAD SHOAIB ZAFAR",
           font=font(25,True),fill="#f0f5ff")
    d.text((45,87),title+" / Actual public website page",
           font=font(18),fill="#22d3ee")
    # Entire visible viewport is preserved, scaled to the screenshot frame.
    scaled = screen.resize((1190, 630), Image.Resampling.LANCZOS)
    box.paste(scaled,(45,132))
    d.rectangle((44,131,1236,763),outline="#4f5584",width=2)
    box.save(dest,optimize=True)
    check_image(dest)


def make_card(shots):
    """Elegant client-facing hero using ONLY genuine website screenshots."""
    from PIL import ImageOps
    frame = Image.new("RGB", (1280, 918), "#090c1b")
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((9, 9, 1271, 909), radius=23,
                        fill="#10182d", outline="#8b5cf6", width=3)
    d.rectangle((42, 29, 309, 34), fill="#22d3ee")
    d.text((45, 52), "DR. MUHAMMAD SHOAIB ZAFAR",
           font=font(29, True), fill="#f0f5ff")
    d.text((45, 100), "PSYCHIATRY WEBSITE  /  CLINIC DIGITAL PLATFORM",
           font=font(17), fill="#a4e9f3")
    d.rounded_rectangle((1004, 68, 1230, 105), radius=11,
                        fill="#1b2646", outline="#7861c4", width=2)
    d.text((1020, 80), "REAL SITE PREVIEW", font=font(14, True),
           fill="#ede8ff")
    with Image.open(shots["home"]) as home:
        screen = ImageOps.fit(home.convert("RGB"), (1186, 470),
                              method=Image.Resampling.LANCZOS,
                              centering=(0.5, 0.1))
        frame.paste(screen, (47, 144))
    d.rectangle((47, 144, 1233, 614), outline="#63539c", width=2)
    labels = {
        "why":"WHY DR. SHOAIB", "pathways":"RECOVERY PATHWAYS",
        "adult":"ADULT PSYCHIATRY", "child":"CHILD PSYCHIATRY",
        "research":"RESEARCH", "blog":"ARTICLES",
        "telepsychiatry":"TELEPSYCHIATRY", "services":"SERVICES",
        "about":"ABOUT",
    }
    picks = [name for name in ("why", "pathways", "adult", "child",
             "research", "blog", "telepsychiatry") if name in shots][:3]
    for index, slug in enumerate(picks):
        x = 47 + 403 * index
        with Image.open(shots[slug]) as im:
            thumb = ImageOps.fit(im.convert("RGB"), (379, 120),
                                 method=Image.Resampling.LANCZOS,
                                 centering=(0.5, 0.12))
            frame.paste(thumb, (x, 635))
        d.rectangle((x, 635, x + 379, 755), outline="#456990", width=2)
        d.rounded_rectangle((x + 10, 645, x + 200, 674),
                            radius=7, fill="#111e3a")
        d.text((x + 18, 654), labels.get(slug, slug.upper()),
               font=font(12, True), fill="#ecf4ff")
    badges = ["SPECIALIST PATHWAYS", "HEALTH ARTICLES",
              "RESEARCH LIBRARY", "APPOINTMENT ACCESS"]
    for i, label in enumerate(badges):
        x = 47 + 302 * i
        accent = "#22d3ee" if i % 2 == 0 else "#a78bfa"
        d.rounded_rectangle((x, 781, x + 284, 837), radius=13,
                            fill="#1a2641", outline=accent, width=2)
        d.text((x + 12, 800), label, font=font(14, True),
               fill="#f1f5ff")
    d.text((47, 878),
           "ACTUAL PUBLIC WEBPAGES  •  NO PATIENT DATA  •  PREVIEW ONLY",
           font=font(16), fill="#b9c6dd")
    target = OUT / "dr-shoaib-live.png"
    frame.save(target, optimize=True)
    check_image(target)


def apply_manifest():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    items=[x for x in data["projects"] if x.get("title")=="DR. SHOAIB ZAFAR"]
    if len(items)!=1:
        raise ValueError("Expected exactly one Dr Shoaib gallery entry")
    items[0]["image"]="assets/previews/dr-shoaib-live.png"
    items[0]["preview_kind"]="real_website_screenshot"
    items[0]["summary"] = PROJECT_SUMMARY
    items[0]["category"] = "Healthcare Website / Clinic Platform"
    items[0]["website_type"] = PROJECT_TYPE
    items[0]["short_description"] = PROJECT_SHORT
    items[0]["description"] = PROJECT_DESCRIPTION
    items[0]["technologies"] = TECHNOLOGIES
    items[0]["features"] = FEATURES
    MANIFEST.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def apply_full_portfolio(shots):
    path=ROOT/"PORTFOLIO.md"
    text=path.read_text(encoding="utf-8")
    start="<!-- DR-SHOAIB-PUBLIC-PAGES:START -->"
    end="<!-- DR-SHOAIB-PUBLIC-PAGES:END -->"
    parts = [
        start,
        "## Dr. Muhammad Shoaib Zafar — Psychiatry Website & Clinic System",
        "",
        "**Platform type:** " + PROJECT_TYPE,
        "",
        "**Short description:** " + PROJECT_SHORT,
        "",
        "**Project overview:** " + PROJECT_DESCRIPTION,
        "",
        "**PUBLIC WEBSITE · FEATURE BADGES**",
        "",
        " ".join("<kbd>" + f + "</kbd>" for f in PUBLIC_FEATURES),
        "",
        "**PRIVATE APPLICATION · CLINIC / CMS CAPABILITIES**",
        "",
        " ".join("<kbd>" + f + "</kbd>" for f in PRIVATE_CAPABILITIES),
        "",
        "**TECHNOLOGY STACK**",
        "",
        " ".join("<kbd>" + tech + "</kbd>" for tech in TECHNOLOGIES),
        "",
        "*Public website pages and private codebase capabilities are shown separately. "
        "Private modules are not represented as live public screenshots or as clinically approved functions.*",
        "",
        "### Genuine Public Website Preview",
        "",
        '<img src="./assets/previews/dr-shoaib-live.png" width="100%" '
        'alt="Actual Dr Shoaib Zafar psychiatry website homepage and selected public pages"/>',
        "",
        "### Selected Public Pages",
        "",
        "<table>",
    ]
    available = [(slug, title) for slug, _, title, _ in ROUTES if slug in shots]
    for i in range(0, len(available), 2):
        parts.append("<tr>")
        for slug, title in available[i:i+2]:
            import html
            safe = html.escape(title)
            parts.append(
                '<td width="50%" align="center" valign="top">'
                '<img src="./assets/previews/dr-shoaib-' + slug +
                '.png" width="100%" alt="Real public Dr Shoaib ' + safe +
                ' webpage screenshot" /><br/><sub><b>' + safe +
                '</b> · Public webpage preview</sub></td>'
            )
        if len(available[i:i+2]) == 1:
            parts.append('<td width="50%"></td>')
        parts.append("</tr>")
    parts.append("</table>")
    parts.append("")
    parts.append(
        "*Screenshot images are not website or source links. Only anonymous public pages are "
        "captured, never admin, private patient records or authenticated booking flows. "
        "The private source project and manually deployed production site are unchanged.*"
    )
    block="\n".join(parts)
    if start in text and end in text:
        a=text.index(start)
        b=text.index(end,a)+len(end)
        text=text[:a]+block+text[b:]
    else:
        anchor="## Source code, examples and confidentiality"
        if anchor not in text:
            raise ValueError("Missing portfolio section anchor")
        text=text.replace(anchor,block+"\n\n"+anchor)
    path.write_text(text,encoding="utf-8")


def main():
    shots=capture()
    for slug,_,title,_ in ROUTES:
        if slug in shots:
            page_frame(shots[slug],title,OUT/("dr-shoaib-"+slug+".png"))
    make_card(shots)
    apply_manifest()
    apply_full_portfolio(shots)
    for source in shots.values():
        source.unlink(missing_ok=True)
    print("DONE: real, non-clickable Dr Shoaib webpage previews")


if __name__ == "__main__":
    main()

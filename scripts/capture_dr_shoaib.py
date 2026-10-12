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
]
MANIFEST = ROOT / "portfolio" / "curated_projects.json"


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
    if "home" not in shots:
        raise RuntimeError("Homepage is required to change public portfolio")
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
    # Big homepage capture. No simulated dashboards or website links.
    frame = Image.new("RGB", (1280, 785), "#0a0c1b")
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((9,9,1271,776),radius=22,
                        fill="#0f172b",outline="#895de0",width=3)
    d.text((44,44),"DR. SHOAIB ZAFAR — WEBSITE",font=font(27,True),fill="#eef4ff")
    d.text((44,89),"Actual public homepage preview · Private source remains private",
           font=font(17),fill="#22d3ee")
    screenshot = Image.open(shots["home"]).convert("RGB")
    screenshot = screenshot.resize((1190,635),Image.Resampling.LANCZOS)
    frame.paste(screenshot,(44,133))
    d.rectangle((44,133,1234,768),outline="#6c549e",width=2)
    target=OUT/"dr-shoaib-live.png"
    frame.save(target,optimize=True)
    check_image(target)


def apply_manifest():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    items=[x for x in data["projects"] if x.get("title")=="DR. SHOAIB ZAFAR"]
    if len(items)!=1:
        raise ValueError("Expected exactly one Dr Shoaib gallery entry")
    items[0]["image"]="assets/previews/dr-shoaib-live.png"
    items[0]["preview_kind"]="real_website_screenshot"
    items[0]["summary"]="Real psychiatry website design, educational content and public information"
    MANIFEST.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def apply_full_portfolio(shots):
    path=ROOT/"PORTFOLIO.md"
    text=path.read_text(encoding="utf-8")
    start="<!-- DR-SHOAIB-PUBLIC-PAGES:START -->"
    end="<!-- DR-SHOAIB-PUBLIC-PAGES:END -->"
    parts=[start,
           "## Dr. Shoaib Zafar · Actual public website pages","",
           "These are **real screenshots of public webpages**, not design concepts. "
           "The preview images do **not redirect** to the website or private GitHub repository.",""]
    for slug, _, title, _ in ROUTES:
        if slug not in shots:
            continue
        parts.extend(["**"+title+"**","",
            '<img src="./assets/previews/dr-shoaib-'+slug+
            '.png" width="100%" alt="Real public Dr Shoaib Zafar '+title+' page screenshot" />',""])
    parts.extend(["*Screenshots refresh on the weekly workflow; the live page may change in between.*",end])
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

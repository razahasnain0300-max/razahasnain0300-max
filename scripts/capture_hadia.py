#!/usr/bin/env python3
"""Capture APPROVED PUBLIC Hadia Collection webpages as real, non-linked portfolio images.

Only fixed public routes on hadia-collection.online. No forms, login, admin or patient pages.
Source software repo and website production deployment are never modified.
"""
from __future__ import annotations

# Screenshots are public read-only previews; never link them to the store or source.
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
BASE = "https://hadia-collection.online/"
START = "<!-- HADIA-COLLECTION-PUBLIC-PAGES:START -->"
END = "<!-- HADIA-COLLECTION-PUBLIC-PAGES:END -->"
ROUTES = [
    ("home", "/", "Shop Homepage", True),
    ("arrivals", "/new-arrivals", "New Arrivals", False),
    ("collections", "/collections", "Fashion Collections", False),
    ("upcoming", "/upcoming", "Upcoming Styles", False),
    ("about", "/about", "About the Brand", False),
    ("contact", "/contact", "Contact the Store", False),
    ("shipping", "/shipping-policy", "Delivery Information", False),
]
# User explicitly approved these public pages for screenshot display.
MAX_PAGES = 7
MIN_PAGES = 3
BLOCKED = ("/admin", "/account", "/login", "/register", "/cart", "/checkout",
           "/orders", "/api/", "/dashboard", "/security/", "/returns", "/reviews")


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(p), size)


def target_url(path):
    if not path.startswith("/") or path.startswith("//") or "?" in path or "#" in path:
        raise ValueError("Only static, approved public routes are permitted")
    url = urljoin(BASE, path.lstrip("/"))
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname != "hadia-collection.online"
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
                if target.hostname not in ("hadia-collection.online", "www.hadia-collection.online"):
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
                tmp = OUT / ("_tmp-hadia-" + slug + ".png")
                page.screenshot(path=str(tmp), full_page=False, animations="disabled")
                valid_screenshot(tmp)
                shots[slug] = tmp
                meta_node = page.locator('meta[name="description"]').first
                meta = " ".join((meta_node.get_attribute("content") or "").split())[:175] if meta_node.count() else ""
                headline = page.locator("h1").first
                h1 = " ".join(headline.inner_text().split())[:95] if headline.count() else ""
                print(f"SITE DESCRIPTION: {slug} — {page.title()[:100]} — {h1} — {meta}", flush=True)
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
    d.text((42, 48), "HADIA COLLECTION", font=font(27, True), fill="#eef5ff")
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
    # Large real landing page with three real-page thumbnail strips.
    hero = Image.new("RGB", (1280, 795), "#080d1b")
    d = ImageDraw.Draw(hero)
    d.rounded_rectangle((10, 10, 1270, 785), radius=21,
                        fill="#11162a", outline="#8b5cf6", width=3)
    d.rectangle((39, 30, 287, 34), fill="#22d3ee")
    d.text((42, 48), "HADIA COLLECTION — FASHION STORE", font=font(28, True), fill="#f1f5ff")
    d.text((42, 92), "Real storefront · Fashion collections · Shopping",
           font=font(18), fill="#8fe5f3")
    with Image.open(shots["home"]) as im:
        screen = im.convert("RGB")
        # The prominent portion is an authentic homepage screenshot.
        big = ImageOps.fit(screen, (1186, 500), method=Image.Resampling.LANCZOS,
                           centering=(.5, .15))
        hero.paste(big, (47, 136))
    d.rectangle((47, 136, 1233, 636), outline="#6256a1", width=2)
    thumbs = [slug for slug in shots if slug != "home"][:3]
    for i, slug in enumerate(thumbs):
        with Image.open(shots[slug]) as im:
            thumb = ImageOps.fit(im.convert("RGB"), (379, 104),
                                 method=Image.Resampling.LANCZOS, centering=(.5, .12))
        x = 47 + i * 403
        hero.paste(thumb, (x, 653))
        d.rectangle((x, 653, x+379, 757), outline="#3e5f90", width=2)
    file_path = OUT / "hadia-live.webp"
    hero.save(file_path, "WEBP", quality=87, method=6)
    valid_screenshot(file_path)


def update_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    matches = [p for p in data["projects"] if p.get("title") in ("HADIA & TAHA", "HADIA COLLECTION")]
    if len(matches) != 1:
        raise ValueError("Expected exactly one Hadia Collection curated project")
    item = matches[0]
    item["title"] = "HADIA COLLECTION"
    item["image"] = "assets/previews/hadia-live.webp"
    item["website_type"] = "Fashion E-Commerce Website / Online Store"
    item["technologies"] = ["Node.js", "Express", "EJS", "MySQL", "Socket.IO"]
    item["features"] = [
        "🛍️ Fashion Collections", "✨ New Arrivals", "🔎 Product Search",
        "🎛️ Catalog Filters", "📦 Color & Size Options", "🛒 Shopping Cart",
        "💵 Cash on Delivery", "🚚 Order Tracking", "👤 Customer Accounts",
        "⭐ Reviews & Ratings", "📦 Inventory Management", "🔄 Returns & Refunds",
        "🔔 Real-Time Updates", "📨 Contact & Support"
    ]
    item["short_description"] = "Hadia & Taha fashion storefront — curated collections, new arrivals, product browsing and customer shopping."
    item["description"] = "Fashion e-commerce platform built with Node.js, Express, EJS and MySQL, including catalog search, product options, customer shopping, orders and inventory workflows."
    item["preview_kind"] = "real_website_screenshot"
    item["summary"] = "Fashion shopping with curated collections, new arrivals, products, cart, orders and customer support"
    item["category"] = "Fashion E-Commerce"
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_full_portfolio(shots):
    original = PROFILE.read_text(encoding="utf-8")
    rows = [
        START,
        "## Hadia Collection — Fashion E-Commerce Website",
        "",
        "These are screenshots from the **actual publicly accessible website**, "
        "not illustrative dashboards. **Preview images are not links** to the "
        "website or the private GitHub source repository.",
        "",
        "**Landing page and selected public screens**",
        "",
        '<img src="./assets/previews/hadia-live.webp" width="100%" '
        'alt="Hadia Collection actual storefront homepage and fashion collection pages" />',
        "",
        "**Project type:** Fashion E-Commerce Website · Online Store · Product Catalog",
        "",
        "**Short description:** Fashion collections, new arrivals and customer-focused shopping.",
        "",
        "**Implemented features (per the project repository):** 🛍️ Collections · ✨ New Arrivals · 🔎 Search · 🎛️ Filters · 📦 Size/Color Selection · 🛒 Cart · 💵 COD Checkout · 🚚 Tracking · 👤 Accounts · ⭐ Reviews · 🔄 Returns · 🔔 Real-Time Order Updates.",
        "",
        "**Technology stack:** `Node.js` · `Express` · `EJS` · `JavaScript` · `MySQL` · `Socket.IO`",
        "",
        "**Note:** Screenshots document public website appearance; implementation features above come from the private source's public-safe feature inventory.",
        "",
        "### Selected website pages",
        "",
        "<table>",
    ]
    captured = [(slug, title) for slug, _, title, _ in ROUTES if slug in shots]
    for i in range(0, len(captured), 2):
        rows.append("<tr>")
        for slug, title in captured[i:i+2]:
            rows.append(
                '<td align="center" valign="top" width="50%">'
                '<img src="./assets/previews/hadia-' + slug + '.webp" width="100%" '
                'alt="Actual public Hadia Collection ' + title.replace('"', '&quot;') + ' webpage" />'
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
        "No customer account, checkout, admin or order details are included. "
        "The screenshots refresh weekly; live pages can change between captures.*",
        END,
    ]
    section = "\n".join(rows)
    if original.count(START) > 1 or original.count(END) > 1:
        raise ValueError("Duplicate Hadia Collection preview markers")
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
            picture_frame(shots[slug], title, OUT / ("hadia-" + slug + ".webp"))
    build_hero(shots)
    # Only publish manifest when the real landing-page screenshot is complete.
    update_manifest()
    update_full_portfolio(shots)
    for source in shots.values():
        source.unlink(missing_ok=True)
    print(f"DONE: {len(shots)} real Hadia Collection pages saved as non-linked website previews", flush=True)


if __name__ == "__main__":
    main()

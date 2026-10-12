import sys
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_project_gallery import merge_projects, block, swap, START, END, generated_card, format_date, canonical, load_curated


def sample(name, date, public=True):
    return {"title":name,"summary":"A professional software solution","category":"Python",
            "date":date,"is_public":public,"source":"public" if public else "approved_private",
            "image":"","public_url":"https://github.com/razahasnain0300-max/"+name if public else "",
            "repo_name":name}


class ProjectGalleryTests(unittest.TestCase):
    def test_newest_first_and_count(self):
        curated=[sample("Existing", "", False)]
        curated[0]["image"]="./assets/previews/goev.svg"
        curated[0]["source"]="curated"
        cur=merge_projects(curated,[sample("Old", "2025-01-01"),sample("New","2026-10-13")])
        self.assertEqual([x["title"] for x in cur],["New","Old","Existing"])
        for x in cur:
            if not x["image"]: x["image"]="./assets/previews/goev.svg"
        result=block(cur)
        self.assertIn("3 showcased projects",result)
        self.assertLess(result.index("New website or project showcase"), result.index("Old website or project showcase"))
        self.assertIn("Created 13 Oct 2026", result)
        another=merge_projects(curated,[sample("Newest","2026-10-14"),sample("Old","2025-01-01"),sample("New","2026-10-13")])
        self.assertEqual(len(another),4)
        self.assertEqual(another[0]["title"],"Newest")

    def test_gallery_only_changes_managed_section(self):
        text="header\n"+START+"\nold\n"+END+"\nfooter"
        update=swap(text,START,END,START+"\nnew\n"+END)
        self.assertTrue(update.startswith("header"))
        self.assertTrue(update.endswith("footer"))
        self.assertEqual(swap(update,START,END,START+"\nnew\n"+END),update)

    def test_generative_svg_is_valid_and_escaped(self):
        item=sample("public-project","2026-10-13")
        item["summary"]="<script>unsafe</script> & data"
        path,data=generated_card(item)
        self.assertTrue(path.endswith(".svg"))
        self.assertNotIn("<script>",data)
        ET.fromstring(data)

    def test_dates_never_fabricated(self):
        self.assertEqual(format_date(""),"")
        self.assertEqual(format_date("2026-10-13T22:15:00Z"),"13 Oct 2026")
        self.assertEqual(format_date("unverified"),"")

    def test_rich_project_card_safe_and_no_website_redirect(self):
        from build_project_gallery import card_text
        item = sample("Hadia Collection", "", False)
        item["source"] = "curated"
        item["image"] = "./assets/previews/hadia-taha.svg"
        item["preview_kind"] = "real_website_screenshot"
        item["website_type"] = "Fashion E-Commerce Website"
        item["features"] = ["New Arrivals", "Fashion Collections", "Product Details"]
        item["summary"] = 'Public online fashion store with <safe> & "brands".'
        markup = card_text(item)
        self.assertIn("Fashion E-Commerce Website", markup)
        self.assertIn("New Arrivals", markup)
        self.assertIn("&lt;safe&gt;", markup)
        self.assertNotIn('href="https://hadia-collection.online', markup)
        self.assertNotIn('href="https://github.com', markup)

    def test_curated_hadia_rich_metadata_and_tech_badges(self):
        from build_project_gallery import load_curated, card_text, ROOT
        projects = load_curated(ROOT / "portfolio" / "curated_projects.json")
        items = [x for x in projects if x["title"] == "HADIA COLLECTION"]
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["preview_kind"], "real_website_screenshot")
        self.assertIn("Node.js", item["technologies"])
        self.assertTrue(item["short_description"])
        markup = card_text(item)
        self.assertIn("BUILT WITH", markup)
        self.assertIn("<kbd>Node.js</kbd>", markup)
        self.assertIn("Fashion Collections", markup)
        self.assertNotIn('href="https://hadia-collection.online', markup)

    def test_rehabconnect_rich_preview_and_non_redirect_badges(self):
        from build_project_gallery import load_curated, card_text, ROOT
        entries = [x for x in load_curated(ROOT / "portfolio" / "curated_projects.json")
                   if x["title"] == "REHABCONNECT"]
        self.assertEqual(len(entries), 1)
        item = entries[0]
        self.assertEqual(item["preview_kind"], "real_website_screenshot")
        self.assertIn("Centre Comparison", " ".join(item["features"]))
        self.assertIn("TypeScript", item["technologies"])
        markup = card_text(item)
        self.assertIn("HEALTHCARE", markup.upper())
        self.assertIn("FEATURES", markup)
        self.assertIn("<kbd>React</kbd>", markup)
        self.assertNotIn("<a ", markup)
        self.assertNotIn("rehabconnect.pk/", markup)

if __name__ == "__main__":
    unittest.main()

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
        self.assertLess(result.index("New visual"), result.index("Old visual"))
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

if __name__ == "__main__":
    unittest.main()

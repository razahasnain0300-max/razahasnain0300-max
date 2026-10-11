import sys
import unittest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from approved_projects import load, apply

class TestApproved(unittest.TestCase):
    def samples(self, rows):
        with TemporaryDirectory() as d:
            p = Path(d) / "data.json"
            p.write_text(json.dumps({"projects":rows}), encoding="utf-8")
            return load(p)

    def test_private_projects_hidden_until_approved(self):
        items = self.samples([{"public_title":"Secret customer", "public_summary":"Private work",
                               "approved_for_public_profile":False}])
        self.assertEqual(items, [])

    def test_safe_approved_case_study(self):
        items = self.samples([{"public_title":"Example Case", "public_summary":"Sample dashboard",
                               "approved_for_public_profile":True, "technologies":"React"}])
        original = "Top\n<!-- APPROVED-CASESTUDIES:START -->\n<!-- APPROVED-CASESTUDIES:END -->\nEnd"
        updated, svg = apply(original, items)
        self.assertIn("Example Case", updated)
        self.assertTrue(updated.startswith("Top"))
        self.assertTrue(updated.endswith("End"))
        self.assertEqual(apply(updated, items)[0], updated)
        ET.fromstring(svg)

    def test_invalid_fields_rejected(self):
        for extra in ({"private_repo":"owner/secret"}, {"public_demo_url":"javascript:alert(1)"},
                      {"public_demo_url":"https://github.com/owner/secret"}):
            row = {"public_title":"Example", "public_summary":"Safe text",
                   "approved_for_public_profile":True}
            row.update(extra)
            with self.assertRaises(ValueError):
                self.samples([row])

if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from capture_hadia import ROUTES, BLOCKED, target_url

class TestHadiaPreview(unittest.TestCase):
    def test_safe_routes(self):
        self.assertGreaterEqual(len(ROUTES), 6)
        for _,route,_,_ in ROUTES:
            self.assertTrue(target_url(route).startswith("https://hadia-collection.online/"))
        for route in ("//evil.example","/admin","/account/dashboard","/cart","/checkout",
                      "/orders","/api/products","/contact?email=sensitive"):
            with self.assertRaises(ValueError):
                target_url(route)

if __name__=="__main__":
    unittest.main()

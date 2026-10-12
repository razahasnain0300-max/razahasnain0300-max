import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

class DrShoaibPublicCaptureTests(unittest.TestCase):
    def test_routes_have_public_safe_scope(self):
        from capture_dr_shoaib import ROUTES, MAX_PAGES, MIN_PAGES, TECHNOLOGIES
        self.assertGreaterEqual(len(ROUTES), 8)
        self.assertLessEqual(MAX_PAGES, 10)
        self.assertGreaterEqual(MIN_PAGES, 3)
        self.assertIn("MySQL", TECHNOLOGIES)
        for _, route, _, _ in ROUTES:
            self.assertTrue(route.startswith("/"))
            self.assertFalse(any(bad in route.lower() for bad in
                ("admin", "patient", "checkout", "login", "account", "booking", "api/")))

    def test_only_public_descriptors(self):
        from capture_dr_shoaib import PUBLIC_FEATURES, PRIVATE_CAPABILITIES
        self.assertLessEqual(len(PUBLIC_FEATURES + PRIVATE_CAPABILITIES), 24)
        self.assertIn("Recovery Pathways", " ".join(PUBLIC_FEATURES))
        self.assertIn("Content Management", " ".join(PRIVATE_CAPABILITIES))

if __name__ == "__main__":
    unittest.main()

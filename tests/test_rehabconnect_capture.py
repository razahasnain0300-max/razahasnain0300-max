import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

class RehabPublicRouteTests(unittest.TestCase):
    def test_public_routes_are_explicit_and_safe(self):
        from capture_rehabconnect import ROUTES, target_url, BLOCKED
        self.assertGreaterEqual(len(ROUTES), 9)
        for slug, route, title, required in ROUTES:
            result = target_url(route)
            self.assertTrue(result.startswith("https://rehabconnect.pk/"))
            self.assertFalse(any(x in route.lower() for x in BLOCKED))
        for path in ("//evil.invalid", "/admin/dashboard", "/patient/login", "/booking", "/api/private", "/get-help?patient=secret"):
            with self.assertRaises(ValueError):
                target_url(path)

    def test_portfolio_capabilities_have_safe_limits(self):
        from capture_rehabconnect import PUBLIC_FEATURES, OPERATIONS_FEATURES, TECHNOLOGIES, PROJECT_TYPE
        features = PUBLIC_FEATURES + OPERATIONS_FEATURES
        self.assertLessEqual(len(features), 24)
        self.assertGreaterEqual(len(PUBLIC_FEATURES), 8)
        self.assertIn("React", TECHNOLOGIES)
        self.assertIn("MySQL", TECHNOLOGIES)
        self.assertIn("Healthcare Directory", PROJECT_TYPE)
        self.assertFalse(any("patient name" in x.lower() for x in features))

if __name__ == "__main__":
    unittest.main()

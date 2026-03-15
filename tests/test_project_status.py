from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wine_rating_inference.project_status import CORE_ASSETS, human_size, render_report


class ProjectStatusTests(unittest.TestCase):
    def test_human_size_formats_bytes(self) -> None:
        self.assertEqual(human_size(512), "512 B")
        self.assertEqual(human_size(2048), "2.0 KB")

    def test_core_assets_include_official_slides(self) -> None:
        labels = {asset.label for asset in CORE_ASSETS}
        self.assertIn("official_slides", labels)
        self.assertIn("canonical_notebook", labels)
        self.assertIn("legacy_notebook", labels)

    def test_render_report_mentions_project(self) -> None:
        report = render_report()
        self.assertIn("Wine Rating Inference Project Status", report)
        self.assertIn("official_slides", report)


if __name__ == "__main__":
    unittest.main()

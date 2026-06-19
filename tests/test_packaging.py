import tempfile
import unittest
from pathlib import Path

from scripts.package_project import should_include


class PackageSafetyTest(unittest.TestCase):
    def test_private_data_paths_are_excluded_from_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_csv = root / "input" / "real_export.csv"
            private_xlsx = root / "private.xlsx"
            output_file = root / "output_py_path" / "summary.json"
            egg_info_file = root / "src" / "project.egg-info" / "PKG-INFO"
            sample_csv = root / "sample_data" / "demo.csv"

            private_csv.parent.mkdir()
            output_file.parent.mkdir()
            egg_info_file.parent.mkdir(parents=True)
            sample_csv.parent.mkdir()
            private_csv.write_text("private", encoding="utf-8")
            private_xlsx.write_text("private", encoding="utf-8")
            output_file.write_text("generated", encoding="utf-8")
            egg_info_file.write_text("generated", encoding="utf-8")
            sample_csv.write_text("demo", encoding="utf-8")

            self.assertFalse(should_include(private_csv, root))
            self.assertFalse(should_include(private_xlsx, root))
            self.assertFalse(should_include(output_file, root))
            self.assertFalse(should_include(egg_info_file, root))
            self.assertTrue(should_include(sample_csv, root))


if __name__ == "__main__":
    unittest.main()

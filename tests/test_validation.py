import json
import tempfile
import unittest
from pathlib import Path

from factory_excel_ops.cli import _filter_by_size
from factory_excel_ops.validation import validate_profile


class ConfigValidationTest(unittest.TestCase):
    def test_duplicate_metric_key_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_types = root / "file_types.json"
            field_mapping = root / "field_mapping.json"
            metrics = root / "metrics.json"

            file_types.write_text(
                json.dumps({"inventory": {"headers": ["item_code"], "values": [], "filename": []}}),
                encoding="utf-8",
            )
            field_mapping.write_text(json.dumps({"item_code": ["item_code"]}), encoding="utf-8")
            metrics.write_text(
                json.dumps({
                    "metrics": [
                        {"key": "duplicate", "label": "One", "type": "count", "source_type": "inventory"},
                        {"key": "duplicate", "label": "Two", "type": "count", "source_type": "inventory"},
                    ]
                }),
                encoding="utf-8",
            )

            result = validate_profile(file_types, field_mapping, metrics)

            self.assertFalse(result.ok)
            self.assertTrue(any("duplicate key" in error for error in result.errors))

    def test_filter_by_size_skips_large_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            small = root / "small.csv"
            large = root / "large.csv"
            small.write_text("a,b\n1,2\n", encoding="utf-8")
            large.write_bytes(b"x" * 2048)

            included, warnings = _filter_by_size([small, large], max_file_mb=0.001)

            self.assertEqual(included, [small])
            self.assertIn("file size exceeds", warnings[0])

    def test_filter_by_size_allows_empty_inputs(self):
        included, warnings = _filter_by_size([], max_file_mb=25)

        self.assertEqual(included, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()

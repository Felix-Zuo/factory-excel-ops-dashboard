import json
import os
import tempfile
import unittest
from pathlib import Path

from factory_excel_ops.adapter_builder import ModelAssistConfig, build_adaptation_profile
from factory_excel_ops.classifier import FileClassifier
from factory_excel_ops.field_mapper import FieldMapper
from factory_excel_ops.ingest import ingest_paths, summarize
from factory_excel_ops.metrics import load_metric_specs
from factory_excel_ops.validation import validate_profile


class AdapterBuilderTest(unittest.TestCase):
    def test_local_adaptation_creates_runnable_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "incoming"
            output_dir = root / "profile"
            input_dir.mkdir()
            (input_dir / "warehouse_stock_export.csv").write_text(
                "SKU No,Product Name,On Hand Units,Snapshot Date\n"
                "A-100,Field repair kit,12,2026-07-01\n"
                "A-200,Service cable,0,2026-07-01\n",
                encoding="utf-8",
            )

            result = build_adaptation_profile(input_dir, output_dir)

            self.assertEqual(len(result.files), 1)
            self.assertEqual(result.files[0].source_type, "inventory")
            self.assertGreaterEqual(result.files[0].confidence, 0.55)
            self.assertTrue((output_dir / "file_types.json").exists())
            self.assertTrue((output_dir / "field_mapping.json").exists())
            self.assertTrue((output_dir / "metrics.json").exists())
            validation = validate_profile(
                output_dir / "file_types.json",
                output_dir / "field_mapping.json",
                output_dir / "metrics.json",
            )
            self.assertTrue(validation.ok, validation.errors)

            records, warnings = ingest_paths(
                [input_dir / "warehouse_stock_export.csv"],
                FileClassifier.from_json(output_dir / "file_types.json"),
                FieldMapper.from_json(output_dir / "field_mapping.json"),
            )
            summary = summarize(records, file_count=1, warnings=warnings, metric_specs=load_metric_specs(output_dir / "metrics.json"))

            self.assertEqual(warnings, [])
            self.assertEqual(summary.record_count, 2)
            self.assertEqual(summary.by_source_type, {"inventory": 2})
            self.assertTrue(any(metric.key == "inventory_available_qty_sum" for metric in summary.metrics))

    def test_model_assist_skips_cleanly_without_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "incoming"
            output_dir = root / "profile"
            input_dir.mkdir()
            (input_dir / "odd_table.csv").write_text(
                "Reference,Owner,Amount\n"
                "R-1,Team A,12\n",
                encoding="utf-8",
            )
            os.environ.pop("FACTORY_EXCEL_OPS_API_KEY", None)

            result = build_adaptation_profile(
                input_dir,
                output_dir,
                model_config=ModelAssistConfig(
                    enabled=True,
                    endpoint="https://example.invalid/v1",
                    model="mapper",
                ),
            )
            report = json.loads((output_dir / "adaptation_report.json").read_text(encoding="utf-8"))

            self.assertEqual(len(result.files), 1)
            self.assertIn("skipped: set FACTORY_EXCEL_OPS_API_KEY", result.files[0].model_assist)
            self.assertFalse(report["privacy"]["api_key_saved"])
            self.assertEqual(report["privacy"]["raw_rows_sent_by_default"], False)


if __name__ == "__main__":
    unittest.main()

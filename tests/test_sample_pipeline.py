import json
import re
import unittest
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from factory_excel_ops.analysis_context import build_analysis_context
from factory_excel_ops.classifier import FileClassifier
from factory_excel_ops.field_mapper import FieldMapper
from factory_excel_ops.ingest import ingest_paths, summarize
from factory_excel_ops.integration_interface import default_integration_interface
from factory_excel_ops.metrics import load_metric_specs
from factory_excel_ops.validation import validate_profile


ROOT = Path(__file__).resolve().parents[1]


class SamplePipelineTest(unittest.TestCase):
    def test_sample_files_classify_and_summarize(self):
        classifier = FileClassifier.from_json(ROOT / "config" / "sample_file_types.json")
        mapper = FieldMapper.from_json(ROOT / "config" / "sample_field_mapping.json")
        metric_specs = load_metric_specs(ROOT / "config" / "sample_metrics.json")
        paths = sorted((ROOT / "sample_data").glob("*.csv"))

        records, warnings = ingest_paths(paths, classifier, mapper)
        summary = summarize(records, file_count=len(paths), warnings=warnings, metric_specs=metric_specs)

        self.assertEqual(warnings, [])
        self.assertEqual(summary.file_count, 5)
        self.assertEqual(summary.record_count, 14)
        self.assertEqual(summary.inventory_items, 4)
        self.assertEqual(summary.out_of_stock_items, 1)
        self.assertEqual(summary.order_demand_qty, 135)
        self.assertEqual(summary.shipment_qty, 50)
        self.assertEqual(summary.purchase_qty, 400)
        self.assertEqual(summary.production_qty, 130)
        self.assertEqual(
            summary.by_source_type,
            {
                "demand": 3,
                "fulfillment": 2,
                "inventory": 4,
                "replenishment": 2,
                "work_output": 3,
            },
        )
        self.assertEqual([metric.key for metric in summary.metrics], [
            "inventory_items",
            "out_of_stock_items",
            "order_demand_qty",
            "shipment_qty",
            "purchase_qty",
            "production_qty",
        ])

    def test_field_mapping_normalizes_common_header_noise(self):
        mapper = FieldMapper.from_json(ROOT / "config" / "sample_field_mapping.json")

        normalized = mapper.normalize({
            "Item Code": "SKU-9001",
            "Available Qty (EA)": "12",
            "Due-Date": "2026-07-20",
        })

        self.assertEqual(normalized["item_code"], "SKU-9001")
        self.assertEqual(normalized["available_qty"], "12")
        self.assertEqual(normalized["source_date"], "2026-07-20")

    def test_classifier_normalizes_header_noise(self):
        path = ROOT / "sample_data" / "inventory_sample.csv"
        classifier = FileClassifier({
            "inventory": {
                "headers": ["Item Code", "Available Qty (EA)"],
                "values": [],
                "filename": [],
            }
        })

        result = classifier.classify(path)

        self.assertEqual(result.source_type, "inventory")
        self.assertGreaterEqual(result.confidence, 0.6)

    def test_low_confidence_files_are_warned_and_skipped(self):
        classifier = FileClassifier({
            "weak_match": {
                "headers": [],
                "values": [],
                "filename": ["inventory"],
            }
        })
        mapper = FieldMapper.from_json(ROOT / "config" / "sample_field_mapping.json")

        records, warnings = ingest_paths(
            [ROOT / "sample_data" / "inventory_sample.csv"],
            classifier,
            mapper,
            min_confidence=0.2,
        )

        self.assertEqual(records, [])
        self.assertIn("low classification confidence", warnings[0])

    def test_public_profile_validates(self):
        result = validate_profile(
            ROOT / "config" / "sample_file_types.json",
            ROOT / "config" / "sample_field_mapping.json",
            ROOT / "config" / "sample_metrics.json",
        )

        self.assertTrue(result.ok, result.errors)

    def test_integration_contract_uses_neutral_public_commands(self):
        contract = default_integration_interface()
        text = json.dumps(contract, ensure_ascii=False)
        legacy_term = "ag" + "ent"

        self.assertIn("integration-spec", text)
        self.assertIn("integration_interface", text)
        self.assertNotIn(legacy_term, text.lower())

    def test_analysis_context_uses_review_payload_shape(self):
        classifier = FileClassifier.from_json(ROOT / "config" / "sample_file_types.json")
        mapper = FieldMapper.from_json(ROOT / "config" / "sample_field_mapping.json")
        metric_specs = load_metric_specs(ROOT / "config" / "sample_metrics.json")
        paths = sorted((ROOT / "sample_data").glob("*.csv"))
        records, warnings = ingest_paths(paths, classifier, mapper)
        summary = summarize(records, file_count=len(paths), warnings=warnings, metric_specs=metric_specs)

        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            summary_path = tmp_path / "summary.json"
            output_path = tmp_path / "analysis_context.json"
            summary_path.write_text(json.dumps(asdict(summary), ensure_ascii=False), encoding="utf-8")

            context = build_analysis_context(summary_path, output_path)

        self.assertEqual(context["context_type"], "operations_review_context")
        self.assertIn("review_sections", context)
        self.assertIn("review_rules", context)
        self.assertNotIn("role", context)

    def test_public_text_surface_stays_neutral(self):
        public_paths = [
            ROOT / "README.md",
            ROOT / "integration_interface.json",
            ROOT / "docs" / "showcase.html",
            ROOT / "docs" / "index.html",
            ROOT / "docs" / "showcase_design_benchmark.md",
            ROOT / "docs" / "assets" / "data-flow.svg",
            ROOT / "docs" / "assets" / "workbench-product.svg",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in public_paths)
        patterns = [
            r"\b" + "a" + "i" + r"\b",
            "open" + "ai",
            "chat" + "gpt",
            "cop" + "ilot",
            "assis" + "tant",
            "ag" + "ent",
            r"\b" + "ll" + "m" + r"\b",
            "智" + "能" + "体",
        ]

        for pattern in patterns:
            self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE), pattern)

        showcase = (ROOT / "docs" / "showcase.html").read_text(encoding="utf-8")
        self.assertIn('data-code-tab="run"', showcase)
        self.assertIn("release package", showcase)

    def test_public_surfaces_read_like_a_product(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        showcase = (ROOT / "docs" / "showcase.html").read_text(encoding="utf-8")

        self.assertIn("docs/assets/workbench-product.png", readme)
        self.assertNotIn("Public core", showcase)
        self.assertNotIn("public " + "edition", showcase)
        self.assertNotIn("private" + "-project", showcase)
        self.assertNotIn("公开" + "核心", showcase)
        self.assertNotIn("公开" + "版本", showcase)
        self.assertNotIn("项目" + "截图", showcase)
        self.assertNotIn("synthetic " + "demo", readme.lower())
        self.assertNotIn("public " + "demo", readme.lower())
        self.assertNotIn("sanit" + "ized", readme.lower())

    def test_public_pages_have_share_metadata(self):
        showcase = (ROOT / "docs" / "showcase.html").read_text(encoding="utf-8")
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertTrue((ROOT / "docs" / ".nojekyll").exists())
        self.assertIn('rel="canonical"', showcase)
        self.assertIn('property="og:image"', showcase)
        self.assertIn('name="twitter:card"', showcase)
        self.assertIn("workbench-product.png", showcase)
        self.assertIn("url=showcase.html", index)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from factory_excel_ops.classifier import FileClassifier
from factory_excel_ops.field_mapper import FieldMapper
from factory_excel_ops.ingest import ingest_paths, summarize


ROOT = Path(__file__).resolve().parents[1]


class DemoPipelineTest(unittest.TestCase):
    def test_demo_files_classify_and_summarize(self):
        classifier = FileClassifier.from_json(ROOT / "config" / "sample_file_types.json")
        mapper = FieldMapper.from_json(ROOT / "config" / "sample_field_mapping.json")
        paths = sorted((ROOT / "sample_data").glob("*.csv"))

        records, warnings = ingest_paths(paths, classifier, mapper)
        summary = summarize(records, file_count=len(paths), warnings=warnings)

        self.assertEqual(warnings, [])
        self.assertEqual(summary.file_count, 5)
        self.assertEqual(summary.record_count, 14)
        self.assertEqual(summary.inventory_items, 4)
        self.assertEqual(summary.out_of_stock_items, 1)
        self.assertEqual(summary.order_demand_qty, 135)
        self.assertEqual(summary.shipment_qty, 50)
        self.assertEqual(summary.purchase_qty, 400)
        self.assertEqual(summary.production_qty, 130)


if __name__ == "__main__":
    unittest.main()

"""Build runnable spreadsheet profiles from unfamiliar tables."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .field_mapper import DEFAULT_MAPPING
from .io import read_table_preview


STANDARD_FIELDS = tuple(DEFAULT_MAPPING.keys())

QUANTITY_FIELDS = {
    "available_qty",
    "demand_qty",
    "fulfilled_qty",
    "replenishment_qty",
    "output_qty",
}

FIELD_HINTS: dict[str, list[str]] = {
    "item_code": [
        "itemcode",
        "itemid",
        "itemno",
        "materialcode",
        "materialid",
        "productcode",
        "productid",
        "sku",
        "partno",
        "料号",
        "物料编码",
        "产品编码",
        "货号",
    ],
    "item_name": [
        "itemname",
        "materialname",
        "productname",
        "description",
        "desc",
        "品名",
        "物料名称",
        "产品名称",
        "名称",
    ],
    "available_qty": [
        "availableqty",
        "stockqty",
        "inventoryqty",
        "onhandqty",
        "onhand",
        "balanceqty",
        "qtyavailable",
        "库存",
        "可用",
        "现存",
        "在库",
    ],
    "demand_qty": [
        "demandqty",
        "orderqty",
        "requiredqty",
        "requestqty",
        "needqty",
        "qtyneeded",
        "needed",
        "needunits",
        "需求",
        "订单数量",
        "要货",
    ],
    "fulfilled_qty": [
        "fulfilledqty",
        "shipmentqty",
        "shipqty",
        "deliveryqty",
        "deliveredqty",
        "qtyfulfilled",
        "发货",
        "交付",
        "已发",
        "已交",
    ],
    "replenishment_qty": [
        "replenishmentqty",
        "purchaseqty",
        "plannedqty",
        "poqty",
        "supplyqty",
        "补货",
        "采购",
        "计划数量",
    ],
    "output_qty": [
        "outputqty",
        "productionqty",
        "completedqty",
        "assemblyqty",
        "finishedqty",
        "产出",
        "完工",
        "完成数量",
    ],
    "account": [
        "account",
        "customer",
        "customername",
        "soldto",
        "client",
        "buyer",
        "客户",
        "账户",
        "门店",
    ],
    "partner": [
        "partner",
        "supplier",
        "suppliername",
        "vendor",
        "provider",
        "供应商",
        "伙伴",
        "承运",
    ],
    "source_date": [
        "date",
        "shipdate",
        "requireddate",
        "promisedate",
        "workdate",
        "duedate",
        "createdat",
        "updatedat",
        "日期",
        "时间",
    ],
}

SOURCE_FIELD_WEIGHTS = {
    "inventory": {"available_qty": 8, "item_code": 2, "source_date": 1},
    "demand": {"demand_qty": 8, "account": 2, "item_code": 2, "source_date": 1},
    "fulfillment": {"fulfilled_qty": 8, "account": 2, "item_code": 2, "source_date": 1},
    "replenishment": {"replenishment_qty": 8, "partner": 2, "item_code": 2, "source_date": 1},
    "work_output": {"output_qty": 8, "item_code": 2, "source_date": 1},
}

SOURCE_NAME_HINTS = {
    "inventory": ["inventory", "stock", "asset", "onhand", "库存", "在库"],
    "demand": ["demand", "order", "sales", "request", "需求", "订单"],
    "fulfillment": ["fulfillment", "shipment", "delivery", "dispatch", "发货", "交付"],
    "replenishment": ["replenishment", "purchase", "procurement", "supply", "采购", "补货"],
    "work_output": ["workoutput", "production", "capacity", "completion", "产出", "完工"],
}


@dataclass(frozen=True)
class FieldSuggestion:
    """One proposed header-to-standard-field match."""

    header: str
    standard_field: str
    confidence: float
    reason: str
    source: str = "local"


@dataclass(frozen=True)
class FileAdaptation:
    """Profile suggestion for one source file."""

    file: str
    source_type: str
    confidence: float
    reasons: list[str]
    fields: list[FieldSuggestion]
    model_assist: str = "not_used"


@dataclass
class AdaptationResult:
    """Generated profile and review report."""

    file_types: dict[str, dict[str, list[str]]]
    field_mapping: dict[str, list[str]]
    metrics: dict[str, Any]
    files: list[FileAdaptation]
    warnings: list[str] = field(default_factory=list)

    def report(self) -> dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "profile": "operations-data-workbench.adapted.v1",
            "files": [asdict(file) for file in self.files],
            "warnings": self.warnings,
            "privacy": {
                "api_key_saved": False,
                "model_payload": "headers and column-shape sketches only",
                "raw_rows_sent_by_default": False,
            },
            "next_steps": [
                "Review file_types.json and field_mapping.json before using them on a live folder.",
                "Run validate-config against the generated profile.",
                "Run the pipeline with the generated configs and inspect summary.json warnings.",
            ],
        }


@dataclass(frozen=True)
class ModelAssistConfig:
    """Runtime settings for optional boundary help."""

    enabled: bool = False
    api_key_env: str = "FACTORY_EXCEL_OPS_API_KEY"
    endpoint: str = ""
    model: str = ""
    timeout_seconds: int = 20


class ModelAssistClient:
    """Small HTTP client for chat-completions-style structured suggestions."""

    def __init__(self, config: ModelAssistConfig) -> None:
        self.config = config

    def suggest(self, payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        api_key = os.environ.get(self.config.api_key_env, "").strip()
        if not self.config.enabled:
            return None, "disabled"
        if not api_key:
            return None, f"skipped: set {self.config.api_key_env}"
        if not self.config.endpoint:
            return None, "skipped: model endpoint is not configured"
        if not self.config.model:
            return None, "skipped: model name is not configured"

        body = {
            "model": self.config.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only JSON. Map spreadsheet headers to the provided standard "
                        "fields and choose one source_type. Do not invent business facts."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }
        request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            return None, f"failed: {exc}"

        content = _extract_response_content(response_payload)
        if content is None:
            return None, "failed: response did not contain structured content"
        try:
            suggestion = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError as exc:
            return None, f"failed: invalid structured content ({exc})"
        if not isinstance(suggestion, dict):
            return None, "failed: structured content must be an object"
        return suggestion, "used"


def build_adaptation_profile(
    input_dir: Path,
    output_dir: Path,
    *,
    model_config: ModelAssistConfig | None = None,
    max_sample_rows: int = 12,
    min_local_confidence: float = 0.55,
) -> AdaptationResult:
    """Create runnable config files for a folder of CSV/XLSX tables."""

    paths = sorted(
        path for path in input_dir.iterdir()
        if path.suffix.lower() in {".csv", ".xlsx", ".xlsm"}
    )
    warnings: list[str] = []
    if not paths:
        warnings.append("No supported input files found.")

    client = ModelAssistClient(model_config or ModelAssistConfig())
    file_adaptations: list[FileAdaptation] = []
    file_types: dict[str, dict[str, list[str]]] = {}
    field_mapping = {field: list(aliases) for field, aliases in DEFAULT_MAPPING.items()}

    for path in paths:
        try:
            preview = read_table_preview(path, max_rows=max_sample_rows)
        except (OSError, ValueError, RuntimeError) as exc:
            warnings.append(f"{path.name}: cannot read table ({exc})")
            continue
        headers = list(preview[0].keys()) if preview else []
        local_fields = [_match_header(header) for header in headers]
        source_type, source_confidence, source_reasons = _infer_source_type(path, local_fields, headers)
        model_state = "not_needed"

        if source_confidence < min_local_confidence or _low_field_coverage(local_fields):
            payload = _model_payload(path, headers, preview)
            suggestion, model_state = client.suggest(payload)
            if suggestion:
                source_type, source_confidence, source_reasons, local_fields = _merge_model_suggestion(
                    suggestion,
                    fallback_source=source_type,
                    fallback_confidence=source_confidence,
                    fallback_reasons=source_reasons,
                    fields=local_fields,
                )

        file_record = FileAdaptation(
            file=path.name,
            source_type=source_type,
            confidence=round(source_confidence, 2),
            reasons=source_reasons,
            fields=[field for field in local_fields if field.standard_field],
            model_assist=model_state,
        )
        file_adaptations.append(file_record)

        _merge_file_signature(file_types, source_type, path, headers)
        for field in file_record.fields:
            aliases = field_mapping.setdefault(field.standard_field, [])
            if field.header not in aliases:
                aliases.append(field.header)

    metrics = _build_metrics(file_adaptations)
    result = AdaptationResult(
        file_types=file_types,
        field_mapping=field_mapping,
        metrics=metrics,
        files=file_adaptations,
        warnings=warnings,
    )
    write_adaptation_profile(result, output_dir)
    return result


def write_adaptation_profile(result: AdaptationResult, output_dir: Path) -> None:
    """Write generated config files and the review report."""

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "file_types.json", result.file_types)
    _write_json(output_dir / "field_mapping.json", result.field_mapping)
    _write_json(output_dir / "metrics.json", result.metrics)
    _write_json(output_dir / "adaptation_report.json", result.report())


def _match_header(header: str) -> FieldSuggestion:
    normalized = _normalize(header)
    best_field = ""
    best_score = 0.0
    best_reason = "no local match"

    for standard, aliases in DEFAULT_MAPPING.items():
        for alias in aliases:
            alias_normalized = _normalize(alias)
            if normalized == alias_normalized:
                return FieldSuggestion(header, standard, 1.0, f"known alias:{alias}")
            if alias_normalized and alias_normalized in normalized:
                score = 0.82
                if score > best_score:
                    best_field = standard
                    best_score = score
                    best_reason = f"contains alias:{alias}"

    for standard, hints in FIELD_HINTS.items():
        for hint in hints:
            hint_normalized = _normalize(hint)
            if hint_normalized and hint_normalized in normalized:
                score = 0.74
                if score > best_score:
                    best_field = standard
                    best_score = score
                    best_reason = f"header hint:{hint}"

    if best_score >= 0.68:
        return FieldSuggestion(header, best_field, round(best_score, 2), best_reason)
    return FieldSuggestion(header, "", 0.0, best_reason)


def _infer_source_type(
    path: Path,
    fields: list[FieldSuggestion],
    headers: list[str],
) -> tuple[str, float, list[str]]:
    scores = {source_type: 0.0 for source_type in SOURCE_FIELD_WEIGHTS}
    reasons: dict[str, list[str]] = {source_type: [] for source_type in SOURCE_FIELD_WEIGHTS}
    field_names = {field.standard_field for field in fields if field.standard_field}
    name_text = _normalize(path.stem)
    header_text = " ".join(_normalize(header) for header in headers)

    for source_type, weights in SOURCE_FIELD_WEIGHTS.items():
        for field_name, weight in weights.items():
            if field_name in field_names:
                scores[source_type] += weight
                reasons[source_type].append(f"field:{field_name}")
        for hint in SOURCE_NAME_HINTS[source_type]:
            normalized_hint = _normalize(hint)
            if normalized_hint and (normalized_hint in name_text or normalized_hint in header_text):
                scores[source_type] += 3
                reasons[source_type].append(f"hint:{hint}")

    best_source = max(scores, key=scores.get)
    best_score = scores[best_source]
    if best_score <= 0:
        fallback = _slug(path.stem)
        return fallback, 0.25, ["fallback:file_stem"]
    confidence = min(best_score / 13, 1.0)
    return best_source, confidence, reasons[best_source]


def _low_field_coverage(fields: list[FieldSuggestion]) -> bool:
    matched = [field for field in fields if field.standard_field]
    if not matched:
        return True
    has_identity = any(field.standard_field in {"item_code", "item_name", "account", "partner"} for field in matched)
    has_quantity = any(field.standard_field in QUANTITY_FIELDS for field in matched)
    return not (has_identity and has_quantity)


def _model_payload(path: Path, headers: list[str], preview: list[dict[str, object]]) -> dict[str, Any]:
    return {
        "file_name": path.name,
        "allowed_standard_fields": list(STANDARD_FIELDS),
        "known_source_types": list(SOURCE_FIELD_WEIGHTS),
        "headers": headers,
        "column_shapes": {
            header: _column_shape([row.get(header) for row in preview[:8]])
            for header in headers
        },
        "instructions": {
            "field_mapping_shape": "object where keys are original headers and values are allowed standard fields",
            "source_type_shape": "one known source type or a short snake_case source type",
        },
    }


def _column_shape(values: list[object]) -> dict[str, int]:
    shape = {"blank": 0, "number": 0, "date_like": 0, "short_text": 0, "long_text": 0}
    for value in values:
        text = str(value or "").strip()
        if not text:
            shape["blank"] += 1
        elif _is_number(text):
            shape["number"] += 1
        elif _looks_like_date(text):
            shape["date_like"] += 1
        elif len(text) <= 32:
            shape["short_text"] += 1
        else:
            shape["long_text"] += 1
    return shape


def _merge_model_suggestion(
    suggestion: dict[str, Any],
    *,
    fallback_source: str,
    fallback_confidence: float,
    fallback_reasons: list[str],
    fields: list[FieldSuggestion],
) -> tuple[str, float, list[str], list[FieldSuggestion]]:
    source_type = _slug(str(suggestion.get("source_type") or fallback_source))
    confidence = _bounded_float(suggestion.get("confidence"), default=max(fallback_confidence, 0.6))
    reasons = list(fallback_reasons) + ["model_boundary_help"]
    mapping = suggestion.get("field_mapping", {})
    if not isinstance(mapping, dict):
        return source_type, confidence, reasons, fields

    updated: list[FieldSuggestion] = []
    for field in fields:
        model_field = str(mapping.get(field.header, "")).strip()
        if model_field in STANDARD_FIELDS and (not field.standard_field or field.confidence < 0.82):
            updated.append(FieldSuggestion(field.header, model_field, max(field.confidence, 0.78), "model suggestion", "model"))
        else:
            updated.append(field)
    return source_type, confidence, reasons, updated


def _merge_file_signature(file_types: dict[str, dict[str, list[str]]], source_type: str, path: Path, headers: list[str]) -> None:
    signature = file_types.setdefault(source_type, {"headers": [], "values": [], "filename": []})
    for header in headers:
        _append_unique(signature["headers"], header)
    for token in _filename_tokens(path.stem):
        _append_unique(signature["filename"], token)


def _build_metrics(files: list[FileAdaptation]) -> dict[str, Any]:
    metric_specs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for file in files:
        count_key = f"{file.source_type}_records"
        if count_key not in seen:
            metric_specs.append({
                "key": count_key,
                "label": _label(file.source_type, "Records"),
                "type": "count",
                "source_type": file.source_type,
            })
            seen.add(count_key)
        for field in file.fields:
            if field.standard_field not in QUANTITY_FIELDS:
                continue
            key = f"{file.source_type}_{field.standard_field}_sum"
            if key in seen:
                continue
            metric_specs.append({
                "key": key,
                "label": _label(file.source_type, field.standard_field.replace("_", " ")),
                "type": "sum",
                "source_type": file.source_type,
                "field": field.standard_field,
                "unit": "units",
            })
            seen.add(key)
    if not metric_specs:
        metric_specs.append({"key": "records", "label": "Records", "type": "count"})
    return {"profile": "operations-data-workbench.adapted.v1", "metrics": metric_specs}


def _extract_response_content(payload: dict[str, Any]) -> Any:
    if "field_mapping" in payload or "source_type" in payload:
        return payload
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict):
            return message.get("content")
    return None


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_unique(values: list[str], value: str) -> None:
    clean = str(value or "").strip()
    if clean and clean not in values:
        values.append(clean)


def _filename_tokens(stem: str) -> list[str]:
    return [token for token in re.split(r"[^A-Za-z0-9\u4e00-\u9fff]+", stem) if token]


def _normalize(value: str) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"\([^)]*\)", "", text)
    return re.sub(r"[\s_\-/\\.]+", "", text)


def _slug(value: str) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "table"


def _label(source_type: str, suffix: str) -> str:
    return f"{source_type.replace('_', ' ').title()} {suffix.title()}"


def _bounded_float(value: object, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return min(max(number, 0.0), 1.0)


def _is_number(value: str) -> bool:
    try:
        float(value.replace(",", ""))
    except ValueError:
        return False
    return True


def _looks_like_date(value: str) -> bool:
    return bool(re.search(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", value))

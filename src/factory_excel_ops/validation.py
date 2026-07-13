"""Validate profile configuration before running the pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .metrics import load_metric_specs


ALLOWED_METRIC_TYPES = {
    "count",
    "count_group_gte",
    "count_group_lte",
    "distinct_count",
    "sum",
}


@dataclass
class ValidationResult:
    """Result object returned by config validation."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def extend(self, other: "ValidationResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def validate_profile(file_types: Path, field_mapping: Path, metrics: Path) -> ValidationResult:
    """Validate source signatures, field aliases, and metric specs together."""

    result = ValidationResult()
    source_types: set[str] = set()
    standard_fields: set[str] = set()

    file_types_payload = _load_json(file_types, result, label="file types")
    if file_types_payload is not None:
        file_types_result, source_types = validate_file_types(file_types_payload)
        result.extend(file_types_result)

    field_mapping_payload = _load_json(field_mapping, result, label="field mapping")
    if field_mapping_payload is not None:
        field_mapping_result, standard_fields = validate_field_mapping(field_mapping_payload)
        result.extend(field_mapping_result)

    if metrics.exists():
        metric_result = validate_metric_file(metrics, source_types, standard_fields)
        result.extend(metric_result)
    else:
        result.errors.append(f"metrics config not found: {metrics}")

    return result


def validate_file_types(payload: Any) -> tuple[ValidationResult, set[str]]:
    """Validate the file-type signature config."""

    result = ValidationResult()
    source_types: set[str] = set()
    if not isinstance(payload, dict) or not payload:
        result.errors.append("file types must be a non-empty object")
        return result, source_types

    for source_type, signature in payload.items():
        source_name = str(source_type).strip()
        if not source_name:
            result.errors.append("file type key cannot be empty")
            continue
        source_types.add(source_name)
        if not isinstance(signature, dict):
            result.errors.append(f"{source_name}: signature must be an object")
            continue
        token_count = 0
        for key in ("headers", "values", "filename"):
            values = signature.get(key, [])
            if values is None:
                values = []
            if not isinstance(values, list) or any(not str(value).strip() for value in values):
                result.errors.append(f"{source_name}.{key}: must be a list of non-empty strings")
                continue
            token_count += len(values)
        if token_count == 0:
            result.errors.append(f"{source_name}: at least one signature token is required")

    return result, source_types


def validate_field_mapping(payload: Any) -> tuple[ValidationResult, set[str]]:
    """Validate the standard-field alias config."""

    result = ValidationResult()
    standard_fields: set[str] = set()
    if not isinstance(payload, dict) or not payload:
        result.errors.append("field mapping must be a non-empty object")
        return result, standard_fields

    for standard_field, aliases in payload.items():
        field_name = str(standard_field).strip()
        if not field_name:
            result.errors.append("standard field key cannot be empty")
            continue
        standard_fields.add(field_name)
        if not isinstance(aliases, list) or not aliases:
            result.errors.append(f"{field_name}: aliases must be a non-empty list")
            continue
        if any(not str(alias).strip() for alias in aliases):
            result.errors.append(f"{field_name}: aliases cannot contain empty values")

    return result, standard_fields


def validate_metric_file(metrics_path: Path, source_types: set[str], standard_fields: set[str]) -> ValidationResult:
    """Validate metric config loaded from disk."""

    result = ValidationResult()
    try:
        metric_specs = load_metric_specs(metrics_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result.errors.append(f"metrics config is invalid: {exc}")
        return result

    seen_keys: set[str] = set()
    for index, spec in enumerate(metric_specs, start=1):
        location = f"metric[{index}]"
        key = str(spec.get("key", "")).strip()
        metric_type = str(spec.get("type", "")).strip()

        if not key:
            result.errors.append(f"{location}: key is required")
        elif key in seen_keys:
            result.errors.append(f"{location}: duplicate key '{key}'")
        else:
            seen_keys.add(key)

        if metric_type not in ALLOWED_METRIC_TYPES:
            result.errors.append(f"{location}: unsupported type '{metric_type}'")

        for source_type in _as_list(spec.get("source_type")):
            if source_types and source_type not in source_types:
                result.warnings.append(f"{location}: source_type '{source_type}' is not declared in file types")

        for field_name in _referenced_fields(spec):
            if standard_fields and field_name not in standard_fields:
                result.warnings.append(f"{location}: field '{field_name}' is not declared in field mapping")

    if not metric_specs:
        result.errors.append("metrics config must contain at least one metric")

    return result


def _load_json(path: Path, result: ValidationResult, label: str) -> Any:
    if not path.exists():
        result.errors.append(f"{label} config not found: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.errors.append(f"{label} config is invalid: {exc}")
        return None


def _as_list(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _referenced_fields(spec: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    for key in ("field", "group_by", "value_field"):
        value = str(spec.get(key, "")).strip()
        if value:
            fields.append(value)
    return fields

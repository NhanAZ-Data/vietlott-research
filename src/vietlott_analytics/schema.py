from __future__ import annotations

from typing import Any

ANALYSIS_EXPORT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://nhanaz.github.io/vietlott-data-research/data/analysis-export.schema.json",
    "title": "Vietlott Research Analysis Export",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "export_type",
        "language",
        "generated_from_dataset_at",
        "purpose",
        "manifest",
        "dataset_summary",
        "dataset_quality",
        "snapshot_manifest",
        "data_dictionary",
        "methodology",
        "source_files",
        "raw_data_catalog",
        "product_reports",
        "predictions",
        "audit_summary",
        "audit_events",
    ],
    "properties": {
        "schema_version": {"const": 2},
        "export_type": {"const": "vietlott_research_analysis"},
        "language": {"const": "vi"},
        "generated_from_dataset_at": {"type": ["string", "null"]},
        "purpose": {"type": "string", "minLength": 1},
        "manifest": {"type": "object"},
        "dataset_summary": {"type": "object"},
        "dataset_quality": {"type": "object"},
        "snapshot_manifest": {"type": "object"},
        "data_dictionary": {"type": "object"},
        "methodology": {
            "type": "object",
            "required": ["versions", "backtest", "fairness_audit"],
            "properties": {
                "versions": {"type": "object"},
                "backtest": {"type": "object"},
                "fairness_audit": {"type": "object"},
            },
        },
        "source_files": {"type": "object"},
        "raw_data_catalog": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "bytes", "sha256"],
                "properties": {
                    "path": {"type": "string"},
                    "bytes": {"type": "integer", "minimum": 0},
                    "sha256": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                    "data_rows": {"type": "integer", "minimum": 0},
                },
            },
        },
        "product_reports": {"type": "object", "minProperties": 1},
        "predictions": {"type": "object"},
        "audit_summary": {"type": "object"},
        "audit_events": {"type": "array"},
    },
}

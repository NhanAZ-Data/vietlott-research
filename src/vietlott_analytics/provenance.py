from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class StructuralValidity(StrEnum):
    VALID = "valid"
    WARNING = "warning"
    UNCHECKED = "unchecked"


class SourceOrigin(StrEnum):
    OFFICIAL = "official"
    SECONDARY = "secondary"
    COMMUNITY = "community"
    UNKNOWN = "unknown"


class SourceVerification(StrEnum):
    OFFICIAL_DIRECT = "official_direct"
    OFFICIAL_VERIFIED_MATCH = "official_verified_match"
    MULTI_SOURCE_CONSENSUS = "multi_source_consensus"
    PENDING_OFFICIAL = "pending_official"
    SINGLE_SECONDARY_SOURCE = "single_secondary_source"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ProvenanceAssessment:
    structural_validity: StructuralValidity
    source_origin: SourceOrigin
    source_verification: SourceVerification
    is_official_source: bool
    is_cross_checked: bool


def assess_provenance(row: dict[str, Any]) -> ProvenanceAssessment:
    attributes = _json_object(row.get("attributes_json"))
    validation = _structural_validity(row.get("validation_status"))
    origin = _source_origin(attributes)
    verification = _source_verification(origin, attributes)
    return ProvenanceAssessment(
        structural_validity=validation,
        source_origin=origin,
        source_verification=verification,
        is_official_source=origin is SourceOrigin.OFFICIAL,
        is_cross_checked=verification
        in {
            SourceVerification.OFFICIAL_VERIFIED_MATCH,
            SourceVerification.MULTI_SOURCE_CONSENSUS,
        },
    )


def _structural_validity(value: object) -> StructuralValidity:
    text = str(value or StructuralValidity.UNCHECKED)
    try:
        return StructuralValidity(text)
    except ValueError:
        return StructuralValidity.UNCHECKED


def _source_origin(attributes: dict[str, Any]) -> SourceOrigin:
    data_source = str(attributes.get("data_source", "")).lower()
    if data_source == "official_vietlott":
        return SourceOrigin.OFFICIAL
    if data_source == "community_mirror":
        return SourceOrigin.COMMUNITY
    if data_source and data_source != "unknown":
        return SourceOrigin.SECONDARY
    if attributes.get("official_list_verified_at"):
        return SourceOrigin.OFFICIAL
    if attributes.get("secondary_source_url"):
        return SourceOrigin.SECONDARY
    return SourceOrigin.UNKNOWN


def _source_verification(
    origin: SourceOrigin,
    attributes: dict[str, Any],
) -> SourceVerification:
    history = attributes.get("source_history")
    has_history = isinstance(history, list) and bool(history)
    if origin is SourceOrigin.OFFICIAL:
        if attributes.get("official_list_verified_at") or has_history:
            return SourceVerification.OFFICIAL_VERIFIED_MATCH
        return SourceVerification.OFFICIAL_DIRECT
    if attributes.get("consensus_sources") or attributes.get("data_source") == "gap_consensus":
        return SourceVerification.MULTI_SOURCE_CONSENSUS
    if attributes.get("official_verification_status") == "pending":
        return SourceVerification.PENDING_OFFICIAL
    if origin in {SourceOrigin.SECONDARY, SourceOrigin.COMMUNITY}:
        return SourceVerification.SINGLE_SECONDARY_SOURCE
    return SourceVerification.UNKNOWN


def _json_object(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if not value:
        return {}
    try:
        parsed = json.loads(str(value))
    except (json.JSONDecodeError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}

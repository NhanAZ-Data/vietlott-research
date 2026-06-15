from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class DrawConfirmation(StrEnum):
    """Whether an issued draw is accepted for statistical analysis."""

    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"


class StructuralValidity(StrEnum):
    """Result of deterministic schema and game-rule validation."""

    VALID = "valid"
    WARNING = "warning"
    UNCHECKED = "unchecked"


class SourceOrigin(StrEnum):
    """Origin of the canonical row, independent of its structural validity."""

    OFFICIAL = "official"
    SECONDARY = "secondary"
    COMMUNITY = "community"
    UNKNOWN = "unknown"


class SourceVerification(StrEnum):
    """How much source-to-source verification is visible in stored metadata."""

    OFFICIAL_DIRECT = "official_direct"
    OFFICIAL_VERIFIED_MATCH = "official_verified_match"
    MULTI_SOURCE_CONSENSUS = "multi_source_consensus"
    PENDING_OFFICIAL = "pending_official"
    SINGLE_SECONDARY_SOURCE = "single_secondary_source"
    UNKNOWN = "unknown"


class StatusEvidence(StrEnum):
    """Evidence required when draw confirmation changes."""

    NONE = "none"
    OFFICIAL_NOTICE = "official_notice"
    OFFICIAL_REINSTATEMENT = "official_reinstatement"


@dataclass(frozen=True, slots=True)
class ProvenanceAssessment:
    structural_validity: StructuralValidity
    source_origin: SourceOrigin
    source_verification: SourceVerification
    is_official_source: bool
    is_cross_checked: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "structural_validity": self.structural_validity.value,
            "source_origin": self.source_origin.value,
            "source_verification": self.source_verification.value,
            "is_official_source": self.is_official_source,
            "is_cross_checked": self.is_cross_checked,
        }


def validate_draw_status_transition(
    current: str,
    target: str,
    evidence: str = StatusEvidence.NONE,
) -> None:
    """Reject confirmation changes that do not carry appropriate evidence."""

    current_status = DrawConfirmation(current)
    target_status = DrawConfirmation(target)
    evidence_status = StatusEvidence(evidence)
    if current_status == target_status:
        return
    if (
        current_status is DrawConfirmation.CONFIRMED
        and target_status is DrawConfirmation.NOT_CONFIRMED
        and evidence_status is StatusEvidence.OFFICIAL_NOTICE
    ):
        return
    if (
        current_status is DrawConfirmation.NOT_CONFIRMED
        and target_status is DrawConfirmation.CONFIRMED
        and evidence_status is StatusEvidence.OFFICIAL_REINSTATEMENT
    ):
        return
    raise ValueError(
        f"Transition {current_status.value} -> {target_status.value} "
        f"requires official evidence"
    )


def assess_provenance(row: dict[str, Any]) -> ProvenanceAssessment:
    attributes = _json_object(row.get("attributes_json"))
    validation = _structural_validity(row.get("validation_status"))
    origin = _source_origin(row, attributes)
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


def append_source_history(
    attributes: dict[str, Any],
    *,
    source_url: str,
    data_source: str,
    draw_date: str,
    result_json: str,
    observed_at: str,
) -> dict[str, Any]:
    """Preserve a compact unique observation before replacing a canonical row."""

    history = attributes.get("source_history")
    if not isinstance(history, list):
        history = []
    observation = {
        "data_source": data_source or "unknown",
        "source_url": source_url,
        "draw_date": draw_date,
        "result_json": result_json,
        "observed_at": observed_at,
    }
    identity = (
        observation["data_source"],
        observation["source_url"],
        observation["draw_date"],
        observation["result_json"],
    )
    known = {
        (
            str(item.get("data_source", "")),
            str(item.get("source_url", "")),
            str(item.get("draw_date", "")),
            str(item.get("result_json", "")),
        )
        for item in history
        if isinstance(item, dict)
    }
    if identity not in known:
        history.append(observation)
    attributes["source_history"] = history
    return attributes


def _structural_validity(value: object) -> StructuralValidity:
    text = str(value or StructuralValidity.UNCHECKED)
    try:
        return StructuralValidity(text)
    except ValueError:
        return StructuralValidity.UNCHECKED


def _source_origin(
    row: dict[str, Any],
    attributes: dict[str, Any],
) -> SourceOrigin:
    data_source = str(attributes.get("data_source", "")).lower()
    if data_source == "official_vietlott":
        return SourceOrigin.OFFICIAL
    if data_source == "community_mirror":
        return SourceOrigin.COMMUNITY
    if data_source and data_source != "unknown":
        return SourceOrigin.SECONDARY
    if not data_source and attributes.get("official_list_verified_at"):
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

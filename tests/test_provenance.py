from __future__ import annotations

import json

import pytest

from vietlott_collector.provenance import (
    SourceOrigin,
    SourceVerification,
    StatusEvidence,
    StructuralValidity,
    assess_provenance,
    validate_draw_status_transition,
)


def test_provenance_keeps_explicit_community_label_over_canonical_url() -> None:
    row = {
        "source_url": "https://vietlott.vn/example?id=1",
        "validation_status": "valid",
        "attributes_json": json.dumps(
            {
                "data_source": "community_mirror",
                "secondary_source_url": "https://example.test/mirror",
            }
        ),
    }

    assessment = assess_provenance(row)

    assert assessment.structural_validity is StructuralValidity.VALID
    assert assessment.source_origin is SourceOrigin.COMMUNITY
    assert assessment.source_verification is SourceVerification.SINGLE_SECONDARY_SOURCE
    assert assessment.is_official_source is False
    assert assessment.is_cross_checked is False


def test_provenance_distinguishes_official_match_from_official_direct() -> None:
    direct = assess_provenance(
        {
            "source_url": "https://vietlott.vn/example?id=1",
            "validation_status": "valid",
            "attributes_json": '{"data_source":"official_vietlott"}',
        }
    )
    matched = assess_provenance(
        {
            "source_url": "https://vietlott.vn/example?id=1",
            "validation_status": "valid",
            "attributes_json": json.dumps(
                {
                    "data_source": "official_vietlott",
                    "official_list_verified_at": "2026-06-15T00:00:00+00:00",
                }
            ),
        }
    )

    assert direct.source_verification is SourceVerification.OFFICIAL_DIRECT
    assert matched.source_verification is SourceVerification.OFFICIAL_VERIFIED_MATCH
    assert matched.is_cross_checked is True


def test_unlabelled_legacy_row_is_not_promoted_by_url_alone() -> None:
    assessment = assess_provenance(
        {
            "source_url": "https://vietlott.vn/example?id=1",
            "validation_status": "unchecked",
            "attributes_json": "{}",
        }
    )

    assert assessment.source_origin is SourceOrigin.UNKNOWN
    assert assessment.source_verification is SourceVerification.UNKNOWN


@pytest.mark.parametrize(
    ("current", "target", "evidence"),
    [
        ("confirmed", "confirmed", StatusEvidence.NONE),
        ("not_confirmed", "not_confirmed", StatusEvidence.NONE),
        ("confirmed", "not_confirmed", StatusEvidence.OFFICIAL_NOTICE),
        (
            "not_confirmed",
            "confirmed",
            StatusEvidence.OFFICIAL_REINSTATEMENT,
        ),
    ],
)
def test_valid_draw_status_transitions(
    current: str,
    target: str,
    evidence: StatusEvidence,
) -> None:
    validate_draw_status_transition(current, target, evidence)


@pytest.mark.parametrize(
    ("current", "target", "evidence"),
    [
        ("confirmed", "not_confirmed", StatusEvidence.NONE),
        ("not_confirmed", "confirmed", StatusEvidence.NONE),
        ("confirmed", "not_confirmed", StatusEvidence.OFFICIAL_REINSTATEMENT),
    ],
)
def test_invalid_draw_status_transitions_are_rejected(
    current: str,
    target: str,
    evidence: StatusEvidence,
) -> None:
    with pytest.raises(ValueError, match="requires official evidence"):
        validate_draw_status_transition(current, target, evidence)

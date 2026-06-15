from __future__ import annotations

from datetime import date

from scripts.check_quality_regressions import compare_quality_reports


def _report(
    *,
    rows: int = 100,
    unknown: int = 0,
    secondary: int = 0,
    pending_official: int = 0,
    not_confirmed: int = 0,
    last_date: str = "2026-06-15",
) -> dict[str, object]:
    return {
        "products": {
            "keno": {
                "rows": rows,
                "last_date": last_date,
                "source_origin": {"unknown": unknown},
                "source_verification": {
                    "unknown": unknown,
                    "single_secondary_source": secondary,
                    "pending_official": pending_official,
                },
                "draw_confirmation": {"not_confirmed": not_confirmed},
            }
        }
    }


def test_quality_monitor_reports_regressions_without_calling_them_missing_draws() -> None:
    alerts = compare_quality_reports(
        _report(),
        _report(
            rows=110,
            unknown=2,
            secondary=10,
            not_confirmed=3,
            last_date="2026-06-10",
        ),
        reference_date=date(2026, 6, 15),
    )

    assert {alert.code for alert in alerts} == {
        "source_stale",
        "unknown_source_increased",
        "secondary_source_rate_increased",
        "not_confirmed_increased",
    }
    assert "không khẳng định kỳ quay bị thiếu" in alerts[0].message


def test_quality_monitor_accepts_growth_without_rate_regression() -> None:
    alerts = compare_quality_reports(
        _report(rows=100, secondary=10),
        _report(rows=200, secondary=20),
        reference_date=date(2026, 6, 15),
    )

    assert alerts == []

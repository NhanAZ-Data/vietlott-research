from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dataset_workflow_preserves_before_and_after_diagnostics() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "update-dataset.yml"
    ).read_text(encoding="utf-8")

    assert "vietlott-reports/before" in workflow
    assert 'after_dir="$report_dir/after"' in workflow
    assert "vietlott-repository-data audit" in workflow
    assert "check_quality_regressions.py" in workflow
    assert "quality-regressions.json" in workflow
    assert "actions/upload-artifact@v7" in workflow


def test_weather_workflow_preserves_before_and_after_diagnostics() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "update-weather.yml"
    ).read_text(encoding="utf-8")

    assert "vietlott-weather-reports/before" in workflow
    assert "vietlott-weather-reports/after" in workflow
    assert "vietlott-repository-data audit" in workflow
    assert "actions/upload-artifact@v7" in workflow

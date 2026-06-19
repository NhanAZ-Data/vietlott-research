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
    assert "site/data" not in workflow
    assert "vietlott-research-report" not in workflow


def test_collector_workflows_do_not_request_pages_permissions() -> None:
    workflows = [
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "update-dataset.yml",
        ROOT / ".github" / "workflows" / "update-fast.yml",
        ROOT / ".github" / "workflows" / "update-scheduled.yml",
    ]

    for path in workflows:
        workflow = path.read_text(encoding="utf-8")
        assert "pages: write" not in workflow
        assert "id-token: write" not in workflow

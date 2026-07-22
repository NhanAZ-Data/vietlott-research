from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_collector_and_analytics_are_distributed_together() -> None:
    assert (ROOT / "src" / "vietlott_collector" / "__init__.py").is_file()
    assert (ROOT / "src" / "vietlott_analytics" / "__init__.py").is_file()
    assert (ROOT / "datasets" / "metadata" / "snapshot-manifest.json").is_file()
    assert (ROOT / "site" / "index.html").is_file()


def test_pages_workflow_uses_the_local_canonical_dataset() -> None:
    workflow = (ROOT / ".github" / "workflows" / "build-pages.yml").read_text(
        encoding="utf-8"
    )

    assert "--datasets-dir datasets" in workflow
    assert "_data_repo" not in workflow
    assert "NhanAZ-Data/vietlott-data-research" not in workflow


def test_readme_points_to_the_merged_repository() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "NhanAZ-Data/vietlott-research" in readme
    assert "NhanAZ-Data/vietlott-data-research" not in readme
    assert "NhanAZ-Data/vietlott-prediction-web" not in readme

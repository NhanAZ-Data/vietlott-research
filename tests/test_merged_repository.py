from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repository_is_collector_only() -> None:
    assert (ROOT / "src" / "vietlott_collector" / "__init__.py").is_file()
    assert not (ROOT / "src" / "vietlott_analytics").exists()
    assert not (ROOT / "site").exists()
    assert not (ROOT / "predictions").exists()


def test_project_identity_is_data_collector() -> None:
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert 'name = "vietlott-data-collector"' in project
    assert 'vietlott-data-collector = "vietlott_collector.cli:main"' in project
    assert 'vietlott-dataset = "vietlott_collector.repository_data:main"' in project
    assert "vietlott-research-report" not in project
    assert "Vietlott Data Collector" in readme
    assert "NhanAZ-Data/vietlott-prediction-web" not in readme

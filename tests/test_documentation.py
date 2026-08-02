from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_collector_documentation_exists() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "docs" / "DATA_DICTIONARY.md",
        ROOT / "docs" / "THU_THAP_DU_LIEU.md",
        ROOT / "docs" / "CHAT_LUONG_DU_LIEU.md",
        ROOT / "docs" / "TU_DONG_CAP_NHAT.md",
        ROOT / "docs" / "ARCHITECTURE.md",
        ROOT / "docs" / "SOURCE_SURVEY.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "loi-du-lieu.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "loi-nguon.yml",
    ]

    for path in required:
        assert path.is_file(), path
        assert path.read_text(encoding="utf-8").strip(), path


def test_readme_describes_only_reusable_collection_outputs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "datasets/draws/<product>",
        "datasets/metadata/quality-report.json",
        "vietlott-collector collect",
        "vietlott-repository-data hydrate",
        "docs/DATA_DICTIONARY.md",
    ):
        assert expected in readme

    for removed_reference in (
        "site/data",
        "predictions/ledger.jsonl",
        "vietlott-research-report",
        "GitHub Pages",
    ):
        assert removed_reference not in readme


def test_removed_research_artifacts_have_no_documentation_links() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "docs").rglob("*.md")
    )

    for removed_reference in (
        "src/vietlott_analytics",
        "analysis-export.json",
        "predictions.json",
        "BACKTEST_",
        "AUDIT_",
        "DU_DOAN_",
    ):
        assert removed_reference not in readme
        assert removed_reference not in docs

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_collector_documentation_exists() -> None:
    required = [
        ROOT / "docs" / "DATA_DICTIONARY.md",
        ROOT / "docs" / "THU_THAP_DU_LIEU.md",
        ROOT / "docs" / "CHAT_LUONG_DU_LIEU.md",
        ROOT / "docs" / "TU_DONG_CAP_NHAT.md",
        ROOT / "docs" / "SOURCE_SURVEY.md",
        ROOT / "docs" / "ARCHITECTURE.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "loi-du-lieu.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "loi-nguon.yml",
    ]

    for path in required:
        assert path.is_file(), path
        assert path.read_text(encoding="utf-8").strip(), path


def test_readme_points_to_split_web_repo_and_collector_docs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "NhanAZ-Data/vietlott-prediction-web" in readme
    assert "docs/THU_THAP_DU_LIEU.md" in readme
    assert "docs/CHAT_LUONG_DU_LIEU.md" in readme
    assert "docs/TU_DONG_CAP_NHAT.md" in readme
    assert "vietlott-research-report" not in readme

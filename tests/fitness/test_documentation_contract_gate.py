"""اختبارات سلبية لعقد التوثيق الحي."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.fitness import check_documentation_contract as gate


def test_check_documentation_contract_rejects_missing_manifest_document(
    tmp_path: Path, monkeypatch
) -> None:
    """الوثيقة الحية المسجلة لكنها غير موجودة يجب أن تُسقط البوابة."""
    docs = tmp_path / "docs"
    docs.mkdir()
    manifest = docs / "DOCUMENTATION_MANIFEST.json"
    manifest.write_text(
        json.dumps(
            {
                "documents": [
                    {"path": "docs/missing.md", "status": "live", "role": "test"}
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gate, "MANIFEST", manifest)

    failures: list[str] = []
    entries = gate._check_manifest(failures)

    assert entries == [("docs/missing.md", "test")]
    assert any("وثيقة manifest مفقودة" in failure for failure in failures)
    assert len(failures) >= 1

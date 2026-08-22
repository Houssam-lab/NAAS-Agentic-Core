"""بوابة عقد التوثيق الحي.

لا تحاول هذه البوابة إثبات أن كل جملة صحيحة دلاليًا؛ بل تمنع أكثر أشكال
الانحراف قابلية للكشف: ملفات manifest مفقودة، روابط محلية مكسورة، أوامر
تثبيت قديمة، وتعليمات تخالف حد التغطية والأوامر التنفيذية الحالية. الفشل
صريح ومقصود: لا تحذيرات تسمح بالمرور ولا استثناءات مخفية.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "docs/DOCUMENTATION_MANIFEST.json"
MAKEFILE = REPO_ROOT / "Makefile"
CI_WORKFLOW = REPO_ROOT / ".github/workflows/ci.yml"
DOC_WORKFLOW = REPO_ROOT / ".github/workflows/doc_integrity.yml"

_LINK = re.compile(r"\]\(([^)]+)\)")
_STALE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("ai-for-solution-labs/my_ai_project", "اسم مستودع تاريخي في تعليمات تشغيلية"),
    ("HOUSSAM16ai/my_ai_project", "اسم مستودع تاريخي في تعليمات تشغيلية"),
    ("cd my_ai_project", "مجلد مشروع تاريخي في أمر تشغيل"),
    ("TROUBLESHOOTING.md", "رابط إلى دليل غير معياري"),
    ("ARCHITECTURE_ANALYSIS.md", "رابط إلى دليل غير معياري"),
    ("cov-fail-under=100", "حد تغطية قديم يخالف المصدر التنفيذي"),
    ("mypy is not yet in CI", "ادعاء قديم عن CI"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_local_target(raw_target: str) -> bool:
    target = raw_target.strip().split(None, 1)[0].strip("<>")
    return not target.startswith(("http://", "https://", "mailto:", "#"))


def _target_path(document: Path, raw_target: str) -> Path:
    target = raw_target.strip().split(None, 1)[0].strip("<>")
    target = target.split("#", 1)[0]
    return (document.parent / target).resolve()


def _check_manifest(failures: list[str]) -> list[tuple[str, str]]:
    if not MANIFEST.is_file():
        failures.append("❌ ملف manifest مفقود: docs/DOCUMENTATION_MANIFEST.json")
        return []
    try:
        payload = json.loads(_read(MANIFEST))
    except json.JSONDecodeError as error:
        failures.append(f"❌ manifest غير صالح JSON: {error}")
        return []

    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        failures.append("❌ manifest يجب أن يحتوي على قائمة documents غير فارغة.")
        return []

    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for entry in documents:
        if not isinstance(entry, dict):
            failures.append("❌ كل عنصر في manifest يجب أن يكون كائنًا.")
            continue
        path = entry.get("path")
        status = entry.get("status")
        if not isinstance(path, str) or not path:
            failures.append("❌ عنصر manifest بلا path صالح.")
            continue
        if path in seen:
            failures.append(f"❌ المسار مكرر في manifest: {path}")
        seen.add(path)
        if status != "live":
            failures.append(f"❌ كل وثيقة في manifest يجب أن تكون live: {path}")
        absolute = REPO_ROOT / path
        if not absolute.is_file():
            failures.append(f"❌ وثيقة manifest مفقودة: {path}")
        entries.append((path, entry.get("role", "")))

    required = {
        "README.md",
        "docs/START_HERE.md",
        "docs/quality/testing.md",
        "CONTRIBUTING.md",
        "AGENTS.md",
        "docs/DOCUMENTATION_INDEX.md",
        "docs/DOCUMENTATION_CONTRACT.md",
    }
    actual = {path for path, _ in entries}
    for path in sorted(required - actual):
        failures.append(f"❌ وثيقة حية إلزامية غير مسجلة في manifest: {path}")
    return entries


def _check_links_and_stale_text(
    entries: list[tuple[str, str]], failures: list[str]
) -> None:
    for rel_path, _ in entries:
        document = REPO_ROOT / rel_path
        if not document.is_file() or document.suffix.lower() != ".md":
            continue
        # The contract documents forbidden examples so agents can recognize them;
        # those examples are policy text, not operational instructions to follow.
        scan_for_stale_text = rel_path != "docs/DOCUMENTATION_CONTRACT.md"
        text = _read(document)
        if scan_for_stale_text:
            for pattern, reason in _STALE_PATTERNS:
                if pattern in text:
                    failures.append(f"❌ {rel_path}: {reason} — وُجد {pattern!r}")
        for raw_target in sorted(set(_LINK.findall(text))):
            if not _is_local_target(raw_target):
                continue
            target = _target_path(document, raw_target)
            if not target.exists():
                failures.append(
                    f"❌ {rel_path}: رابط محلي مكسور {raw_target!r} "
                    f"(المسار المحلّل: {target.relative_to(REPO_ROOT)})"
                )


def _check_executable_truth(failures: list[str]) -> None:
    makefile = _read(MAKEFILE)
    workflow = _read(CI_WORKFLOW)
    doc_workflow = _read(DOC_WORKFLOW)

    if "test:" not in makefile or "--cov=app" not in makefile:
        failures.append("❌ Makefile لا يثبت أن make test يقيس نطاق app.")
    if "--cov-fail-under=73" not in makefile:
        failures.append("❌ Makefile لا يثبت حد التغطية التنفيذي 73.")
    if "--cov-fail-under=73" not in workflow:
        failures.append("❌ CI لا يثبت حد التغطية التنفيذي 73.")
    if "check_documentation_contract.py" not in workflow:
        failures.append("❌ بوابة التوثيق غير مربوطة بمسار required-ci.")
    if "check_documentation_contract.py" not in doc_workflow:
        failures.append("❌ بوابة doc-integrity لا تشغّل عقد التوثيق.")
    index = _read(REPO_ROOT / "docs/DOCUMENTATION_INDEX.md")
    agents = _read(REPO_ROOT / "AGENTS.md")
    contributing = _read(REPO_ROOT / "CONTRIBUTING.md")
    if "DOCUMENTATION_CONTRACT.md" not in index or "DOCUMENTATION_MANIFEST.json" not in index:
        failures.append("❌ الفهرس المركزي لا يربط عقد التوثيق وmanifest.")
    if "docs/DOCUMENTATION_CONTRACT.md" not in agents:
        failures.append("❌ AGENTS.md لا يفرض عقد التوثيق على الوكلاء.")
    if "check_documentation_contract.py" not in contributing:
        failures.append("❌ CONTRIBUTING.md لا يطلب فحص عقد التوثيق.")
    if "continue-on-error: true" in doc_workflow:
        failures.append("❌ بوابة doc-integrity تحتوي continue-on-error؛ لا يسمح بالتجاوز الصامت.")


def main() -> int:
    failures: list[str] = []
    entries = _check_manifest(failures)
    _check_links_and_stale_text(entries, failures)
    _check_executable_truth(failures)

    if failures:
        print("\n".join(failures))
        print(f"\n❌ check_documentation_contract: {len(failures)} انتهاكًا.")
        return 1

    print(
        f"✅ عقد التوثيق سليم: {len(entries)} وثائق حية، "
        "الروابط والمسارات والأوامر الأساسية متسقة."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

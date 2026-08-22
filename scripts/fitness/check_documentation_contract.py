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
BRANCH_POLICY = REPO_ROOT / ".github/branch-protection-policy.json"
CODEOWNERS = REPO_ROOT / ".github/CODEOWNERS"

_LINK = re.compile(r"]\(([^)]+)\)")
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


def _load_manifest(failures: list[str]) -> dict:
    if not MANIFEST.is_file():
        failures.append("❌ ملف manifest مفقود: docs/DOCUMENTATION_MANIFEST.json")
        return {}
    try:
        payload = json.loads(_read(MANIFEST))
    except json.JSONDecodeError as error:
        failures.append(f"❌ manifest غير صالح JSON: {error}")
        return {}
    if not isinstance(payload, dict):
        failures.append("❌ manifest يجب أن يكون كائن JSON.")
        return {}
    return payload


def _validate_manifest_shape(payload: dict, failures: list[str]) -> list[dict]:
    documents = payload.get("documents")
    if not isinstance(documents, list) or not documents:
        failures.append("❌ manifest يجب أن يحتوي على قائمة documents غير فارغة.")
        return []
    for field in ("scan_globs", "exclude_globs"):
        if not isinstance(payload.get(field), list) or not payload[field]:
            failures.append(f"❌ manifest يجب أن يعلن قائمة {field} غير فارغة.")
    return [entry for entry in documents if isinstance(entry, dict)]


def _validate_manifest_entry(
    entry: dict, seen: set[str], failures: list[str]
) -> tuple[str, str] | None:
    path = entry.get("path")
    role = entry.get("role")
    audience = entry.get("audience")
    authority = entry.get("authority")
    if not isinstance(path, str) or not path:
        failures.append("❌ عنصر manifest بلا path صالح.")
        return None
    if Path(path).is_absolute() or ".." in Path(path).parts:
        failures.append(f"❌ مسار manifest خارج جذر المستودع: {path}")
    if not all(isinstance(value, str) and value.strip() for value in (role, audience)):
        failures.append(f"❌ وثيقة manifest بلا audience/role موصوفين: {path}")
    if authority not in {"primary", "supporting"}:
        failures.append(f"❌ وثيقة manifest بلا authority معتمد (primary/supporting): {path}")
    if path in seen:
        failures.append(f"❌ المسار مكرر في manifest: {path}")
    seen.add(path)
    if entry.get("status") != "live":
        failures.append(f"❌ كل وثيقة في manifest يجب أن تكون live: {path}")
    if not (REPO_ROOT / path).is_file():
        failures.append(f"❌ وثيقة manifest مفقودة: {path}")
    return path, role if isinstance(role, str) else ""


def _check_required_manifest_documents(entries: list[tuple[str, str]], failures: list[str]) -> None:
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


def _check_manifest(failures: list[str]) -> list[tuple[str, str]]:
    payload = _load_manifest(failures)
    if not payload:
        return []
    documents = _validate_manifest_shape(payload, failures)
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for entry in documents:
        validated = _validate_manifest_entry(entry, seen, failures)
        if validated is not None:
            entries.append(validated)
    _check_required_manifest_documents(entries, failures)
    return entries


def _scan_documents(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """يوسّع نطاق البيان إلى كل الوثائق الحية المعلنة في scan_globs."""
    paths: dict[str, str] = {path: role for path, role in entries}
    try:
        payload = json.loads(_read(MANIFEST))
    except json.JSONDecodeError:
        return entries
    excludes = tuple(str(item) for item in payload.get("exclude_globs", []))
    for pattern in payload.get("scan_globs", []):
        for document in REPO_ROOT.glob(str(pattern)):
            if not document.is_file() or document.suffix.lower() != ".md":
                continue
            relative = str(document.relative_to(REPO_ROOT))
            if any(
                (exclude.endswith("/**") and relative.startswith(exclude[:-3].rstrip("/") + "/"))
                or Path(relative).match(exclude)
                for exclude in excludes
            ):
                continue
            paths.setdefault(relative, "scan")
    return sorted(paths.items())


def _stale_text_failures(rel_path: str, text: str) -> list[str]:
    if rel_path == "docs/DOCUMENTATION_CONTRACT.md":
        return []
    if rel_path in {
        "docs/governance/SOURCE_ADOPTION_MATRIX.md",
        "docs/research/ALL_GITHUB_SOURCES_INVENTORY.md",
    }:
        return []
    return [
        f"❌ {rel_path}: {reason} — وُجد {pattern!r}"
        for pattern, reason in _STALE_PATTERNS
        if pattern in text
    ]


def _local_link_failures(rel_path: str, document: Path, text: str) -> list[str]:
    failures: list[str] = []
    for raw_target in sorted(set(_LINK.findall(text))):
        if not _is_local_target(raw_target):
            continue
        target = _target_path(document, raw_target)
        if target.exists():
            continue
        try:
            display_target = target.relative_to(REPO_ROOT)
        except ValueError:
            display_target = target
        failures.append(
            f"❌ {rel_path}: رابط محلي مكسور {raw_target!r} "
            f"(المسار المحلّل: {display_target})"
        )
    return failures


def _check_links_and_stale_text(
    entries: list[tuple[str, str]], failures: list[str]
) -> None:
    for rel_path, _ in _scan_documents(entries):
        document = REPO_ROOT / rel_path
        if not document.is_file() or document.suffix.lower() != ".md":
            continue
        text = _read(document)
        failures.extend(_stale_text_failures(rel_path, text))
        failures.extend(_local_link_failures(rel_path, document, text))


def _check_branch_protection_policy(failures: list[str]) -> None:
    """تحقق من السياسة المرغوبة محليًا؛ الحالة الحية تُراجع خارج المستودع بصلاحية الإدارة."""
    if not BRANCH_POLICY.is_file():
        failures.append("❌ سياسة حماية main مفقودة: .github/branch-protection-policy.json")
        return
    try:
        policy = json.loads(_read(BRANCH_POLICY))
    except json.JSONDecodeError as error:
        failures.append(f"❌ سياسة حماية main غير صالحة JSON: {error}")
        return
    required = set(policy.get("required_status_checks", {}).get("contexts", []))
    reviews = policy.get("required_pull_request_reviews", {})
    checks = {
        "branch": policy.get("branch") == "main",
        "strict_status_checks": policy.get("required_status_checks", {}).get("strict") is True,
        "required_ci": "required-ci" in required,
        "doc_integrity": "doc-integrity" in required,
        "enforce_admins": policy.get("enforce_admins") is True,
        "one_approval": reviews.get("required_approving_review_count", 0) >= 1,
        "codeowners": reviews.get("require_code_owner_reviews") is True,
        "last_push_approval": reviews.get("require_last_push_approval") is True,
        "dismiss_stale": reviews.get("dismiss_stale_reviews") is True,
        "linear_history": policy.get("required_linear_history") is True,
        "no_force_pushes": policy.get("allow_force_pushes") is False,
        "no_deletions": policy.get("allow_deletions") is False,
        "conversation_resolution": policy.get("required_conversation_resolution") is True,
    }
    for name, valid in checks.items():
        if not valid:
            failures.append(f"❌ سياسة حماية main غير مكتملة: {name}")
    if CODEOWNERS.is_file():
        owners = _read(CODEOWNERS)
        for path in ("/docs/", "/scripts/", "/.github/"):
            if path not in owners:
                failures.append(f"❌ CODEOWNERS لا يملك نطاق الحوكمة: {path}")
    else:
        failures.append("❌ CODEOWNERS مفقود؛ لا توجد مراجعة ملكية للحوكمة.")


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
    guardrails_start = workflow.find("  guardrails:")
    required_start = workflow.find("  required-ci:")
    if guardrails_start < 0 or "check_documentation_contract.py" not in workflow[guardrails_start:]:
        failures.append("❌ عقد التوثيق ليس خطوة داخل job guardrails.")
    if required_start < 0 or "guardrails," not in workflow[required_start:]:
        failures.append("❌ required-ci لا يعتمد صراحة على guardrails؛ يمكن أن يمر التوثيق منفصلًا.")
    if "set -euo pipefail" not in workflow[guardrails_start:required_start if required_start >= 0 else None]:
        failures.append("❌ guardrails لا يعمل في وضع fail-closed (set -euo pipefail مفقود).")
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
    _check_branch_protection_policy(failures)
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

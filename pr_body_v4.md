## Why

This change turns documentation acceptance into a repository-and-GitHub control plane. The previous implementation enforced the repository contract, but external quality checks exposed two remaining weaknesses: Qodana counted inherited technical debt as if it were introduced by this PR, and the PR description did not use the exact D-270 evidence structure. This update establishes a reproducible baseline and makes the PR evidence machine-readable without weakening any gate.

## Summary

The live documentation contract scans every Markdown file under the repository through `**/*.md`, excluding only the explicitly declared historical `docs/archive/**` scope. It validates manifest metadata, rejects escape paths, resolves local links, detects stale repository names and operational claims, verifies executable truth, requires fail-closed shell behavior, and proves that `guardrails` is a direct dependency of `required-ci`.

The change also adds `.github/branch-protection-policy.json`, explicit CODEOWNERS anchors for governance and CI files, `NO_BYPASS_CONTROL_PLANE.md`, negative documentation tests, and a Qodana baseline generated from the exact main base commit. Existing onboarding, deployment, contract, microservice, application-layer, safety-toolkit, memory, and CI-verification references were corrected without deleting project history.

## How to Test

Run from the repository root:

```text
python3 scripts/fitness/check_documentation_contract.py
pytest -q tests/fitness/test_documentation_contract_gate.py
python3 scripts/fitness/check_authority_links.py
make gates
```

## Validation Evidence

The local validation completed successfully:

```text
✅ عقد التوثيق سليم: 28 وثائق حية، الروابط والمسارات والأوامر الأساسية متسقة.
...                                                                      [100%]
3 passed in 0.16s
✅ كل روابط ملفّات السلطة الـ5 تصل إلى مسارات موجودة.
✅ كل البوّابات الـ73 خضراء.
✅ All fitness gates passed!
```

Qodana was compared against a SARIF report from the exact PR base commit. It reported 2,539 inherited findings and one newly introduced finding in the documentation gate; the new regex finding was fixed, and the workflow now uses `.qodana/baseline.sarif.json` with `--fail-threshold 0`, so any future new finding fails the scan.

## Risk & Rollback

The change is documentation- and validation-focused. The primary risk is a false red from a stale baseline or an analyzer environment change; the rollback is to revert the Qodana baseline/workflow commit while keeping the repository documentation contract and its required-ci gate intact. A baseline may only be regenerated from a successful main analysis, never from a failing feature branch, and any baseline refresh requires review of the SARIF diff.

HUMAN:

AGENT:
The agent prepared the evidence above but does not provide the human attestation. A human CODEOWNER must replace the empty `HUMAN:` section with a first-person confirmation after independently reviewing and running the change. The D-270 gate must remain red until that attestation is supplied.

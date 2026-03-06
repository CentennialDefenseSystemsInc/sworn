Sworn 0.4.0 Phase-0 Release Evidence Manifest

Manifest Type: Phase-0 pre-tag evidence
Release Tag: pending phase1
Tag SHA: pending phase1
PyPI Publish Ref: pending phase1
Build Date (UTC): 2026-03-06T22:35:11Z
Maintainer: pending phase1
Phase-0 Start Commit: c0158bad2c5421b549f8507aaf2a7a4a5d4ca979
Phase-0 Branch: main

Evidence Artifacts
- install.log
- pytest-full.log
- validate_governance.log
- bootstrap_gov.log
- full_verification.log
- release-static-guard.log
- pip-bootstrap.log
- sworn-cli.log
- sworn-module-help.txt
- env-version.txt
- env-uname.txt
- pip-freeze.txt
- phase0-start-sha.txt
- working-tree-at-start.txt
- build-timestamp-utc.txt
- dist-shas.txt
- twine-check.log
- release-smoke.log
- evidence-package.tar.gz
- evidence-package.sha256

Assertions
- Tests passed in clean venv
- Signing available under [dev,signing] release proof and CLI invocation succeeded
- Governance checks passed via validate_governance.py --root . --strict
- Bootstrap and full verification checks passed
- Release static guard passed with version-aligned metadata and no placeholder surfaces
- Canonicalization and hash-chain behavior unchanged from tagged baseline
- CI fail-closed semantics unchanged
- Compliance scope bound to code version in this release
- Built wheel passed smoke install and adversarial behavior scenarios
- Release evidence requires review and commit before any signed tag or publish step
- Signed tag and publish identity must be recorded during phase1 outside the committed phase0 snapshot

Sworn 0.3.0 Phase-0 Release Evidence Manifest

Release Tag:
Tag SHA:
Build Date (UTC): 2026-03-06T21:30:13Z
Maintainer:
Release Commit: b176a08dbb81079b34e2937209acf07ccb5a05ab
Release Branch: main

Evidence Artifacts
- install.log
- pytest-full.log
- validate_governance.log
- bootstrap_gov.log
- full_verification.log
- pip-bootstrap.log
- sworn-cli.log
- sworn-module-help.txt
- env-version.txt
- env-uname.txt
- pip-freeze.txt
- release-sha.txt
- working-tree-at-start.txt
- build-timestamp-utc.txt
- dist-shas.txt
- twine-check.log
- evidence-package.tar.gz
- evidence-package.sha256

Assertions
- Tests passed in clean venv
- Signing available under [dev,signing] release proof and CLI invocation succeeded
- Governance checks passed via validate_governance.py --root . --strict
- Bootstrap and full verification checks passed
- Canonicalization and hash-chain behavior unchanged from tagged baseline
- CI fail-closed semantics unchanged
- Compliance scope bound to code version in this release
- Release evidence requires review and commit before any signed tag or publish step

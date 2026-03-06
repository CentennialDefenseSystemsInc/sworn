# Sworn Phase-0 Evidence Manifest Template

Release Version:
Signed Tag:
Build Date (UTC):
Maintainer:
Release Commit:

## Artifact Inventory

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

## Assertions

- Working tree clean before release run
- `python3 -m pip install .[dev,signing]` passed in clean venv
- `python3 -m pytest tests -q --tb=short` passed
- `python3 ~/.codex/scripts/validate_governance.py --root . --strict` passed
- Bootstrap and full verification scripts passed
- `python3 -m build --no-isolation` succeeded
- Release evidence reviewed and committed before signed tag creation
- Release evidence folder hash recorded

## Hashes

Evidence bundle SHA256:
- evidence-package.sha256:

## Validation Notes

- Any deviation between implementation and signed scope documents is a defect.
- Repo-wide policy drift must be documented before external use.

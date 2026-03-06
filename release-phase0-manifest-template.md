# Sworn Phase-0 Evidence Manifest Template

Release Version:
Signed Tag:
Build Date (UTC):
Maintainer:
Release Commit:

## Artifact Inventory

- install-clean.log
- pytest.log
- governance-checks.log
- bootstrap-check.log
- full-verification.log
- pip-upgrade.log
- sworn-cli.log
- python-version.txt
- pip-freeze.txt
- system.txt
- build-timestamp-utc.txt
- artifacts.sha256
- evidence-package.tar.gz
- evidence-package.sha256

## Assertions

- Working tree clean before release run
- `python3 -m pip install .[signing]` passed in clean venv
- `python3 -m pytest -q --tb=short` passed
- `python3 ~/.codex/scripts/validate_governance.py --strict` passed
- Bootstrap and full verification scripts passed
- `python3 -m build` succeeded
- Release tag created and immutable references attached
- Release evidence folder hash recorded

## Hashes

Evidence bundle SHA256:
- evidence-package.sha256:

## Validation Notes

- Any deviation between implementation and signed scope documents is a defect.
- Repo-wide policy drift must be documented before external use.

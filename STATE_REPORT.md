# STATE_REPORT

Date: 2026-03-06
Branch: `fix/fail-closed-hardening`
Base: `main`

## Outcome

Sworn fail-closed hardening is implemented on this branch.

The following are now `implemented+tested`:

- Evidence append failures block the gate instead of passing through.
- Corrupt prior evidence state fails closed instead of resetting to `genesis`.
- `signing.enabled = true` without a private key blocks the gate.
- Hook installation and status resolve Git's effective hooks path and support worktrees.
- GitHub Action install is version-pinned instead of defaulting to `latest`.
- The example workflow references the real `0.3.0` tag.
- Private-key ignore coverage includes both `.sworn/keys/active.key` and legacy `.sworn/signing.key`.
- Compliance and governance docs reflect detective/evidence-only surfaces where enforcement does not exist.

## Commits

- `4914843` `fix(core): fail closed on evidence and signing faults`
- `301e9d9` `fix(docs): align compliance and release evidence truth`
- `614d5f8` `fix(git): harden hooks, action pinning, and key ignores`
- `fd482d4` `docs(readme): clarify hook and CI enforcement surface`
- `9450260` `fix(git): harden hooks and action distribution`

## Verification

- `PYTHONPATH=src python3 -m pytest tests -q --tb=short` → `180 passed`
- `python3 /Users/cj/.codex/scripts/validate_governance.py --root . --strict` → pass
- `bash /Users/cj/.codex/scripts/bootstrap_codex_governance.sh --repo-root . --check-only` → `BOOTSTRAP PASS`
- `bash /Users/cj/.codex/scripts/run_full_verification.sh` → `VERIFICATION PASS`
- `python3 /Users/cj/.codex/validators/post_session.py /Users/cj/Workspace/active/sworn` → pass
- Portfolio sweep: `/tmp/sworn-sweep-20260306-hardening/PORTFOLIO_SUMMARY.md`

## Notes

- The historical `release-evidence/0.3.0/` bundle was not rewritten in this session. The release-process and manifest tooling were aligned for the next tagged release.
- `PORTFOLIO_STATE.json` baseline for `sworn` was updated from `26` to `27` to match the new sweep inventory.

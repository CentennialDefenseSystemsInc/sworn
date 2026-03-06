#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  local code=$?
  if command -v deactivate >/dev/null 2>&1; then
    deactivate >/dev/null 2>&1 || true
  fi
  if [[ -d "${RUNNER_VENV:-}" ]]; then
    rm -rf "$RUNNER_VENV"
  fi
  if [[ $code -ne 0 ]]; then
    echo "FAIL: phase0 aborted | phase0 | exit code $code | inspect release artifacts for partial state"
  fi
}

trap cleanup EXIT

USAGE() {
  cat <<'EOF'
Usage:
  ./scripts/release_phase0_readiness.sh [--version VERSION] [--tag TAG] [--push] [--python PYTHON_BIN]

Required:
  - Clean git working tree
  - Signable signing dependency available via [signing] extra
  - Access to ~/.codex/scripts/validate_governance.py

Options:
  --version VERSION  Override release version (defaults to pyproject.toml version)
  --tag TAG         Create and optionally push a signed tag after checks
  --push            Push tag after signing (requires --tag)
  --python PYTHON_BIN
                    Python executable to use (default: python3)
  -h, --help        Show this help
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER_BIN="python3"
VERSION="${SWORN_VERSION_OVERRIDE:-}"
TAG_NAME=""
PUSH_TAG="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION="${2:-}"
      shift 2
      ;;
    --tag)
      TAG_NAME="${2:-}"
      shift 2
      ;;
    --push)
      PUSH_TAG="true"
      shift
      ;;
    --python)
      RUNNER_BIN="${2:-}"
      shift 2
      ;;
    -h|--help)
      USAGE
      exit 0
      ;;
    *)
      echo "FAIL: unknown argument: $1 | phase0 | unrecognized CLI"
      USAGE
      exit 1
      ;;
  esac
done

if [[ ! -f "$ROOT_DIR/pyproject.toml" ]]; then
  echo "FAIL: pyproject.toml missing | phase0 | no version source | $ROOT_DIR/pyproject.toml"
  exit 1
fi

if [[ -z "$VERSION" ]]; then
  VERSION="$(grep -E '^version[[:space:]]*=' "$ROOT_DIR/pyproject.toml" | head -n 1 | sed -E 's/version[[:space:]]*=[[:space:]]*["'\'']([^"'\'']+)["'\''].*/\1/')"
fi

if [[ -z "${VERSION}" ]]; then
  echo "FAIL: release version not resolved | phase0 | set --version or fix pyproject.toml"
  exit 1
fi

if ! command -v "$RUNNER_BIN" >/dev/null; then
  echo "FAIL: python binary missing | phase0 | RUNNER_BIN=$RUNNER_BIN"
  exit 1
fi

if [[ ! -x "$RUNNER_BIN" ]]; then
  echo "FAIL: python not executable | phase0 | $RUNNER_BIN"
  exit 1
fi

cd "$ROOT_DIR"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "FAIL: dirty working tree | phase0 | git status must be clean before release run"
  git status --short
  exit 1
fi

if [[ ! -f "$HOME/.codex/scripts/validate_governance.py" ]]; then
  echo "FAIL: governance validation script missing | phase0 | $HOME/.codex/scripts/validate_governance.py"
  exit 1
fi

if [[ ! -f "$HOME/.codex/scripts/bootstrap_codex_governance.sh" ]]; then
  echo "FAIL: bootstrap script missing | phase0 | $HOME/.codex/scripts/bootstrap_codex_governance.sh"
  exit 1
fi

if [[ ! -f "$HOME/.codex/scripts/run_full_verification.sh" ]]; then
  echo "FAIL: full verification script missing | phase0 | $HOME/.codex/scripts/run_full_verification.sh"
  exit 1
fi

RELEASE_DIR="release-evidence/$VERSION"
mkdir -p "$RELEASE_DIR"

LOG() { echo "SOLID: $1 | $2 | $3 | $4"; }

run_step() {
  local name="$1"
  local cmd="$2"
  local out="$3"
  echo "SOLID: phase0 start | $name | $cmd"
  {
    cd "$ROOT_DIR"
    eval "$cmd"
  } | tee "$out"
}

RUNNER_VENV="$ROOT_DIR/.venv-release"
rm -rf "$RUNNER_VENV"
$RUNNER_BIN -m venv "$RUNNER_VENV"
source "$RUNNER_VENV/bin/activate"

run_step "bootstrap env" "$RUNNER_BIN -m pip install --upgrade pip" "$RELEASE_DIR/pip-upgrade.log"
run_step "repro install" "$RUNNER_BIN -m pip install .[signing]" "$RELEASE_DIR/install-clean.log"
run_step "cli sanity" "$RUNNER_BIN -m sworn --version" "$RELEASE_DIR/sworn-cli.log"

run_step "tests" "$RUNNER_BIN -m pytest -q --tb=short" "$RELEASE_DIR/pytest.log"

run_step "governance strict" "$RUNNER_BIN ~/.codex/scripts/validate_governance.py --strict" "$RELEASE_DIR/governance-checks.log"
run_step "bootstrap check" "$RUNNER_BIN ~/.codex/scripts/bootstrap_codex_governance.sh --repo-root . --check-only" "$RELEASE_DIR/bootstrap-check.log"
run_step "full verification" "$RUNNER_BIN ~/.codex/scripts/run_full_verification.sh" "$RELEASE_DIR/full-verification.log"

run_step "python version" "$RUNNER_BIN --version" "$RELEASE_DIR/python-version.txt"
run_step "pip freeze" "$RUNNER_BIN -m pip freeze | sort" "$RELEASE_DIR/pip-freeze.txt"
uname -a | tee "$RELEASE_DIR/system.txt"
date -u +"%Y-%m-%dT%H:%M:%SZ" | tee "$RELEASE_DIR/build-timestamp-utc.txt"

rm -rf "$ROOT_DIR/dist"
$RUNNER_BIN -m build
sha256sum dist/* | sort | tee "$RELEASE_DIR/artifacts.sha256"

tar -czf "$RELEASE_DIR/evidence-package.tar.gz" \
  -C "$ROOT_DIR" \
  "release-evidence/$VERSION" \
  pyproject.toml src/sworn/__init__.py SECURITY.md COMPLIANCE_SCOPE.md RELEASE_PROCESS.md GOVERNANCE_OVERVIEW.md README.md
sha256sum "$RELEASE_DIR/evidence-package.tar.gz" | tee "$RELEASE_DIR/evidence-package.sha256"

cat > "$RELEASE_DIR/MANIFEST.md" <<EOF
Sworn $VERSION Phase-0 Release Evidence Manifest

Release Tag:
Tag SHA:
Build Date (UTC): $(cat "$RELEASE_DIR/build-timestamp-utc.txt")
Maintainer:
Release Commit: $(git rev-parse HEAD)
Release Branch: $(git rev-parse --abbrev-ref HEAD)

Evidence Artifacts
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

Assertions
- Tests passed in clean venv
- Signing available under [signing] extras and CLI invocation succeeded
- Governance checks passed via validate_governance.py --strict
- Bootstrap and full verification checks passed
- Canonicalization and hash-chain behavior unchanged from tagged baseline
- CI fail-closed semantics unchanged
- Compliance scope bound to code version in this release
EOF

if [[ -n "$TAG_NAME" ]]; then
  if [[ "$PUSH_TAG" == "true" ]]; then
    git tag -s "$TAG_NAME" -m "Sworn $VERSION — External Exposure Ready"
    git push origin "$TAG_NAME"
  else
    git tag -s "$TAG_NAME" -m "Sworn $VERSION — External Exposure Ready"
  fi
  echo "SOLID: release tag created | phase0 | $TAG_NAME | $(git rev-parse "$TAG_NAME")"
elif [[ "$PUSH_TAG" == "true" ]]; then
  echo "FAIL: --push requires --tag | phase0 | prevent accidental push without tag"
  exit 1
fi

deactivate
rm -rf "$RUNNER_VENV"

echo "SOLID: phase0 complete | release evidence captured | $VERSION"

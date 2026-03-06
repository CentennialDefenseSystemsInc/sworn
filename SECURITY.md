# SECURITY.md

## Security Model Overview

Sworn enforces deterministic, fail-closed governance over AI-assisted code changes.

Security-sensitive surfaces include:

- Evidence signing and verification
- Hash-chain integrity enforcement
- CI diff-base resolution
- Kernel execution semantics
- Key material handling

Changes to these areas are treated as Rule-2 scope.

## Security Objectives

Sworn’s non-negotiable security invariants:

1. Deterministic governance decisions (no nondeterministic pass/fail outcomes).
2. Tamper-evident evidence logging and verification.
3. Fail-closed behavior in signing and CI enforcement.
4. No silent downgrade of enforcement behavior.

Violations of these objectives are release blockers.

## Trust Assumptions

Sworn operates under the following assumptions:

- The repository host enforces branch protection and reviewer controls as configured.
- CI secrets are protected by the CI provider and repository policy.
- Private signing keys are protected outside repository working trees when org-trust posture is claimed.
- Kernel implementations conform to documented purity and determinism constraints.

Violation of these assumptions reduces assurance guarantees and shifts findings into out-of-model risk.

## Threat Model

### Assets

- Evidence log integrity
- Signature authenticity
- Governance decision determinism
- CI enforcement surface

### Adversary Capabilities Considered

1. Modifies evidence log after commit
2. Strips or tampers with signatures
3. Replays or reorders entries
4. Attempts to bypass pre-commit with `--no-verify`
5. Attempts to exploit CI shallow clone behavior
6. Attempts to exploit nondeterministic kernel ordering
7. Attempts to introduce override-based precedence bypass

### Adversary Capabilities NOT Covered

1. Theft of private signing key
2. Compromise of developer workstation
3. Compromise of CI secrets
4. Malicious kernel implementation
5. Git history rewriting outside Sworn detection surface

Sworn detects integrity violations. It does not defend against host compromise.

## Integrity Guarantees

### Hash Chain

- Each entry includes `prev_hash`.
- Chain discontinuity invalidates verification.

### Signature

- Ed25519 signatures over canonical JSON.
- Canonicalization:
  - UTF-8
  - `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False)`
  - `signature=""` placeholder
- Verification fails closed on mismatch.

## CI Enforcement Model

In CI mode:

- Base SHA must be provided.
- If diff base cannot be resolved, Sworn fails.
- Silent fallback is not permitted.
- Requires `fetch-depth: 0`.

CI misconfiguration results in block, not bypass.

## Kernel Execution Model

Kernels:

- Execute even if structural gates block.
- Must be pure and side-effect free.
- Must tolerate partial pipeline state.
- Must not mutate repository state.

Violations are security defects.

## Key Management

### Default

- Private key: `.sworn/keys/active.key` (gitignored)
- Public keys: `.sworn/keys/*.pub` (committed)

### Migration

Legacy `.sworn/signing.key` layout blocks signed mode until explicitly migrated.

No silent auto-migration occurs.

## Trust Model

Sworn supports two trust postures:

### Repo-Local Integrity

- Detects tampering relative to stored public keys.
- Does not prove organizational authority.

### Org-Trust Mode

Requires:

- Public key pinning
- Protected branch enforcement
- External private-key custody controls
- Explicit rotation policy

Sworn verifies signatures. It does not provide a PKI.

## Non-Goals

Sworn does not:

- Certify CMMC or SOC 2 compliance
- Replace a C3PAO
- Prevent private key theft
- Prevent workstation compromise
- Enforce org-level identity governance
- Provide sandbox isolation for kernels

## Security Severity Classification

Security-Critical (Rule-2):

- Signing canonicalization changes
- Hash-chain structure or verification behavior changes
- Resolver block-semantics changes (including ordering and precedence)
- CI fail-closed enforcement changes
- Kernel behavior changes that alter blocking guarantees

Security-Critical changes require:

- Explicit review
- Required test coverage
- Classification and release handling in `RELEASE_PROCESS.md`

All other changes are non-security-critical by default and follow normal development workflow.

## Reporting Vulnerabilities

Security-sensitive changes should:

- Include test coverage
- Preserve fail-closed semantics
- Maintain canonicalization stability
- Avoid introducing override logic in resolver

## Why This Matters

README explains behavior.

SECURITY.md explains:

- What Sworn defends against
- What it explicitly does not defend against
- Where trust boundaries are
- What assumptions auditors should not make

Without this file, your control-plane language remains marketing-adjacent.

With this file, your posture becomes technically credible.

"""Tests for disposition resolver."""
from __future__ import annotations

from sworn.resolver import KernelDisposition, ResolutionTrace, resolve


def _disp(name: str, decision: str = "PASS", rules: list[str] | None = None,
          evidence: list[str] | None = None) -> KernelDisposition:
    return KernelDisposition(
        name=name,
        decision=decision,
        triggered_rules=rules or [],
        evidence_summary=evidence or [],
    )


class TestResolver:
    def test_all_pass(self):
        result = resolve([_disp("a"), _disp("b"), _disp("c")])
        assert result.final_decision == "PASS"
        assert result.blocked_by == []
        assert result.applied_overrides == []

    def test_single_blocked(self):
        result = resolve([_disp("a"), _disp("b", "BLOCKED", evidence=["bad"])])
        assert result.final_decision == "BLOCKED"
        assert result.blocked_by == ["b"]

    def test_mixed_no_rules_blocked(self):
        result = resolve([
            _disp("a"),
            _disp("b", "BLOCKED", evidence=["issue"]),
            _disp("c"),
        ])
        assert result.final_decision == "BLOCKED"
        assert result.blocked_by == ["b"]

    def test_precedence_override_removes_block(self):
        rules = [{"when_pass": "a", "overrides_block": "b"}]
        result = resolve(
            [_disp("a"), _disp("b", "BLOCKED", evidence=["x"])],
            precedence_rules=rules,
        )
        assert result.final_decision == "PASS"
        assert len(result.applied_overrides) == 1
        assert "a PASS overrides b BLOCKED" in result.applied_overrides[0]
        assert result.blocked_by == []

    def test_override_partial_one_remains(self):
        rules = [{"when_pass": "a", "overrides_block": "b"}]
        result = resolve(
            [
                _disp("a"),
                _disp("b", "BLOCKED", evidence=["x"]),
                _disp("c", "BLOCKED", evidence=["y"]),
            ],
            precedence_rules=rules,
        )
        assert result.final_decision == "BLOCKED"
        assert result.blocked_by == ["c"]
        assert len(result.applied_overrides) == 1

    def test_override_cannot_add_block(self):
        """Precedence rules can only remove blocks, never add."""
        rules = [{"when_pass": "a", "overrides_block": "b"}]
        result = resolve(
            [_disp("a"), _disp("b")],
            precedence_rules=rules,
        )
        assert result.final_decision == "PASS"
        assert result.blocked_by == []

    def test_override_when_pass_didnt_pass(self):
        """Override rule ignored when condition kernel also blocked."""
        rules = [{"when_pass": "a", "overrides_block": "b"}]
        result = resolve(
            [_disp("a", "BLOCKED", evidence=["a_bad"]), _disp("b", "BLOCKED", evidence=["b_bad"])],
            precedence_rules=rules,
        )
        assert result.final_decision == "BLOCKED"
        assert sorted(result.blocked_by) == ["a", "b"]

    def test_empty_dispositions_pass(self):
        result = resolve([])
        assert result.final_decision == "PASS"
        assert result.final_reason == "No kernels evaluated"

    def test_resolution_trace_populated(self):
        result = resolve([_disp("a"), _disp("b", "BLOCKED", evidence=["err"])])
        assert isinstance(result, ResolutionTrace)
        assert len(result.dispositions) == 2
        assert result.blocked_by == ["b"]
        assert "Kernel 'b'" in result.final_reason

    def test_deterministic_ordering(self):
        """Same input always produces same output."""
        disps = [
            _disp("z", "BLOCKED", evidence=["z_bad"]),
            _disp("a", "BLOCKED", evidence=["a_bad"]),
            _disp("m"),
        ]
        r1 = resolve(disps)
        r2 = resolve(disps)
        assert r1.blocked_by == r2.blocked_by
        assert r1.final_decision == r2.final_decision
        assert r1.applied_overrides == r2.applied_overrides

    def test_multiple_overrides(self):
        rules = [
            {"when_pass": "x", "overrides_block": "a"},
            {"when_pass": "x", "overrides_block": "b"},
        ]
        result = resolve(
            [_disp("x"), _disp("a", "BLOCKED", evidence=["1"]), _disp("b", "BLOCKED", evidence=["2"])],
            precedence_rules=rules,
        )
        assert result.final_decision == "PASS"
        assert len(result.applied_overrides) == 2

    def test_malformed_rule_ignored(self):
        """Rules missing required keys are skipped."""
        rules = [{"when_pass": "a"}, {"overrides_block": "b"}]
        result = resolve(
            [_disp("a"), _disp("b", "BLOCKED", evidence=["err"])],
            precedence_rules=rules,
        )
        assert result.final_decision == "BLOCKED"

    def test_blocked_reason_includes_evidence(self):
        result = resolve([_disp("sec", "BLOCKED", evidence=["crypto/key.py detected"])])
        assert "crypto/key.py detected" in result.final_reason

    def test_none_precedence_rules(self):
        result = resolve([_disp("a")], precedence_rules=None)
        assert result.final_decision == "PASS"

    def test_all_blocked(self):
        result = resolve([
            _disp("a", "BLOCKED", evidence=["a_err"]),
            _disp("b", "BLOCKED", evidence=["b_err"]),
        ])
        assert result.final_decision == "BLOCKED"
        assert sorted(result.blocked_by) == ["a", "b"]

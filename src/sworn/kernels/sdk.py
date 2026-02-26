"""Kernel SDK — KernelInput, KernelResult, and kernel loader."""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal


@dataclass
class KernelInput:
    """Input provided to every kernel's evaluate() function."""

    files: list[str]
    actor: str
    tool: str | None
    repo_root: str
    config: dict = field(default_factory=dict)


@dataclass
class KernelResult:
    """Result returned by every kernel's evaluate() function."""

    decision: Literal["PASS", "BLOCKED"]
    triggered_rules: list[str] = field(default_factory=list)
    evidence_summary: list[str] = field(default_factory=list)
    required_next_action: str = ""


EvaluateFn = Callable[[KernelInput], KernelResult]


def load_builtin_kernels(
    enabled: dict[str, bool],
) -> list[tuple[str, EvaluateFn]]:
    """Load built-in kernels based on config. Returns (name, evaluate) pairs."""
    kernels: list[tuple[str, EvaluateFn]] = []

    if enabled.get("security", True):
        from sworn.kernels.security_kernel import evaluate

        kernels.append(("security", evaluate))

    if enabled.get("allowlist", True):
        from sworn.kernels.allowlist_kernel import evaluate as al_evaluate

        kernels.append(("allowlist", al_evaluate))

    if enabled.get("audit", True):
        from sworn.kernels.audit_kernel import evaluate as au_evaluate

        kernels.append(("audit", au_evaluate))

    # CMMC kernel pack (group toggle or per-control)
    cmmc_enabled = enabled.get("cmmc", False)
    if cmmc_enabled:
        _cmmc_kernels = [
            ("cmmc_ac_access", "sworn.kernels.cmmc.ac_access"),
            ("cmmc_au_records", "sworn.kernels.cmmc.au_records"),
            ("cmmc_au_traceability", "sworn.kernels.cmmc.au_traceability"),
            ("cmmc_cm_baseline", "sworn.kernels.cmmc.cm_baseline"),
            ("cmmc_cm_settings", "sworn.kernels.cmmc.cm_settings"),
            ("cmmc_cm_access", "sworn.kernels.cmmc.cm_access"),
            ("cmmc_sc_boundary", "sworn.kernels.cmmc.sc_boundary"),
            ("cmmc_si_flaw", "sworn.kernels.cmmc.si_flaw"),
            ("cmmc_evidence_integrity", "sworn.kernels.cmmc.evidence_integrity"),
        ]
        for name, module_path in _cmmc_kernels:
            if not enabled.get(name, True):
                continue
            import importlib
            mod = importlib.import_module(module_path)
            kernels.append((name, mod.evaluate))

    return kernels


def load_custom_kernels(
    custom_dir: Path,
) -> list[tuple[str, EvaluateFn]]:
    """Load custom kernels from directory. Fail-closed on import errors."""
    kernels: list[tuple[str, EvaluateFn]] = []

    if not custom_dir.is_dir():
        return kernels

    for py_file in sorted(custom_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(
                f"sworn_custom_kernel_{name}", py_file
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load spec for {py_file}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"sworn_custom_kernel_{name}"] = mod
            spec.loader.exec_module(mod)
            evaluate_fn = getattr(mod, "evaluate", None)
            if evaluate_fn is None:
                raise ImportError(f"No evaluate() function in {py_file}")
            kernels.append((name, evaluate_fn))
        except Exception:
            # Fail-closed: import failure = blocked kernel
            def _blocked_kernel(
                _input: KernelInput, _name: str = name, _path: str = str(py_file)
            ) -> KernelResult:
                return KernelResult(
                    decision="BLOCKED",
                    triggered_rules=["kernel_import_failure"],
                    evidence_summary=[f"Failed to import kernel: {_path}"],
                    required_next_action=f"Fix kernel {_name} at {_path}",
                )

            kernels.append((name, _blocked_kernel))

    return kernels

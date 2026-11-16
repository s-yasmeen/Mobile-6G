"""History-aware candidate selector for sequential sensing releases.

This module is a policy primitive, not a privacy guarantee. Candidate risk values
must be calibrated estimates of adversarial success on the complete release
prefix after the candidate transformation has been applied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ControllerConfig:
    max_sequence_risk: float = 0.60
    min_utility: float = 0.70
    max_latency_ms: float = 20.0
    utility_weight: float = 0.50
    latency_weight: float = 0.10
    sanitizer_penalty: float = 0.02
    history_growth_weight: float = 1.00


@dataclass(frozen=True)
class PolicyCandidate:
    action: str
    sequence_risk: float
    utility: float
    latency_ms: float


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    reason: str
    sequence_risk: float | None
    utility: float | None
    latency_ms: float | None
    risk_delta: float | None
    objective: float | None


class HistoryAwareController:
    """Select the least-cost feasible action using risk over the full prefix.

    Risk is never summed across releases. Each candidate must supply a calibrated
    sequence-risk estimate for the complete prefix X_1:t. The controller tracks
    the last accepted prefix risk and penalizes increases in the next prefix.
    """

    ALLOWED_ACTIONS = {"ALLOW", "SANITIZE"}

    def __init__(self, config: ControllerConfig | None = None):
        self.config = config or ControllerConfig()
        self.accepted_risk_history: list[float] = []

    @property
    def previous_risk(self) -> float | None:
        return self.accepted_risk_history[-1] if self.accepted_risk_history else None

    def decide(self, candidates: Iterable[PolicyCandidate]) -> PolicyDecision:
        cfg = self.config
        candidates = list(candidates)
        if not candidates:
            raise ValueError("At least one candidate assessment is required")

        seen: set[str] = set()
        feasible: list[tuple[float, PolicyCandidate, float]] = []
        previous = self.previous_risk

        for candidate in candidates:
            action = candidate.action.upper()
            if action not in self.ALLOWED_ACTIONS:
                raise ValueError(f"Unsupported candidate action: {candidate.action}")
            if action in seen:
                raise ValueError(f"Duplicate candidate action: {action}")
            seen.add(action)
            if not 0.0 <= candidate.sequence_risk <= 1.0:
                raise ValueError("sequence_risk must be in [0, 1]")
            if not 0.0 <= candidate.utility <= 1.0:
                raise ValueError("utility must be in [0, 1]")
            if candidate.latency_ms < 0.0:
                raise ValueError("latency_ms must be non-negative")

            risk_delta = 0.0 if previous is None else candidate.sequence_risk - previous
            if (
                candidate.sequence_risk > cfg.max_sequence_risk
                or candidate.utility < cfg.min_utility
                or candidate.latency_ms > cfg.max_latency_ms
            ):
                continue

            sanitizer_cost = cfg.sanitizer_penalty if action == "SANITIZE" else 0.0
            growth_cost = cfg.history_growth_weight * max(0.0, risk_delta)
            objective = (
                cfg.utility_weight * (1.0 - candidate.utility)
                + cfg.latency_weight * candidate.latency_ms
                + sanitizer_cost
                + growth_cost
            )
            feasible.append((objective, candidate, risk_delta))

        if not feasible:
            return PolicyDecision(
                action="BLOCK",
                reason="No candidate satisfies the sequence-risk, utility and latency constraints.",
                sequence_risk=None,
                utility=None,
                latency_ms=None,
                risk_delta=None,
                objective=None,
            )

        objective, selected, risk_delta = min(
            feasible, key=lambda item: (item[0], item[1].action != "ALLOW")
        )
        action = selected.action.upper()
        self.accepted_risk_history.append(float(selected.sequence_risk))
        return PolicyDecision(
            action=action,
            reason="Selected the lowest-objective candidate satisfying all configured constraints.",
            sequence_risk=float(selected.sequence_risk),
            utility=float(selected.utility),
            latency_ms=float(selected.latency_ms),
            risk_delta=float(risk_delta),
            objective=float(objective),
        )

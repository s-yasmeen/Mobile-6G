import pytest

from src.history_controller import (
    ControllerConfig,
    HistoryAwareController,
    PolicyCandidate,
)


def test_controller_allows_low_risk_candidate():
    controller = HistoryAwareController()
    decision = controller.decide([
        PolicyCandidate("ALLOW", sequence_risk=0.25, utility=0.90, latency_ms=2.0),
        PolicyCandidate("SANITIZE", sequence_risk=0.10, utility=0.80, latency_ms=4.0),
    ])
    assert decision.action == "ALLOW"
    assert decision.risk_delta == 0.0
    assert controller.previous_risk == 0.25


def test_controller_sanitizes_when_allow_candidate_exceeds_risk_cap():
    controller = HistoryAwareController(ControllerConfig(max_sequence_risk=0.60))
    decision = controller.decide([
        PolicyCandidate("ALLOW", sequence_risk=0.72, utility=0.95, latency_ms=2.0),
        PolicyCandidate("SANITIZE", sequence_risk=0.40, utility=0.82, latency_ms=4.0),
    ])
    assert decision.action == "SANITIZE"
    assert decision.sequence_risk == 0.40


def test_history_growth_penalty_can_prefer_sanitization():
    controller = HistoryAwareController(ControllerConfig(
        max_sequence_risk=0.80,
        history_growth_weight=2.0,
        sanitizer_penalty=0.01,
        utility_weight=0.50,
        latency_weight=0.10,
    ))
    first = controller.decide([
        PolicyCandidate("ALLOW", sequence_risk=0.40, utility=0.98, latency_ms=1.0),
    ])
    assert first.action == "ALLOW"

    second = controller.decide([
        PolicyCandidate("ALLOW", sequence_risk=0.62, utility=0.98, latency_ms=1.0),
        PolicyCandidate("SANITIZE", sequence_risk=0.44, utility=0.92, latency_ms=1.2),
    ])
    assert second.action == "SANITIZE"
    assert second.risk_delta == pytest.approx(0.04)


def test_controller_blocks_when_no_candidate_is_feasible():
    controller = HistoryAwareController(ControllerConfig(min_utility=0.80))
    decision = controller.decide([
        PolicyCandidate("ALLOW", sequence_risk=0.20, utility=0.60, latency_ms=2.0),
        PolicyCandidate("SANITIZE", sequence_risk=0.10, utility=0.75, latency_ms=2.0),
    ])
    assert decision.action == "BLOCK"
    assert controller.previous_risk is None


def test_controller_rejects_invalid_risk_and_duplicate_actions():
    controller = HistoryAwareController()
    with pytest.raises(ValueError, match="sequence_risk"):
        controller.decide([PolicyCandidate("ALLOW", 1.2, 0.9, 2.0)])
    with pytest.raises(ValueError, match="Duplicate"):
        controller.decide([
            PolicyCandidate("ALLOW", 0.2, 0.9, 2.0),
            PolicyCandidate("ALLOW", 0.3, 0.9, 2.0),
        ])

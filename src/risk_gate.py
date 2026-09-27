from dataclasses import dataclass

@dataclass
class GateThresholds:
    allow_auc_max: float = 0.60
    block_auc_min: float = 0.75
    min_utility_f1: float = 0.70


def release_decision(identity_auc: float, utility_f1: float, t: GateThresholds) -> str:
    """Fail-closed release decision based on measured privacy and utility."""
    if utility_f1 < t.min_utility_f1:
        return "BLOCK"
    if identity_auc >= t.block_auc_min:
        return "BLOCK"
    if identity_auc > t.allow_auc_max:
        return "SANITIZE"
    return "ALLOW"

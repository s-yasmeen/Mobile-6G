# Mobile-6G: Cumulative Privacy Leakage Experiments

Research code for **risk-adaptive privacy assurance in next-generation mobile/ISAC networks**.

## Research hypothesis
Repeated observations that appear acceptable individually can accumulate enough information to increase identity inference risk.

## Pipeline
1. Load RF/ISAC features and labels.
2. Train a utility classifier (e.g. activity/gesture).
3. Train an identity attacker.
4. Aggregate repeated releases at K = 1, 2, 5, 10, 20 observations.
5. Estimate cumulative privacy leakage.
6. Apply an ALLOW / SANITIZE / BLOCK release policy.
7. Report utility, privacy leakage, and policy decisions.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python experiments/run_smoke_test.py
```

The smoke test uses synthetic data only. Public dataset adapters for mmHSense and OPERAnet are planned next; dataset files should not be committed to Git.

## Status
Phase 1: reproducible baseline scaffold.

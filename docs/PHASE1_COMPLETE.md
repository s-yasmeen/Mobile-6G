# Phase 1 Completion Record

Phase 1 objective: establish a reproducible, falsifiable baseline framework before using real participant RF/ISAC datasets.

| Task | Status | Evidence |
|---|---|---|
| Define central hypothesis | COMPLETE | README + experiment plan |
| Define RQ1-RQ4 | COMPLETE | docs/EXPERIMENT_PLAN.md |
| Map research gaps to measurements | COMPLETE | This record + experiment plan |
| Synthetic RF validation generator | COMPLETE | src/synthetic.py |
| Utility classifier | COMPLETE | experiments/run_cumulative.py |
| Identity inference attacker | COMPLETE | experiments/run_cumulative.py |
| Repeated-release K experiment | COMPLETE | K read from configs/baseline.yaml |
| Privacy baselines | COMPLETE | none/noise/quantize/clip |
| Adaptive release gate | COMPLETE | src/risk_gate.py |
| Privacy metric | COMPLETE | macro one-vs-rest ROC-AUC |
| Utility metric | COMPLETE | macro-F1 |
| Runtime measurement | COMPLETE | attack_fit_eval_ms |
| External feature-data contract | COMPLETE | src/data.py + data/README.md |
| Configuration-driven thresholds | COMPLETE | configs/baseline.yaml |
| Deterministic seed | COMPLETE | config/CLI + model random_state |
| Run metadata/provenance | COMPLETE | per-run metadata JSON |
| Automated tests | COMPLETE | tests/test_core.py |
| Continuous integration | COMPLETE | .github/workflows/ci.yml |
| Result visualization | COMPLETE | experiments/plot_results.py |
| Third-party raw data excluded | COMPLETE | .gitignore + data/README.md |
| Scientific-claim boundary documented | COMPLETE | README |

## Gap traceability

**G1 cumulative leakage** → identity AUC at increasing K.  
**G2 composition over time** → repeated-release aggregation versus K=1 baseline.  
**G3 privacy–utility coupling** → identity AUC reported with utility macro-F1.  
**G4 static controls** → risk-adaptive ALLOW/SANITIZE/BLOCK gate.  
**G5 comparable protections** → controlled none/noise/quantize/clip baselines.  
**G6 generalization** → interface prepared in Phase 1; actual mmHSense/OPERAnet validation is Phase 2.  
**G7 overhead** → baseline runtime instrumentation; expanded systems profiling is Phase 3.  
**G8 AI attack surface** → explicit trained identity adversary.  
**G9 fail-closed assurance** → utility/privacy thresholds feed release gate.

## Exit criterion
Phase 1 is complete when CI passes on the final branch revision. Synthetic outputs validate implementation only and are not publication evidence.

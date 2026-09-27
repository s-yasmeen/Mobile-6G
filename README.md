# Mobile-6G — Cumulative Privacy Leakage Assurance

Experimental prototype for studying **cumulative identity leakage from repeated RF/ISAC releases** and risk-adaptive ALLOW / SANITIZE / BLOCK control in next-generation mobile sensing networks.

> Research status: the software pipeline is implemented and reproducible. Synthetic data is used only for smoke testing; scientific conclusions require experiments on real datasets such as mmHSense and OPERAnet.

## Hypothesis
A release that is acceptable in isolation may become privacy-sensitive when an adversary combines repeated observations.

## Architecture
RF/ISAC input → task utility → sanitizer → repeated-release aggregation → identity attacker → cumulative privacy score → risk gate.

## Reproduce
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q
python experiments/run_smoke_test.py
python experiments/run_cumulative.py --sanitizer none
python experiments/run_cumulative.py --sanitizer noise --strength 0.25
python experiments/run_cumulative.py --sanitizer quantize --strength 0.25
python experiments/plot_results.py
```

Windows activation: `.venv\\Scripts\\activate`.

## Real dataset input
Export extracted RF/ISAC windows to a feature CSV containing `identity`, `activity`, and numeric features, then run:
```bash
python experiments/run_cumulative.py --csv data/processed/features.csv --sanitizer none
```
See `data/README.md` for the contract. Raw third-party datasets are deliberately excluded.

## Outputs
- utility macro-F1
- identity attacker macro one-vs-rest ROC-AUC
- decision: ALLOW / SANITIZE / BLOCK
- attack runtime
- privacy-vs-release-count CSVs and plot

## Research questions
1. Does identity leakage increase as repeated observations accumulate?
2. Can cumulative leakage drive adaptive release decisions?
3. What privacy–utility trade-off results from sanitization?
4. What computational overhead is introduced?

## Repository map
- `src/`: data, privacy, metrics, risk gate, synthetic validation
- `experiments/`: runnable experiments and plotting
- `configs/`: baseline thresholds/configuration
- `tests/`: core unit tests
- `docs/EXPERIMENT_PLAN.md`: publication-oriented protocol
- `.github/workflows/ci.yml`: reproducibility checks

## Scientific caution
Do not describe Wi-Fi/5G measurements as native 6G data. They are RF/ISAC validation datasets for a framework motivated by next-generation mobile networks. Report dataset-specific protocols, subject/session splits, confidence intervals, and all privacy/utility thresholds in the manuscript.

## License
MIT.

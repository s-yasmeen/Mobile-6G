# Mobile-6G — Cumulative Privacy Leakage Assurance

Experimental prototype for studying **cumulative identity leakage from repeated RF/ISAC releases** and risk-adaptive ALLOW / SANITIZE / BLOCK control in next-generation mobile sensing networks.

> Research status: the original synthetic pipeline supports smoke testing. A new session-disjoint chronological evaluation path is available in `experiments/run_sequence_protocol.py`. Neither path constitutes scientific validation until qualified real datasets are processed and experiments are run. The previously listed mmHSense and OPERAnet candidates still require verification of official records, labels, sessions, licences and access.

## Hypothesis

A release that is acceptable in isolation may become privacy-sensitive when an adversary combines repeated observations.

## Architecture

RF/ISAC input → task utility → sanitizer → ordered release sequences → identity attacker → sequence-level risk assessment → risk gate.

## Reproduce the existing synthetic smoke pipeline

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

Synthetic runs are software smoke tests only. Do not use their outputs as evidence for research claims.

## Session-disjoint chronological evaluation

The new protocol requires a CSV containing:
- `identity`: pseudonymous identity label
- `activity`: legitimate sensing-task label
- `session`: acquisition session identifier
- `timestamp`: recommended ordering field
- numeric feature columns

Run:
```bash
python experiments/run_sequence_protocol.py --csv data/processed/features.csv --sanitizer none
python experiments/run_sequence_protocol.py --csv data/processed/features.csv --sanitizer noise --strength 0.25
```

This protocol evaluates **known-identity re-identification across held-out sessions**. Each identity must have at least two sessions. It constructs chronological sequences within identity-session boundaries and does not allow sessions to overlap across train/test. It is not an unseen-identity open-set protocol.

See:
- `data/README.md` for the data contract.
- `docs/EXPERIMENT_PROTOCOL_V2.md` for threat model, split rules, metrics, baselines and statistical design.
- `docs/LITERATURE_REVIEW_2026.md` for the preliminary evidence scan.
- `docs/RESEARCH_DEVELOPMENT_PLAN.md` for the work packages and publication roadmap.

Raw third-party datasets are deliberately excluded from this repository.

## Outputs

- legitimate-task macro-F1
- identity attacker macro-F1 and macro one-vs-rest ROC-AUC
- ALLOW / SANITIZE / BLOCK decision
- attack fit/evaluation runtime
- per-release-count CSV and metadata manifest

**Important:** ROC-AUC is an empirical attacker-performance metric. It is not a formal cumulative privacy budget and must not be summed across releases. Formal differential-privacy claims require a calibrated mechanism, explicit adjacency and sensitivity assumptions, and a valid composition accountant.

## Research questions

1. Does identity inference risk increase as ordered observations accumulate?
2. How do sequence length, temporal dependence and adversarial side information affect inference?
3. Can release-history-aware control improve the privacy–utility–cost frontier?
4. Does the result generalize across held-out sessions, environments and datasets?
5. What computational and latency overhead is introduced?

## Repository map

- `src/`: data, privacy, metrics, risk gate, sequence construction and synthetic validation
- `experiments/`: runnable experiments and plotting
- `configs/`: baseline thresholds/configuration
- `tests/`: core and sequence protocol tests
- `docs/`: literature review, experiment protocols and research plan
- `.github/workflows/ci.yml`: reproducibility checks

## Scientific caution

Do not describe Wi-Fi/5G measurements as native 6G data. They are RF/ISAC validation datasets for a framework motivated by next-generation mobile networks. Report dataset-specific protocols, subject/session splits, confidence intervals, and all privacy/utility thresholds in the manuscript. Do not claim that a research gap is unique until direct-overlap literature has been checked in full text.

## License

MIT.

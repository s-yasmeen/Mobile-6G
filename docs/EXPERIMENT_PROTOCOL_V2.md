# Experimental Protocol v2: Sequential Leakage-Aware Privacy Control

## 1. Research objective

Evaluate whether a release-history-aware controller can reduce adversarial inference from sequential RF/ISAC sensing releases while retaining task utility and meeting latency/compute constraints.

## 2. Claims to test (not assume)

- H1: An attacker using multiple ordered releases can outperform a single-release attacker under at least some participant/session and environment conditions.
- H2: The amount and shape of additional inference depend on sequence length, temporal dependence, attacker side information and distribution shift.
- H3: A release-history-aware policy can improve a measured privacy–utility–cost frontier over fixed sanitization and per-release thresholding.
- H4: The policy's benefit persists under held-out sessions/environments and reasonable attacker model changes.

A null result for any hypothesis is scientifically reportable.

## 3. Critical correction to current pipeline

The current `experiments/run_cumulative.py` performs a stratified random observation-level split. The current CSV loader discards `timestamp` and `session`. The current aggregation routine groups observations by identity and averages non-overlapping blocks after splitting. This can place correlated windows from the same session in train and test and can create groups that do not correspond to true chronological release sequences.

Do not use current random-split results as publication evidence.

## 4. Data schema and split contract

Retain at minimum:
- `identity`: pseudonymous participant/device label, as appropriate to the threat model.
- `activity`: sensing task label.
- numeric features or raw CSI-derived representations.
- `session`: acquisition session identifier.
- `timestamp` or ordered sample index.
- `environment`, `device`, `radio` where available.

Before model fitting:
1. Check duplicate rows, missing labels, timestamp monotonicity and sample/window overlap.
2. Keep participant IDs pseudonymous; do not commit raw participant data.
3. Fit scalers, feature selection and sanitizers only on training data.
4. Create sequence windows within participant-session boundaries; never concatenate across session breaks.
5. Use a session-disjoint split within each participant when the goal is known-user re-identification across sessions. The same enrolled identities may occur in train and test, but sessions/time windows must be disjoint.
6. If the dataset has only one session per participant, do not claim cross-session identity generalization. Use an explicitly different protocol (e.g., within-session chronological holdout with a purge gap) and report its limitation.
7. For unseen-identity evaluation, use open-set verification or retrieval metrics; a closed-set classifier cannot classify identity classes absent from training.

## 5. Threat model

Specify before experiments:
- protected attribute: participant identity, location, behavior or another label actually present.
- legitimate task: activity recognition, presence detection or localization.
- adversary access: released feature sequence, timing, metadata and stated side information.
- attacker knowledge: white-box/black-box model access, training data availability, known sanitizer.
- observation horizon: K releases, with K values fixed in advance.
- adversary objective: closed-set identity classification, pairwise verification, retrieval/re-identification or attribute inference.
- attacker adaptation: train separately for each K and also test a fixed attacker where appropriate.
- no access to raw data beyond the stated release interface.

Avoid implying a real 6G deployment or native 6G measurement unless the data actually comes from such a system.

## 6. Release sequence design

Use chronological, non-overlapping release sequences with K in {1, 2, 5, 10, 20}, provided the dataset supports those horizons. Add overlapping windows only as a separately labelled sensitivity experiment.

For each sequence, compare:
- last release only;
- first release only;
- simple temporal mean;
- concatenated sequence;
- temporal summary (mean, variance, trend and quantiles);
- a lightweight sequence model (e.g., GRU/1D-CNN) only when sample volume supports it.

Ensure that all methods receive the same allowed observations and no future data.

## 7. Baselines and interventions

Baselines:
1. No sanitizer.
2. Fixed Gaussian perturbation.
3. Quantization.
4. Clipping.
5. Fixed-threshold per-release ALLOW/SANITIZE/BLOCK.
6. Adaptive policy using only current-release risk.
7. Proposed release-history-aware policy.
8. Where implementable, a calibrated DP feature-release baseline with a documented privacy accountant and valid adjacency/sensitivity assumptions.

Do not describe arbitrary Gaussian noise as differentially private. DP claims require calibrated noise, clipping/sensitivity bounds, adjacency definition and correct composition accounting.

## 8. Metrics

### Utility
- Macro-F1 and balanced accuracy for the legitimate task.
- Per-class recall and confusion matrix.
- Utility degradation relative to no sanitizer.

### Adversarial inference
- Macro one-vs-rest ROC-AUC and macro-F1 for closed-set classification.
- For verification/re-identification: ROC-AUC, EER, TAR at fixed FAR, and rank-1/CMC where appropriate.
- Calibration and confidence intervals.
- Compare K=1 against larger K using the same subject/session split.

### Cumulative risk
Do not sum ROC-AUC values. Report:
- attacker success/posterior success probability over the whole K-release sequence, if a calibrated probabilistic attacker is used;
- sequence-level Bayes risk or log-loss where assumptions permit;
- mutual-information estimates only with estimator details and uncertainty;
- for DP baselines, composed epsilon/delta using the appropriate accountant, not an empirical AUC surrogate.

### Systems cost
- per-release decision latency and end-to-end sequence processing latency;
- CPU time and peak memory;
- model size and policy overhead;
- report hardware/software environment.

## 9. Statistical design

- Use at least 5 fixed random seeds where training stochasticity applies.
- Bootstrap at participant or session level, not individual correlated windows, for 95% confidence intervals.
- Use paired comparisons on identical held-out sessions.
- Report effect sizes and confidence intervals, not only p-values.
- Pre-register primary metric, primary K horizon and primary comparator in the experiment config.
- Include multiple-comparison correction for families of confirmatory comparisons.

## 10. Ablations and stress tests

- remove cumulative-history state;
- replace temporal attacker with mean aggregation;
- vary K and release interval;
- vary sanitizer strength;
- vary side-information availability;
- test activity/environment/device shift;
- test class imbalance and small enrollment;
- test missing or irregular releases;
- test threshold calibration sensitivity;
- compare online update cost with batch sequence inference.

## 11. Dataset admission checklist

A dataset is admitted only after confirming:
- official repository/publisher page and stable citation;
- licence and permitted use;
- raw signal or feature access;
- identity/participant labels;
- task labels;
- session/timestamp/order fields;
- sufficient repeated observations per identity;
- acquisition conditions and device metadata;
- no prohibited redistribution;
- reproducible preprocessing.

Current repository candidates mmHSense and OPERAnet remain unverified until these checks pass. Alternatives surfaced by literature search include WiMANS, EHUNAM, eHealth CSI, the 80-MHz CSI dataset, WiStride, ElderAL-CSI, SHARP-80 and CSI-based Device-free Localization and Obfuscation. Select one primary dataset and one independent validation dataset based on actual files and annotations.

## 12. Reproducibility artifacts

Each run must save:
- immutable config snapshot;
- dataset/version and preprocessing manifest;
- split indices or split manifest (pseudonymous IDs only);
- seed, package versions and hardware;
- predictions/probabilities and per-sequence identifiers;
- metrics and bootstrap intervals;
- runtime/memory measurements;
- model and sanitizer parameters;
- commit SHA.

Never commit raw participant data or sensitive identifiers.

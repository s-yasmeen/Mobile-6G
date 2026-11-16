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
- `session`: acquisition session identifier, where available.
- `timestamp` or original ordered sample index.
- `environment`, `device`, `radio` where available.

Before model fitting:
1. Check duplicate rows, missing labels, timestamp monotonicity and sample/window overlap.
2. Keep participant IDs pseudonymous; do not commit raw participant data.
3. Fit scalers, feature selection and sanitizers only on training data.
4. Create sequence windows within participant-session or recording boundaries; never concatenate across acquisition breaks.
5. Use a session-disjoint split within each participant when the goal is known-user re-identification across sessions. The same enrolled identities may occur in train and test, but sessions/time windows must be disjoint.
6. If a dataset has only one recording/session per participant, do not claim cross-session identity generalization. Use a documented chronological within-recording holdout with a purge gap only if original sample ordering and recording boundaries are available; report this as a weaker protocol.
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

## 11. Dataset admission and protocol mapping

A dataset is admitted only after confirming:
- official repository/publisher page and stable citation;
- licence and permitted use;
- raw signal or feature access;
- identity/participant labels;
- task labels;
- session/timestamp/order fields or an explicitly justified within-recording split;
- sufficient repeated observations per identity;
- acquisition conditions and device metadata;
- no prohibited redistribution;
- reproducible preprocessing.

### mmHSense (primary candidate)

The 2026 IEEE Access paper and official code repository are verified. The mmW-GaitID dataset targets person identification and reports 20 participants across a three-day collection campaign, with 60-GHz CSI at 10 Hz and a matched 5-GHz CSI modality. The public example loader exposes combined data and labels but does not expose session/day/timestamp metadata. Inspect the actual DataPort archive and labels before choosing a split. Do not assume that three collection days mean each participant has multiple sessions.

mmW-Loc is a separate 20-participant localization-fingerprinting task on a 4×5 grid and may support a location-privacy sub-study, but its task labels and threat model must be kept distinct from person identification.

### OPERAnet (secondary candidate)

The 2022 Scientific Data paper documents approximately eight hours of synchronized RF and vision measurements across two rooms, six participants and six activities, with WiFi CSI, passive WiFi radar, UWB and Kinect modalities. It is a useful independent RF activity/localization dataset. Verify participant-ID labels and sequence/session structure from the downloadable files before using it for identity re-identification. Its small participant count limits identity-generalisation claims.

### Other candidates

WiMANS, EHUNAM, eHealth CSI, the 80-MHz WiFi CSI dataset, WiStride, ElderAL-CSI, SHARP-80 and CSI-based Device-free Localization and Obfuscation remain secondary options pending file/licence/label verification.

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


## 13. Updated dataset strategy: CSI-Bench as primary candidate

The NeurIPS 2025 CSI-Bench benchmark is now the preferred primary candidate, subject to data-rights and metadata qualification. The paper reports over 461 hours, 35 users, 26 environments and 16 device types, with a multitask dataset carrying user identity, activity and proximity annotations. The current author repository documents per-recording paths with user, activity, environment, device and session timestamp components, metadata CSVs and split manifests.

Before any experiment:
1. Verify the Kaggle dataset terms independently of the code repository's MIT licence.
2. Inspect the latest archive/version and all three multitask metadata tables.
3. Verify that UID/HAR/proximity rows refer to the same observations using common stable IDs or exact resolved file paths. A shared column name alone is not proof of alignment.
4. Check duplicate keys, one-to-many mappings, label consistency and file availability.
5. Confirm the number of genuine session groups per user and whether the official split definitions overlap sessions.
6. Preserve official splits for baseline reproduction; use additional session/device/environment holdouts for the proposed privacy experiments and document their construction.

Run the diagnostic:
```bash
python experiments/qualify_csi_bench.py --root /path/to/CSI-Bench
```
It is inspection-only and deliberately returns a NOT_ADMITTED decision. Review its JSON report before creating a feature table.

The public benchmark project page reports high in-distribution user-identification performance. Those are dataset-author baseline results, not results of this project. The current author repository also documents cross-device and cross-environment evaluations. Use these only as motivation and reproduce them from the current archive before quoting exact values.

### Secondary datasets

- mmHSense: use mmW-GaitID and mmW-Loc as separate mmWave/ISAC replications. Collection across several days does not prove repeated per-user sessions.
- OPERAnet: use for secondary RF activity/localization sensitivity analysis; its participant count is small for identity-generalization claims.

No raw archive is currently present in this repository workspace. Therefore, the session-aware runner remains a protocol implementation awaiting a dataset-specific adapter and real-data validation.

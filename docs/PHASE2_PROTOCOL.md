# Phase 2 — Pre-specified Real-Data Baseline Protocol

## Purpose
Establish whether real RF/ISAC representations simultaneously contain useful sensing information and recoverable identity information before testing cumulative composition.

## Frozen hypotheses
- H2-U: RF/ISAC representations support the legitimate sensing task above an empirical label-permutation baseline.
- H2-P: A single RF/ISAC observation contains identity information above an empirical label-permutation baseline.
- H2-R: conclusions are not dependent on one attacker, seed, or split.
- H2-X: the pipeline transfers to an independent RF dataset without changing the evaluation definitions.

These hypotheses are evaluated without assuming they will be supported.

## Primary endpoints
1. Utility macro-F1 and balanced accuracy.
2. Identity macro one-vs-rest ROC-AUC, macro-F1 and balanced accuracy.
3. 95% bootstrap confidence intervals.
4. Empirical permutation/chance baseline.
5. Runtime per fitted/evaluated model.

## Models
Privacy attackers: multinomial logistic regression, random forest, MLP. Utility baselines use the same model families to avoid selecting a favorable learner post hoc.

## Dataset roles
### mmHSense — primary ISAC dataset
Use an mmHSense subset only when the released files provide both the required task and identity/session metadata for the planned experiment. Gesture/localization are candidate utility tasks; gait/person identification informs privacy-risk evaluation. Do not fabricate a cross-task sample correspondence when separate subsets do not contain aligned observations.

### OPERAnet — independent validation
Use RF modalities only (initially Wi-Fi CSI; UWB/PWR as extensions). Activity is the legitimate target and person_id the private target when available in the selected modality/metadata.

## Split policy
Random window splits are diagnostic only and must not be the headline result. Prefer session/experiment-aware separation so neighboring windows from one recording cannot leak across partitions. Subject-disjoint splitting is appropriate for utility generalization, but is NOT valid for closed-set identity classification because test identities must exist in training. Identity leakage therefore uses known-identity, session-disjoint evaluation. Report these threat models separately.

## Benchmark interpretation
No universal AUC value is declared privacy-safe. Statistical evidence is measured relative to empirical permutation baselines and confidence intervals. ALLOW/SANITIZE/BLOCK thresholds are engineering operating points, not 6G standards.

## Phase 2 exit criteria
- real dataset audit and license/provenance record;
- deterministic adapter/preprocessing path;
- integrity checks and class distributions;
- leakage-aware split manifest;
- three utility models and three privacy attackers;
- five pre-specified seeds;
- bootstrap 95% CIs and permutation baseline;
- machine-readable results and metadata;
- independent-dataset sanity check where labels permit;
- CI tests for adapters, splitting, metrics and benchmark runner;
- no synthetic observations in headline Phase 2 result tables.

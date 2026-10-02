# ESP-Fi HAR controlled pilot — Phase 2

**Status:** preliminary real-data pilot; not final Phase-2 evidence.

## Scope

The pilot uses ESP-Fi HAR raw CSI recordings supplied locally and does not redistribute third-party raw data.

Two controlled 3-class tasks were formed from Scenario 1:

- **Privacy / identity:** Activity 7 fixed; Participants 1, 2, and 8; 10 trials per participant (30 recordings).
- **Utility / activity:** Participant 1 fixed; Activities 1, 5, and 7; 10 trials per activity (30 recordings).

This construction prevents activity from acting as an identity proxy in the privacy task and prevents participant identity from acting as an activity proxy in the utility task.

## Features and evaluation

The model input contains CSI-derived amplitude summaries only. Filename labels, participant/activity identifiers, timestamps, MAC addresses, RSSI, and other packet metadata are not model features.

Per-subcarrier features include mean, standard deviation, 25/50/75% quantiles, and temporal-difference summaries. Evaluation is leave-one-trial-out: for each fold, one complete trial from every class is held out.

Models: Logistic Regression and Random Forest.

Primary metrics: macro one-vs-rest ROC-AUC, Macro-F1, and balanced accuracy. Trial-cluster bootstrap is used for 95% intervals. A class-preserving permutation null shuffles class assignments within each trial, retaining one observation per class per trial while destroying stable class association.

## Pilot results

| Task | Attacker/classifier | Macro OVR AUC | Macro-F1 | Balanced accuracy |
|---|---|---:|---:|---:|
| Identity privacy | Logistic Regression | 1.000 | 1.000 | 1.000 |
| Identity privacy | Random Forest | 1.000 | 0.967 | 0.967 |
| Activity utility | Logistic Regression | 1.000 | 1.000 | 1.000 |
| Activity utility | Random Forest | 1.000 | 1.000 | 1.000 |

For Logistic Regression, the class-preserving permutation null was centered near chance (privacy mean AUC ≈ 0.493; utility mean AUC ≈ 0.476). The current local pilot used 20 permutations, giving an exact Monte-Carlo floor of p = 1/21 ≈ 0.0476. This is a smoke-test significance check only; the final benchmark must use the pre-specified larger permutation count.

## Repeated-release pilot

To preserve independence, trials 1–5 were used to build attack-training aggregates and trials 6–10 were used only for testing. Aggregation was performed within identity.

| K releases | Logistic AUC | Logistic F1 | RF AUC | RF F1 |
|---:|---:|---:|---:|---:|
| 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| 2 | 1.000 | 1.000 | 1.000 | 1.000 |
| 5 | 1.000 | 1.000 | 1.000 | 1.000 |

The pilot cannot defensibly estimate **K=10** with independent attack-training and test observations because only 10 trials per identity are available. K=10, K=20, and K=50 remain Phase-3 targets with a larger repeated-observation set.

## Interpretation

The pilot shows that the selected CSI summaries contain a highly separable participant-associated signal under this narrow controlled subset. It does **not** establish that the signal is biometric identity rather than participant-correlated hardware, placement, gait, channel, or session artifacts. The perfect/near-perfect scores therefore trigger stronger confound testing rather than a headline claim of “100% identity leakage.”

The cumulative curve is saturated at K=1 in this subset, so it cannot demonstrate increasing leakage with K. The paper's cumulative-leakage claim requires a harder setting (cross-session/environment/device where possible), stronger privacy transformations, or lower-information releases that begin below saturation and can reveal composition over repeated releases.

## Exit conditions before final scientific claim

1. Expand identity count and activity coverage.
2. Run the full pre-specified permutation count and 5 seeds.
3. Add stronger confound controls and, where metadata permit, session/environment-disjoint evaluation.
4. Evaluate static privacy defenses and the proposed adaptive release controller.
5. Report K=1,2,5,10,20,50 only where independent repeated observations support those K values.
6. Replicate on at least one independent RF/CSI dataset.
7. Keep thresholds explicitly described as engineering operating points, not universal privacy standards.

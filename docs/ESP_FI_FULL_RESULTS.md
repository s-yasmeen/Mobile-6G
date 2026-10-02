# ESP-Fi HAR full Phase-2 experiment

## Dataset and QC

The full experiment uses 2,240 ESP-Fi HAR recordings:

- 4 scenarios
- 8 participants
- 7 activities
- 10 repeated trials
- 560 recordings per scenario

Each raw CSV packet contains 104 interleaved I/Q values, corresponding to 52 complex CSI coefficients. Scenario-1 MAT files were checked against the raw CSV representation and `CSIamp` is consistent with `sqrt(I^2 + Q^2)`. The main benchmark therefore uses raw CSVs for all four scenarios to avoid representation mismatch.

Model inputs contain CSI-derived amplitude statistics only. Scenario, participant, activity, trial, filenames, timestamps, MAC addresses, RSSI, and packet metadata are excluded from X.

Per-recording feature vector: 364 dimensions (52 coefficients × mean, standard deviation, Q25, median, Q75, mean absolute temporal difference, temporal-difference standard deviation).

## Evaluation protocol

Primary within-scenario split:
- attack/classifier training: trials 1–5
- held-out testing: trials 6–10

Models:
- one-vs-rest Logistic Regression (LR)
- Random Forest (RF)
- MLP

Metrics:
- macro one-vs-rest ROC-AUC
- Macro-F1
- balanced accuracy

A second, harder leave-one-scenario-out (LOSO) evaluation trains on three scenarios and tests on the fourth.

## Within-scenario results

### Identity/privacy (8 classes), average over four scenarios

| Model | Macro OVR AUC | Macro-F1 | Balanced accuracy |
|---|---:|---:|---:|
| LR | 0.977 | 0.859 | 0.861 |
| RF | 0.974 | 0.806 | 0.807 |
| MLP | 0.967 | 0.768 | 0.771 |

LR identity AUC by scenario:
- S1: 0.970
- S2: 0.951
- S3: 0.990
- S4: 0.998

### Activity utility (7 classes), average over four scenarios

| Model | Macro OVR AUC | Macro-F1 | Balanced accuracy |
|---|---:|---:|---:|
| LR | 0.857 | 0.553 | 0.561 |
| RF | 0.877 | 0.599 | 0.606 |
| MLP | 0.793 | 0.437 | 0.444 |

These results show that participant-associated information is highly separable within an environment while legitimate activity information remains measurable.

## Cross-scenario generalization

### Identity/privacy LOSO, average over four held-out scenarios

| Model | Macro OVR AUC | Macro-F1 | Balanced accuracy |
|---|---:|---:|---:|
| LR | 0.600 | 0.153 | 0.217 |
| RF | 0.568 | 0.128 | 0.153 |
| MLP | 0.561 | 0.126 | 0.168 |

LR held-out-scenario identity AUC:
- test S1: 0.641
- test S2: 0.614
- test S3: 0.578
- test S4: 0.566

Interpretation: the strong within-scenario identity signal does not transfer cleanly to unseen environments. This is evidence of substantial environment/channel dependence and prevents an unsupported claim that the observed signal is a scenario-invariant biometric identity signature.

## Repeated-release / cumulative privacy

Independent construction:
- train attack model on trials 1–5
- test only on trials 6–10
- aggregate releases only within the same participant/activity
- K = 1, 2, 5

Average identity AUC across scenarios:

| Model | K=1 | K=2 | K=5 |
|---|---:|---:|---:|
| LR | 0.977 | 0.984 | 0.986 |
| RF | 0.973 | 0.979 | 0.984 |
| MLP | 0.968 | 0.975 | 0.981 |

Average LR Macro-F1 increases from 0.859 at K=1 to 0.881 at K=2 and 0.890 at K=5.

The direction is consistent across model families: repeated observations improve identity inference. The effect is modest because single-release leakage is already high.

K=10 is not reported from this 10-trial design because maintaining independent attack-training and test observations would be impossible. Larger K values remain a Phase-3 target requiring additional independent repeated observations or a different sequence protocol.

## Statistical smoke test

For Scenario 1 identity with LR:
- observed macro OVR AUC: 0.9703
- trial-cluster bootstrap 95% interval: [0.9643, 0.9756]
- class-preserving permutation null mean AUC: 0.4930
- 100 permutations
- empirical p = 0.0099

The full manuscript should increase permutation repetitions and repeat inference across seeds before treating p-values as final.

## Static privacy-defense sweep

A Gaussian perturbation baseline was evaluated with noise standard deviation expressed relative to each training feature's standard deviation. RF was used for the privacy–utility sweep.

Average across scenarios:

| Noise σ | Identity AUC | Activity balanced accuracy |
|---:|---:|---:|
| 0.00 | 0.973 | 0.609 |
| 0.25 | 0.970 | 0.546 |
| 0.50 | 0.958 | 0.444 |
| 1.00 | 0.917 | 0.340 |
| 2.00 | 0.823 | 0.235 |
| 4.00 | 0.688 | 0.179 |

Noise reduces privacy leakage, but utility collapses before the engineering privacy operating point is reached.

## Adaptive release decision

Using the pre-declared engineering privacy operating point AUC <= 0.55, no tested static-noise configuration satisfies the privacy condition while retaining useful activity performance. The correct fail-closed decision is therefore:

**BLOCK**

This threshold is a system-design operating point, not a universal privacy standard.

## Main scientific conclusion

1. ESP-Fi CSI contains strong participant-associated information within the same environment.
2. Identity inference is substantially environment dependent under leave-one-scenario-out testing.
3. Repeated releases increase identity inference performance from K=1 to K=2/K=5.
4. Naive Gaussian sanitization produces an unfavorable privacy–utility tradeoff.
5. A fail-closed adaptive gate correctly refuses release when no tested transformation meets the operating constraints.

These results support the cumulative-leakage and risk-adaptive assurance research direction, while also showing why cross-environment validation is essential.

## Limitations / next scientific requirements

- ESP-Fi is Wi-Fi CSI validation relevant to next-generation RF sensing; it is not itself a native 6G dataset.
- Replicate on an independent RF/CSI dataset.
- Increase permutation repetitions and run the pre-specified seed set.
- Evaluate stronger learned privacy transformations.
- For K=10/20/50, use a dataset/protocol with sufficient independent repeated observations.
- Do not interpret participant classification as proof of immutable biometric identity.

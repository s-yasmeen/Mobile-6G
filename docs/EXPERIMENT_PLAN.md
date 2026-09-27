# Experiment Plan

## Primary question
Does identity inference risk increase when an adversary combines repeated RF/ISAC releases?

## RQ1
How does identity leakage change with repeated observations?

## RQ2
Can cumulative leakage drive real-time ALLOW/SANITIZE/BLOCK decisions?

## RQ3
Can privacy risk be reduced while retaining useful sensing performance?

## Planned datasets
- mmHSense: primary candidate for modern mmWave/Wi-Fi/5G sensing experiments.
- OPERAnet: independent multimodal validation candidate.

## Core metrics
- Utility: macro-F1 / task accuracy.
- Privacy: identity attacker macro one-vs-rest ROC-AUC and macro-F1.
- Composition: attacker performance versus release count K.
- Systems: runtime/latency and memory overhead.

## Experimental controls
Use subject-aware splits where appropriate to prevent leakage between train/test partitions. Fit preprocessing on training data only. Report random seeds and confidence intervals. Do not claim 6G-native measurements when using Wi-Fi/5G datasets; treat them as RF/ISAC validation data for a next-generation-network framework.

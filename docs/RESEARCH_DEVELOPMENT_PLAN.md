# Research Development Plan: CLAPA for Sequential Privacy Assurance in 6G ISAC

## Working title

**Cumulative Leakage-Aware Adaptive Privacy Assurance for Sequential Sensing Releases in 6G Integrated Sensing and Communication Networks**

Working acronym: CLAPA. Retain as a provisional name until novelty and naming checks are complete.

## Current project state

The existing Mobile-6G repository contains:
- synthetic smoke-test data generation;
- generic CSV feature adapter;
- noise, quantization and clipping sanitizers;
- identity aggregation by non-overlapping mean blocks;
- an identity attacker and activity utility classifier;
- a threshold-based ALLOW/SANITIZE/BLOCK gate;
- a cumulative experiment script and plotting pipeline.

The README correctly warns that synthetic data is only for smoke testing and that real data is required for scientific claims.

## Audit findings requiring action

1. The current experiment uses random observation-level train/test splitting. This risks train/test contamination from correlated windows and sessions.
2. The data loader discards session and timestamp metadata.
3. Aggregation is based on sorted identity subsets, not a verified chronological sequence protocol.
4. The current privacy score is ROC-AUC. AUC is an attacker-performance metric, not a composable privacy budget and should not be added across releases.
5. Sanitization is applied to the full feature matrix before the split. Any data-dependent sanitizer or calibration would risk test-set leakage; fit parameters on training data only.
6. Thresholds in baseline.yaml are fixed constants and need validation-only calibration plus sensitivity analysis.
7. Dataset references mmHSense and OPERAnet have not yet been verified against official dataset records, data dictionaries, licences and required labels.
8. The current script should remain labelled exploratory until the protocol and data adapter are corrected.

## Proposed contribution

A release-history-aware controller that:
- models ordered sensing releases and stated adversarial side information;
- estimates sequence-level inference risk;
- selects ALLOW, SANITIZE or BLOCK for the next release;
- balances privacy risk, sensing utility and system cost;
- is evaluated against no protection, fixed sanitization, per-release gating and suitable formal-DP baselines.

The novelty claim must be narrowed after full-text comparison with adaptive DP feature release, operational leakage metrics, temporal-correlation privacy and recent physical-layer ISAC defenses.

## Research questions

- RQ1: How does adversarial inference change as an attacker receives longer ordered RF/ISAC release sequences?
- RQ2: Which sequence representations and side-information assumptions most affect the inference risk?
- RQ3: Does release-history-aware control outperform fixed and current-release-only policies on privacy–utility–cost trade-offs?
- RQ4: How robust is the controller across sessions, environments, devices and datasets?
- RQ5: What latency, memory and compute costs are introduced?

## Work packages

### WP1 — Evidence and novelty validation
- Complete a structured literature review with search strings, dates, screening rules and a verified bibliography.
- Read full text of direct-overlap studies.
- Build a matrix of threat model, leakage metric, release model, defense, dataset, baselines and limitations.
- Produce a novelty statement supported by the matrix.

### WP2 — Dataset qualification
- Verify mmHSense and OPERAnet or replace them with qualified public datasets.
- Check licence, participant/session labels, timestamp order, signal modality and repeated-release suitability.
- Choose one primary and one external validation dataset.
- Document preprocessing and feature extraction.

### WP3 — Mathematical formulation
Define release sequence X_{1:K}, protected attribute S, legitimate task Y, adversary side information Z, sanitizer/action A_t and utility/cost terms. Candidate risk measures include sequence-level posterior success, Bayes risk or calibrated information estimates. For a DP comparator, use formal composition only where the mechanism satisfies DP assumptions.

A candidate controller objective is:
minimize expected cumulative adversarial risk + lambda_u * utility loss + lambda_c * system cost,
subject to a minimum legitimate-task utility constraint and explicit release/action constraints.

This is a design template, not yet a proved guarantee. Derive assumptions and any bounds before claiming formal assurance.

### WP4 — Algorithm and implementation
- preserve metadata through the data pipeline;
- implement chronological sequence construction within sessions;
- implement session-aware splits and leakage checks;
- add sequence attacker baselines;
- implement history-aware state and controller;
- calibrate thresholds only on validation data;
- retain deterministic seeds and full run manifests.

### WP5 — Experiments
- evaluate K in {1,2,5,10,20}, subject to dataset support;
- compare sequence models and aggregation strategies;
- compare sanitizers and gate baselines;
- conduct ablations and shift tests;
- use participant/session-level bootstrap confidence intervals;
- report privacy, utility, latency and memory.

### WP6 — Manuscript and reproducibility
- revise title, abstract, introduction and related work only after novelty validation;
- include threat model, assumptions, equations, algorithm pseudocode and complexity;
- report negative/null results and limitations;
- publish code/configs/split manifests where licensing permits;
- verify every citation and numerical statement against source papers and run outputs.

## Publication integrity rules

- Never invent results, dataset properties, sample sizes, citations or DOI metadata.
- Do not present synthetic smoke tests as scientific validation.
- Do not call AUC a cumulative privacy budget.
- Do not claim formal DP unless its mathematical requirements and accountant are implemented.
- Do not call Wi-Fi/5G data native 6G measurements.
- Clearly distinguish preprints, conference papers, journal articles and standards documents.
- Preserve raw dataset licensing and participant privacy.

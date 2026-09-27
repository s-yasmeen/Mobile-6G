# Phase 2 Completion Status

## Implementation status: COMPLETE
The repository now contains the frozen protocol, official-schema audit, OPERAnet packet preparation contract, experiment-safe windowing, quality audit, group-disjoint utility and known-identity privacy splits, three pre-specified model families, five seeds, empirical permutation baselines, session-level cluster bootstrap confidence intervals, split manifests, run provenance, machine-readable result outputs, and CI smoke execution of the full benchmark runner.

## Scientific real-data status: BLOCKED ON DATA STAGING
This is deliberately not marked as a completed empirical study. The official OPERAnet wificsi1 item is approximately 33.98 GB. mmHSense data are distributed separately through IEEE DataPort. Neither dataset's raw observations are stored in this repository. Publication results must be generated only after official files are staged and their checksums/provenance recorded.

## Required real-data execution chain
1. Read/export official OPERAnet Wi-Fi CSI MAT data preserving packet metadata.
2. Run packet preparation/schema validation.
3. Run experiment-safe windowing.
4. Run experiments/run_phase2_baselines.py on the resulting feature table.
5. Archive data_quality.json, split_manifest.json, run_metadata.json, baseline_results.csv, baseline_summary.csv and permutation_baselines.csv.
6. Repeat the appropriate independent validation protocol on mmHSense only where labels support the stated task/threat model.

## Non-negotiable publication rule
No synthetic CI/smoke output may appear in a manuscript result table. Phase 2 becomes empirically COMPLETE only after official-data outputs satisfy the protocol and are reviewed for leakage, class support, session coverage and convergence.

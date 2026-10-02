# Phase 2 Discrepancy Audit

Status: OPEN. This audit is a pre-real-data quality gate.

## Corrected before real-data execution
- Bootstrap confidence intervals were specified but absent: implemented for macro-F1, balanced accuracy and identity macro OVR AUC.
- Permutation benchmark previously measured only macro-F1: extended to all declared privacy endpoints.
- Utility evaluation used random stratification despite the leakage-aware protocol: group-disjoint utility splitting is now used when session/experiment groups exist.
- Split reproducibility was undocumented: each run now writes a split manifest.
- Run provenance was promised but absent: runner now records input, config, seed/model set and Git commit.
- Unused validation_size was removed; fixed pre-specified models do not require a hidden tuning partition in the current Phase 2 protocol.

## Still open / must be resolved with official data
1. **Dataset schema:** exact mmHSense and OPERAnet files/columns must be inspected before adapters are considered final.
2. **mmHSense alignment:** do not assume gesture/localization and identity labels coexist for the same observation.
3. **OPERAnet RF representation:** the current CSV helper is not a raw CSI/UWB feature extractor. Signal-specific windowing/feature extraction must be defined after inspecting official files.
4. **Session cardinality:** each identity needs enough independent sessions/experiments to support known-identity group-disjoint evaluation.
5. **Class imbalance:** report per-class support; macro metrics remain primary.
6. **Window independence:** overlapping windows from the same recording must never cross train/test boundaries.
7. **Preprocessing leakage:** scaling/feature learning must be fit on training data only. sklearn pipelines satisfy this for current standardized models; future learned feature extraction must preserve it.
8. **Hyperparameters:** current models are fixed baselines. If tuning is later introduced, add nested/group-aware validation and document the search space before final evaluation.
9. **Statistical unit:** bootstrap resampling by individual windows can understate uncertainty for correlated RF windows. Final real-data CIs should use group/session-aware bootstrap where feasible.
10. **Cross-dataset comparability:** do not pool scores across datasets with different modalities/tasks; report each protocol separately and compare qualitative trends.
11. **Demographic/private attributes:** only evaluate attributes actually documented and ethically justified; do not infer undocumented sensitive traits.
12. **Phase 3 metrics:** K*, delta-privacy and repeated-release curves remain Phase 3 and must not be presented as Phase 2 results.

## Closure rule
Phase 2 cannot close until the official data resolve items 1–6 and the final statistical unit for item 9 is fixed and reported.

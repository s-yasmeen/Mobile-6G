# Literature Review: Privacy Leakage in RF Sensing and 6G ISAC (evidence scan, 16 Nov 2026)

## Scope and caution

This is a targeted evidence scan using SciSpace discovery/extraction and independent web verification. It is not yet a PRISMA systematic review. Bibliographic metadata, publication status, full-text assumptions, and claims must be checked against publisher or author versions before manuscript submission. Search snippets and AI-extracted fields are triage aids, not substitutes for reading the source.

## Emerging evidence relevant to this project

| Work | Contribution relevant to this study | Implication for our novelty |
|---|---|---|
| Su et al., *An Operational Leakage Metric for Eavesdropping in Joint Sensing and Communications Systems* (2026 preprint; arXiv:2609.27527) | Bayesian operational leakage based on an adversary's finite-record probability of reconstructing symbols or estimating sensing parameters; separates prior side information from observation-driven risk. | We cannot claim novelty for simply introducing an operational leakage probability. We need a sequential/compositional formulation over multiple releases, an explicit release-history model, and validated adaptive control. |
| Han, Meng & Masouros, *Physical-Layer Sensing Privacy via Constellation Shaping for OFDM-ISAC Systems: Theory, Design, and Experiments* (2026 preprint; arXiv:2609.25103) | Receiver-specific ranging MSE gap and constellation shaping; numerical and over-the-air evidence of a privacy–throughput trade-off. | Include as a strong physical-layer comparator or complementary sanitizer; distinguish our temporal release controller from waveform-level protection. |
| Chen et al., *Fine-Grained Privacy Control for OFDM-based Integrated Sensing and Communication* (IEEE INFOCOM 2026) | Range-Doppler-domain manipulation mapped to OFDM resource elements to impair unauthorized sensing while preserving legitimate decoding. | Compare against signal-level obfuscation; do not present generic sanitization as a new PHY mechanism. |
| *ISAC Privacy: Challenges and Solutions for 6G* (2026) | Organizes sensitive sensing data into location/environment, behavioral, and physiological levels; discusses privacy, consent, transparency and control. | Use a clear threat taxonomy and explain which sensitive attribute our experiments actually measure. |
| Qu et al., *Secure and privacy-preserving issues in integrated sensing and communication-enabled wireless networks: a survey* (2025/2026 issue) | Surveys physical/network-layer security and privacy; calls for scalable, adaptable frameworks and trustworthy collaborative ISAC. | Position CLAPA as a measurable adaptive control framework, not a general survey or broad privacy architecture. |
| *ISAC Privacy: Achieving Signal Indistinguishability via Joint Beamforming and Perturbation* (IEEE TCCN, 2026) | Joint secure beamforming and artificial noise; minimizes eavesdropper Jensen–Shannon distinguishability, including imperfect statistical CSI. | Include a distributional/indistinguishability comparator where implementation and assumptions permit. |
| *Privacy-Protection of Reference Signals via Transparent Artificial Multipath for ISAC* (IEEE TWC, 2026) | Transparent artificial multipath distorts adversarial channel estimates while preserving legitimate localization/communication. | A recent competing PHY defense; explicitly compare scope and threat model. |
| *Differentially Private Feature Release for Wireless Sensing: Adaptive Privacy Budget Allocation on CSI Spectrograms* (2025 preprint) | Adaptive DP budget allocation for released CSI features. | This is a direct overlap risk. Our contribution must specify what is different: sequential adversarial inference measurement, release-history-aware action policy, and/or rigorous composition accounting—not merely adaptive thresholds or adaptive epsilon. |
| *An investigation of the private-attribute leakage in WiFi sensing* (2024) | Empirically studies inference of private physical attributes from WiFi sensing data. | Supports evaluating sensitive attributes beyond activity utility; verify the full paper, dataset details and reported metrics. |
| *A Multi-Radio Audit of Subject-Dependent Performance in Recent Public WiFi CSI Datasets* (2026) | Shows random-window evaluation can inflate performance relative to subject-disjoint protocols on WiStride, ElderAL-CSI and SHARP-80. | Makes leakage-resistant splits and session/subject-aware evaluation essential. |
| *Protecting the Moving User’s Locations by Combining Differential Privacy and k-Anonymity under Temporal Correlations in Wireless Networks* (2021) | Addresses temporal correlation in location privacy. | Temporal composition is not a new concept generally; articulate the specific gap in RF/ISAC release-level adversarial inference and adaptive control. |

## Official standards and governance context

- ETSI GR ISC 004 V1.1.1 (March 2026) addresses security, privacy, trustworthiness and sustainability for 6G ISAC, including unauthorized sensing, consent, transparency and sensing-data handling.
- Do not imply that this prototype is a 3GPP- or ETSI-compliant implementation. It is a research framework informed by standards discussions.

## Preliminary research gap (must be validated)

The defensible candidate gap is not "privacy leakage accumulates over time" in the broad sense. Prior work already studies temporal correlations and adaptive privacy budgets. The narrower, testable gap is:

> A reproducible, release-history-aware evaluation and control framework for measuring how an adversary's inference capability changes when it jointly processes sequential RF/ISAC sensing releases, and for selecting per-release actions under explicit sensing-utility and system-cost constraints.

The paper must demonstrate all three:
1. **Sequential adversary model:** the attacker receives ordered releases and can use temporal aggregation or sequence models, not only a mean of non-overlapping windows.
2. **Cumulative risk measure:** report adversarial success/posterior risk or a defensible information measure over the complete sequence. Do not add AUC values or call AUC itself a formal privacy budget.
3. **Adaptive policy value:** show that release-history-aware control improves the privacy–utility–cost frontier against fixed and per-release baselines under the same attacker and data splits.

## Dataset qualification: verified starting point

### Primary candidate: mmHSense

The mmHSense paper and public code/data entry have now been verified:
- Six labeled mmWave ISAC datasets are provided for gesture recognition, pose estimation, localization and person identification.
- The mmW-GaitID task is directly relevant to identity inference: the paper reports 20 participants, collection over three days, 60-GHz CSI at 10 Hz, and a paired 5-GHz CSI modality.
- The paper reports approximately 26,000 60-GHz CSI samples per device pair and describes an evaluation representation of 1,318 examples with 60 concatenated features and 20 time steps.
- The companion code identifies mmW-GaitID as a 20-class classification task and provides a loader for the combined tensors.
- The paper also documents mmW-Loc with 20 participants and a 4×5 localization grid, potentially useful for location privacy experiments.
- The dataset paper is IEEE Access (2026), DOI 10.1109/ACCESS.2026.3691174. The code repository states CC BY 4.0 and links to IEEE DataPort.

**Important qualification:** the public example loader returns combined data and labels, but does not expose session/day/timestamp metadata in its simple interface. The paper says collection spans three days, but this alone does not prove repeated sessions for the same participant. Before using the new session-disjoint runner, inspect the raw archive and metadata. If per-participant session labels are absent, use a documented chronological within-recording split with a purge gap only if original ordering can be reconstructed; otherwise restrict claims to the split the dataset actually supports. Do not manufacture session labels.

### Secondary candidate: OPERAnet

OPERAnet is verified as an open-access Scientific Data dataset (2022), DOI 10.1038/s41597-022-01573-2:
- approximately eight hours of synchronized measurements;
- two rooms and six participants;
- six daily activities;
- WiFi CSI, passive WiFi radar, UWB and Kinect modalities;
- high-temporal-resolution activity and location annotations;
- CC BY 4.0 publication licence.

OPERAnet is useful as an independent RF/multimodal activity and localization validation dataset. Its six-participant scale is limited, and participant identity-label availability and sequence/session mapping must be confirmed from the actual files before treating it as an identity re-identification benchmark.

### Additional candidate datasets

SciSpace surfaced WiMANS, EHUNAM, eHealth CSI, an 80-MHz WiFi CSI dataset, WiStride, ElderAL-CSI, SHARP-80 and CSI-based Device-free Localization and Obfuscation. These remain secondary candidates pending verification of original files, licences, participant/session labels and temporal ordering.

Dataset selection must be based on actual downloadable files, label availability, participant/session structure, consent and licence, not paper abstracts alone. Do not combine datasets with incompatible label semantics into a single pooled benchmark without a justified harmonization protocol.

## Bibliographic and dataset starting points

- Operational leakage metric: https://arxiv.org/abs/2609.27527
- Constellation shaping: https://arxiv.org/abs/2609.25103
- ISAC privacy review: https://arxiv.org/abs/2605.28325
- Fine-grained OFDM privacy control: https://doi.org/10.1109/infocom59046.2026.11571379
- ISAC privacy via signal indistinguishability: https://doi.org/10.1109/TCCN.2026.3704837
- Transparent artificial multipath: https://doi.org/10.1109/TWC.2026.3733285
- ISAC security/privacy survey: https://doi.org/10.1186/s13634-025-01277-w
- ETSI GR ISC 004 overview: https://www.etsi.org/newsroom/news/2647-report-6g-isac-security-privacy-sustainability/
- mmHSense paper: https://doi.org/10.1109/ACCESS.2026.3691174
- mmHSense code and IEEE DataPort link: https://github.com/nisarnabeel/Multi-Modal-and-Distributed-mmWave-ISAC-Datasets-for-Human-Sensing
- OPERAnet paper and dataset details: https://doi.org/10.1038/s41597-022-01573-2

## Required next literature-review actions

1. Retrieve and read full texts for the direct-overlap papers (adaptive DP feature release, operational leakage, temporal-correlation location privacy, private-attribute leakage).
2. Extract equations, threat models, release assumptions, baselines, datasets, and limitations into a verified matrix.
3. Inspect the downloaded mmHSense and OPERAnet archives and metadata to determine whether session-aware evaluation is possible.
4. Search citation chains and related work for sequential/compositional leakage in RF sensing, CSI, localization, ISAC and privacy-preserving feature release.
5. Record inclusion/exclusion criteria and search dates before describing the review as systematic.


## Addendum — newer direct-overlap evidence and dataset reprioritization (16 Nov 2026)

### Directly relevant 2025–2026 studies

- *Differentially Private Feature Release for Wireless Sensing: Adaptive Privacy Budget Allocation on CSI Spectrograms* (2025 preprint) already proposes clipping, calibrated Gaussian noise, adaptive blockwise privacy-budget allocation, RDP composition accounting and identity/membership inference evaluation. Its reported guarantee is sample-level DP; user-level protection requires separate grouping/accounting. This is a direct comparator, not a gap we can claim to have invented.
- *An Operational Leakage Metric for Eavesdropping in Joint Sensing and Communications Systems* (2026) proposes finite-record Bayesian operational leakage and explicitly distinguishes prior adversarial side information from observation-driven success. The new paper must therefore focus on sequential sensing prefixes and empirical dataset-grounded attacks, not simply a Bayesian leakage scalar.
- *Learning Identity Beyond Activity: Open-Set User Verification with WiFi CSI* (2026) frames CSI identity inference as pairwise verification and reports central-holdout and leave-one-subject-out protocols. Closed-set identification and open-set verification must remain separate tasks in our evaluation.
- *Resource-Efficient Wi-Fi CSI-Based Sensing via Exploiting the Age of Samples* (2026) studies age-aware sensing under sparse/irregular CSI reporting. Our release model should preserve timestamps or sample ages and include staleness/packet-gap sensitivity tests.
- *Adaptive Privacy of Sequential Data Releases Under Collusion* (2026) further confirms that adaptive sequential privacy and colluding recipients are established topics outside wireless sensing. The contribution must be domain- and protocol-specific.

### Dataset priority change: CSI-Bench

CSI-Bench (NeurIPS 2025 Datasets and Benchmarks Track) is now the preferred primary candidate over mmHSense because its described data scale and labels are better aligned with the core experiment: more than 461 hours, 35 users, 26 environments, 16 device types, and a multitask component with identity, activity and proximity annotations. Its documented directory structure includes user/activity/environment/device/session path components and metadata/split files.

- NeurIPS paper: https://proceedings.neurips.org/paper_files/paper/2025/hash/f7c68372b3d39e8d7a093eb2edaaad87-Abstract-Datasets_and_Benchmarks_Track.html
- Project page: https://ai-iot-sensing.github.io/projects/project.html
- Author code repository: https://github.com/guozhen-jenn-zhu/CSI-Bench-Real-WiFi-Sensing-Benchmark
- Dataset access page: https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench

The project page reports high user-identification performance on its in-distribution benchmark. These are author-reported results and must not be presented as results produced by CLAPA. The author repository reports additional cross-device/environment splits; reproduce and verify those results against the current dataset version before quoting exact values.

The code repository has an MIT licence, but this does not establish the dataset's licence. The Kaggle dataset terms must be checked independently. A diagnostic utility, `experiments/qualify_csi_bench.py`, has been added to inspect metadata columns, label counts, common-key overlap, file references and explicit path-derived user/session structure. Its output is not an admission approval: the researcher must manually review the report and verify data terms, duplicates and label semantics.

### Updated research position

The strongest candidate contribution is an empirical system study of history-aware privacy–utility–cost control over sequential wireless sensing releases, with:
1. sequence-prefix adversarial success and calibration rather than summed AUC;
2. aligned identity and legitimate-task labels from the same records;
3. held-out session, device and environment evaluation;
4. fixed, current-release-only, history-aware and formally accounted DP comparators; and
5. participant/session-level confidence intervals and runtime cost.

Do not claim a new general theory of sequential privacy, a first Bayesian operational leakage metric, or formal DP. The literature review remains a targeted evidence scan, not a systematic review.

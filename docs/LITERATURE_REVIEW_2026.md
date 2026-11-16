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

- ETSI GR ISC 004 V1.1.1 (March 2026) addresses security, privacy, trustworthiness and sustainability for 6G ISAC, including unauthorized sensing, consent, transparency and sensing-data handling. Use it to ground system requirements and threat assumptions.
- Do not imply that this prototype is a 3GPP- or ETSI-compliant implementation. It is a research framework informed by standards discussions.

## Preliminary research gap (must be validated)

The defensible candidate gap is not "privacy leakage accumulates over time" in the broad sense. Prior work already studies temporal correlations and adaptive privacy budgets. The narrower, testable gap is:

> A reproducible, release-history-aware evaluation and control framework for measuring how an adversary's inference capability changes when it jointly processes sequential RF/ISAC sensing releases, and for selecting per-release actions under explicit sensing-utility and system-cost constraints.

The paper must demonstrate all three:
1. **Sequential adversary model:** the attacker receives ordered releases and can use temporal aggregation or sequence models, not only a mean of non-overlapping windows.
2. **Cumulative risk measure:** report adversarial success/posterior risk or a defensible information measure over the complete sequence. Do not add AUC values or call AUC itself a formal privacy budget.
3. **Adaptive policy value:** show that release-history-aware control improves the privacy–utility–cost frontier against fixed and per-release baselines under the same attacker and data splits.

## Candidate datasets: verification status

The repository currently names mmHSense and OPERAnet, but this evidence scan did not establish authoritative dataset records, data dictionaries, identity labels, session structure, licences or reproducible download instructions for either. Treat both as **unverified candidates**, not confirmed experimental inputs.

SciSpace surfaced potentially relevant alternatives:
- WiMANS: multi-user WiFi activity sensing; verify whether identity labels and raw CSI are available for the required attack.
- EHUNAM: WiFi CSI for human and machine sensing; verify participant/session annotations and licence.
- eHealth CSI: reported as involving more than 100 participants; verify exact data modalities, consent/usage terms and identity labels.
- 80-MHz WiFi CSI dataset: reports 13 subjects across environments, days and hardware; verify release files and licence.
- WiStride, ElderAL-CSI and SHARP-80: mentioned in a 2026 evaluation audit; verify original dataset pages and access terms.
- CSI-based Device-free Localization and Obfuscation dataset: includes CSI traces and obfuscation conditions; verify identity labels and licence.

Dataset selection must be based on actual downloadable files, label availability, participant/session structure, consent and licence, not paper abstracts alone. Do not combine datasets with incompatible label semantics into a single pooled benchmark without a justified harmonization protocol.

## Bibliographic starting points

- Operational leakage metric: https://arxiv.org/abs/2609.27527
- Constellation shaping: https://arxiv.org/abs/2609.25103
- ISAC privacy review: https://arxiv.org/abs/2605.28325
- Fine-grained OFDM privacy control: https://doi.org/10.1109/infocom59046.2026.11571379
- ISAC privacy via signal indistinguishability: https://doi.org/10.1109/TCCN.2026.3704837
- Transparent artificial multipath: https://doi.org/10.1109/TWC.2026.3733285
- ISAC security/privacy survey: https://doi.org/10.1186/s13634-025-01277-w
- ETSI GR ISC 004 news/overview: https://www.etsi.org/newsroom/news/2647-report-6g-isac-security-privacy-sustainability/

## Required next literature-review actions

1. Retrieve and read full texts for the direct-overlap papers (adaptive DP feature release, operational leakage, temporal-correlation location privacy, private-attribute leakage).
2. Extract equations, threat models, release assumptions, baselines, datasets, and limitations into a verified matrix.
3. Search citation chains and related work for sequential/compositional leakage in RF sensing, CSI, localization, ISAC and privacy-preserving feature release.
4. Record inclusion/exclusion criteria and search dates before describing the review as systematic.

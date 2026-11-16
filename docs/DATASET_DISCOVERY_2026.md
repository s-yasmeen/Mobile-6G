# Real RF/CSI dataset discovery — 16 November 2026

## Executive result

The expanded search identified multiple real datasets. The recommended order is:

1. **EHUNAM** — first pilot for joint identity/activity privacy–utility evaluation.
2. **CSI-Bench** — scale and cross-environment/device benchmark.
3. **CSI-GaitCov** — independent identity and covariate-shift replication.
4. **mmHSense** — mmWave/ISAC transfer experiment.
5. **BFId** — identity-only external validation if non-commercial access agreement is obtained.

This is a dataset discovery and suitability assessment. No raw archive has been downloaded or executed in this repository yet.

## 1. EHUNAM — best first joint identity/activity pilot

- Paper: https://doi.org/10.1038/s41597-025-06238-4
- Data archive: https://doi.org/10.6084/m9.figshare.28541225
- Dataset code/schema: https://github.com/GuillermoDiazSM/EHUNAM-dataset
- Repository reports CC BY 4.0.

The Scientific Data paper describes 2,401 measurement files, approximately 38 hours over 23 days, 21 participants, eight environments/scenarios and three measurement campaigns. Records include CSI and metadata fields for participant IDs (`People`), `Activity`, `Environment`, `Date`, `Time`, receiver, NIC, campaign/set and packet timestamps. The paper explicitly says people-identification is possible from the HAR and people-counting data. MC1 includes single-person activity recordings such as walking, jumping, standing, sitting and sit/stand transitions. Individual measurements are typically 60 seconds long, and packet timestamps allow chronological release windows.

**Why this is the best pilot:** the same measurement records can potentially support protected identity and legitimate activity labels, while packet timestamps support ordered within-recording release sequences. Start with unambiguous single-person MC1 records.

**Cautions:**
- Confirm participant ID overlap across dates, environments and campaigns before claiming cross-day or cross-environment identity generalization.
- Do not assume that all 21 participants appear in every campaign or that every participant was recorded on multiple days.
- MC1/MC2/MC3 differ in NIC, CSI extractor, band, bandwidth and collection configuration. Treat these as domain variables, not interchangeable samples.
- Multi-person captures require explicit attribution. Do not mix them into the first pilot without a validated label protocol.
- The data paper documents ethics approval and informed consent. Use only the released anonymous participant IDs.

## 2. CSI-Bench — best scale/generalization benchmark

- NeurIPS 2025 paper: https://proceedings.neurips.cc/paper_files/paper/2025/hash/f7c68372b3d39e8d7a093eb2edaaad87-Abstract-Datasets_and_Benchmarks_Track.html
- Project: https://ai-iot-sensing.github.io/projects/project.html
- Code/schema: https://github.com/guozhen-jenn-zhu/CSI-Bench-Real-WiFi-Sensing-Benchmark
- Dataset access: https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench

The paper describes more than 461 hours, 35 users, 26 environments and a co-labelled multitask dataset with identity, activity and proximity. The author repository documents task metadata, split manifests and paths that encode user, activity, environment, device and session timestamp.

**Why it matters:** it offers stronger scale and diversity for held-out device/environment analysis.

**Cautions:** independently verify the Kaggle dataset terms; the code repository's MIT licence does not license the dataset. Confirm common stable keys and one-to-one record alignment across identity/activity/proximity tables before joining them. The paper's reported benchmark numbers are author results, not CLAPA results.

## 3. CSI-GaitCov — independent identity/covariate replication

- Zenodo archive: https://doi.org/10.5281/zenodo.22757555
- Data in Brief paper: https://doi.org/10.1016/j.dib.2026.113303
- Open article: https://pmc.ncbi.nlm.nih.gov/articles/PMC13677237/

The dataset article describes 2,500 trial-level recordings from 25 anonymized participants, 100 trials per participant, with walking direction and backpack-carrying conditions. Raw CSVs preserve packet timestamps, RSSI, acquisition metadata and CSI payload; processed NPZ files provide four CSI streams × 512 time samples × 245 subcarriers. The release includes a manifest, data dictionary, predefined splits and validation notebook. The Zenodo page reports a 14.4 GB archive.

**Why it matters:** excellent independent identity-inference replication under controlled covariate changes and repeated trials.

**Cautions:** it is gait/identity-focused, not broad activity recognition. Treat direction/carrying as auxiliary tasks or nuisance strata, not generic HAR. The population is 25 adult male participants from one indoor lab. Verify the archive's own LICENSE.txt and reuse terms; the Zenodo landing page did not expose an explicit licence field, although the associated paper is open access under CC BY.

## 4. mmHSense — 6G/ISAC transfer

- Paper: https://doi.org/10.1109/ACCESS.2026.3691174
- Code: https://github.com/nisarnabeel/Multi-Modal-and-Distributed-mmWave-ISAC-Datasets-for-Human-Sensing
- DataPort: https://ieee-dataport.org/documents/mmhsense-multi-modal-and-distributed-mmwave-isac-datasets-human-sensing

Six labelled datasets include mmW-GaitID (person identification), mmW-Loc (localization), gesture and pose tasks. The published work reports 20 participants in the GaitID/Loc collection and paired 60 GHz/5 GHz CSI. Inspect raw archive labels and session metadata before asserting repeated per-user sessions. Use this as the direct mmWave/ISAC transfer test after the first Wi-Fi CSI pilot.

## 5. BFId — identity-focused external validation, access by agreement

- Dataset: https://ps.tm.kit.edu/english/bfid-dataset/index.php
- Paper: https://doi.org/10.5445/IR/1000185756

KIT reports BFI and CSI recordings from 197 individuals. Access is for non-commercial research and requires a signed agreement and institutional information. Use as an identity-attack benchmark unless the archive confirms an aligned legitimate-task label.

## 6. Smaller or restricted alternatives

| Dataset | Evidence | Suitability |
|---|---|---|
| WiFi gait identity (UCSB) | 18 people, seven areas, 196 walk samples; academic access by request | Small identity/environment replication |
| WiFi-Wild | 2.4 GB raw CSI; Zenodo files restricted | HAR candidate; identity labels not established |
| Wi-Fi 6 802.11ax tracking/activity | About 200 minutes, 51.8 GB archive | Tracking/activity only unless identity labels are found |
| Human-to-human interaction CSI | 40 pairs, 12 interaction classes | Interaction utility; identity/temporal fields require inspection |
| SHD-HAR | Six participants, 10 activities, timestamped CSVs | Small utility-only validation |

Links:
- UCSB gait: https://web.ece.ucsb.edu/mostofi-lab/WiFiGaitIDDataset.html
- WiFi-Wild: https://doi.org/10.5281/zenodo.18431784
- 802.11ax: https://doi.org/10.5281/zenodo.21335109
- Interaction CSI: https://data.mendeley.com/datasets/3dhn4xnjxw/1
- SHD-HAR: https://doi.org/10.5281/zenodo.11201414

## Recommended experimental sequence

1. Obtain EHUNAM from Figshare; inspect archive and terms. Build a first pilot on single-person MC1 records with identity and activity labels.
2. Divide each CSI recording into ordered timestamped packet/window releases. Evaluate identity attack success for prefixes K = 1, 2, 5, 10, 20 where data length permits.
3. Preserve file, participant, date, environment, campaign, receiver and NIC metadata. Split by measurement file/session; do not randomly distribute adjacent windows across train and test.
4. Fit preprocessing, sanitizer strength and risk calibration on training/validation data only.
5. Evaluate activity macro-F1 and calibrated identity success on the same underlying records.
6. Replicate identity/covariate findings on CSI-GaitCov.
7. Evaluate scale and device/environment shift on CSI-Bench after verifying data terms and label alignment.
8. Transfer selected experiments to mmHSense to support the 6G ISAC positioning.

No empirical CLAPA result should be claimed until these steps are completed on the downloaded raw archives.

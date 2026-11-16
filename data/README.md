# Data

Do not commit raw participant/RF datasets to this repository.

## Generic CSV contract

For the generic feature pipeline, CSV should contain:
- `identity`: pseudonymous participant/person label
- `activity`: utility/task label
- `session`: acquisition session or recording identifier, where available
- `timestamp` or an original ordered sample index, where available
- numeric feature columns
- optional `environment`, `device`, and `radio`

For session-disjoint experiments, each identity must have at least two distinct sessions. If this condition is not met, do not create artificial session labels. Use a chronological within-recording holdout with a purge gap only if original order and recording boundaries are recoverable.

## Primary dataset candidate: mmHSense

Verified paper: Bhat et al., *mmHSense: Multi-Modal and Distributed mmWave ISAC Datasets for Human Sensing*, IEEE Access (2026), DOI: 10.1109/ACCESS.2026.3691174.

- Official code: https://github.com/nisarnabeel/Multi-Modal-and-Distributed-mmWave-ISAC-Datasets-for-Human-Sensing
- Dataset download: https://ieee-dataport.org/documents/mmhsense-multi-modal-and-distributed-mmwave-isac-datasets-human-sensing
- Code repository states CC BY 4.0; confirm data-port terms and attribution before reuse.
- The mmW-GaitID task is the best starting point for identity inference: the paper reports 20 participants, three collection days, 60-GHz CSI at 10 Hz and paired 5-GHz CSI.
- The mmW-Loc task reports 20 participants and a 4×5 localization grid; use it for a distinct location-privacy task, not as the same label space as identity.
- The companion loader returns combined tensors and labels but does not expose session/day/timestamp fields. Inspect raw archive and metadata before selecting a temporal split. Do not assume participants were recorded repeatedly across days.

## Secondary dataset candidate: OPERAnet

Verified paper: Bocus et al., *OPERAnet, a multimodal activity recognition dataset acquired from radio frequency and vision-based sensors*, Scientific Data (2022), DOI: 10.1038/s41597-022-01573-2.

- Paper: https://doi.org/10.1038/s41597-022-01573-2
- Dataset is available through the linked Figshare record in the paper.
- Approximately eight hours of measurements across two rooms, six participants and six daily activities.
- Modalities include WiFi CSI, passive WiFi radar, UWB and Kinect.
- The publication is CC BY 4.0. Confirm each downloaded file's licence and data dictionary.
- Verify whether participant identity and recording/session metadata are available before using it for re-identification. Its small participant count limits identity generalisation claims.

## Run the current sequence protocol

After transforming a qualified dataset into the CSV schema above:
```bash
python experiments/run_sequence_protocol.py --csv data/processed/features.csv --sanitizer none
python experiments/run_sequence_protocol.py --csv data/processed/features.csv --sanitizer noise --strength 0.25
```

This runner evaluates known-identity re-identification across held-out sessions. It is not appropriate for a dataset without repeated sessions per identity.

## Other candidates

WiMANS, EHUNAM, eHealth CSI, an 80-MHz WiFi CSI dataset, WiStride, ElderAL-CSI, SHARP-80 and CSI-based Device-free Localization and Obfuscation may be useful alternatives. Verify original files, labels, licence and temporal structure before admission.

Keep dataset licences and official citations with any derived local data. The repository intentionally does not redistribute third-party data.


## Revised dataset prioritization (16 Nov 2026)

The dataset priority is updated after inspecting the NeurIPS 2025 CSI-Bench paper, project page and current author code repository. **CSI-Bench is now the preferred primary candidate**, subject to the admission gates below. This supersedes the earlier preliminary priority given to mmHSense.

### Primary candidate: CSI-Bench

- NeurIPS 2025 Datasets and Benchmarks paper: https://proceedings.neurips.cc/paper_files/paper/2025/hash/f7c68372b3d39e8d7a093eb2edaaad87-Abstract-Datasets_and_Benchmarks_Track.html
- Project page: https://ai-iot-sensing.github.io/projects/project.html
- Code/data layout: https://github.com/guozhen-jenn-zhu/CSI-Bench-Real-WiFi-Sensing-Benchmark
- Kaggle data entry: https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench

The paper describes over 461 hours of CSI data, 35 users, 26 environments and 16 device types. The multitask benchmark includes joint user identity, activity and proximity labels. The documented directory layout encodes user, activity, environment, device and session timestamp; task metadata and split files are supplied.

The author project page reports high in-distribution user-identification performance (single-task accuracy/F1 99.51%/99.51%; multitask 99.83%/100.00%). These are author-reported baseline figures, not Mobile-6G/CLAPA results. They motivate the identity-leakage experiment but do not establish our method's performance.

**Before admission:** independently verify the Kaggle dataset licence/terms (the code repository's MIT licence does not automatically license the dataset); inspect the latest data release; confirm that the UID, HAR and proximity metadata share stable sample IDs or file paths; validate repeated sessions per user; parse timestamp/session semantics; inspect missing/corrupt files; and preserve the official split definitions for baseline reproduction. If identity and utility records cannot be joined unambiguously, run separate task experiments and do not claim a joint privacy–utility evaluation.

### Dataset qualification utility

After downloading the dataset under its published terms, run:

```bash
python experiments/qualify_csi_bench.py --root /path/to/CSI-Bench
```

The script reports metadata columns, label distributions, stable-key overlap across UID/HAR/proximity tables, per-user session counts inferred from file paths where possible, referenced-file availability, and representative HDF5 keys/shapes. It is a diagnostic only; its output must be reviewed before converting data to the generic feature CSV.

### Secondary candidates

- **mmHSense:** keep mmW-GaitID and mmW-Loc as separate mmWave/ISAC replication tasks. Do not infer repeated participant sessions from the statement that collection spanned three days.
- **OPERAnet:** use for secondary RF activity/localization sensitivity analysis; its six-participant scale limits identity generalization claims.

No dataset archive has yet been inspected locally, and no CLAPA real-data experiment has been run.

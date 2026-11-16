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

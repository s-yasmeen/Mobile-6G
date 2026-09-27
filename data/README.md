# Data
Do not commit raw participant/RF datasets to this repository.

## Generic CSV contract
For immediate experiments, export extracted features as CSV with:
- `identity`: participant/person label
- `activity`: utility/task label
- numeric feature columns
- optional `timestamp`, `session`

Run: `python experiments/run_cumulative.py --csv data/processed/features.csv`

## Planned external validation
1. mmHSense: map released feature arrays to identity + sensing-task labels.
2. OPERAnet: derive synchronized RF feature windows and map participant/activity labels.

Keep dataset licenses and official citations with any derived local data. The repository intentionally does not redistribute third-party data.

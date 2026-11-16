"""Qualify a local CSI-Bench archive before any privacy experiment.

This is an inspection-only utility. It does not alter, upload, or redistribute data.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

TASKS = (
    "HumanIdentification",
    "HumanActivityRecognition",
    "ProximityRecognition",
)
KEY_CANDIDATES = ("sample_id", "id", "record_id", "file_path", "filepath", "path")
LABEL_CANDIDATES = ("label", "identity", "user_id", "activity", "proximity")


def parse_recording_path(value: Any) -> dict[str, str | None]:
    """Extract only explicit path tokens; never invent missing session metadata."""
    raw = str(value).replace("\\", "/")
    parts = [p for p in raw.split("/") if p]
    patterns = {
        "identity": r"^(user_[^/]+)$",
        "activity": r"^(act_[^/]+)$",
        "environment": r"^(env_[^/]+)$",
        "device": r"^(device_[^/]+)$",
        "session": r"^(session_[^/]+)$",
    }
    result: dict[str, str | None] = {k: None for k in patterns}
    for part in parts:
        for field, pattern in patterns.items():
            if re.match(pattern, part, flags=re.IGNORECASE):
                result[field] = part
    return result


def choose_join_key(left: pd.DataFrame, right: pd.DataFrame) -> str | None:
    """Choose a shared stable key only when both tables contain it."""
    for key in KEY_CANDIDATES:
        if key in left.columns and key in right.columns:
            return key
    return None


def summarize_metadata(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    summary: dict[str, Any] = {
        "metadata_path": str(path),
        "rows": int(len(frame)),
        "columns": list(map(str, frame.columns)),
        "missing_by_column": {
            str(c): int(frame[c].isna().sum()) for c in frame.columns
        },
    }
    if "label" in frame.columns:
        counts = frame["label"].astype(str).value_counts(dropna=False)
        summary["label_counts"] = {str(k): int(v) for k, v in counts.items()}
    for candidate in KEY_CANDIDATES:
        if candidate in frame.columns:
            summary[f"{candidate}_unique"] = int(frame[candidate].nunique(dropna=True))
            summary[f"{candidate}_duplicates"] = int(frame[candidate].duplicated().sum())
    path_col = next((c for c in ("file_path", "filepath", "path") if c in frame.columns), None)
    if path_col:
        parsed = [parse_recording_path(v) for v in frame[path_col].dropna().astype(str)]
        for field in ("identity", "activity", "environment", "device", "session"):
            values = [p[field] for p in parsed if p[field] is not None]
            summary[f"path_{field}_unique"] = len(set(values))
        pairs = {
            (p["identity"], p["session"])
            for p in parsed
            if p["identity"] is not None and p["session"] is not None
        }
        users = {u for u, _ in pairs}
        summary["path_user_session_pairs"] = len(pairs)
        summary["path_users_with_multiple_sessions"] = sum(
            1 for user in users
            if len({session for u, session in pairs if u == user}) > 1
        )
    return summary


def resolve_recording_path(root: Path, task_dir: Path, value: str) -> Path | None:
    candidate = Path(value)
    candidates = [candidate] if candidate.is_absolute() else [
        root / candidate,
        task_dir / candidate,
        task_dir / "metadata" / candidate,
    ]
    for item in candidates:
        resolved = item.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved
    return None


def inspect_h5(path: Path) -> dict[str, Any]:
    try:
        import h5py
    except ImportError:
        return {"inspection": "skipped: install h5py to inspect HDF5 payloads"}
    try:
        with h5py.File(path, "r") as handle:
            return {
                "keys": list(handle.keys()),
                "datasets": {
                    key: list(handle[key].shape)
                    for key in handle.keys()
                    if hasattr(handle[key], "shape")
                },
            }
    except Exception as exc:  # report corrupt/unreadable files without aborting audit
        return {"error": f"{type(exc).__name__}: {exc}"}


def qualify(root: Path, tasks: tuple[str, ...] = TASKS, sample_files: int = 5) -> dict[str, Any]:
    root = root.resolve()
    report: dict[str, Any] = {
        "dataset_root": str(root),
        "tasks": {},
        "cross_task_alignment": {},
        "license_notice": (
            "Code-repository licence does not establish the dataset licence. "
            "Verify the Kaggle dataset terms and any restrictions before research use."
        ),
    }
    frames: dict[str, pd.DataFrame] = {}
    task_dirs: dict[str, Path] = {}

    for task in tasks:
        task_dir = root / task
        if not task_dir.exists():
            task_dir = root / "Multitask" / task
        metadata_path = task_dir / "metadata" / "sample_metadata.csv"
        if not metadata_path.exists():
            report["tasks"][task] = {
                "status": "metadata_not_found",
                "expected": str(metadata_path),
            }
            continue
        try:
            frame = pd.read_csv(metadata_path)
            frames[task] = frame
            task_dirs[task] = task_dir
            summary = summarize_metadata(metadata_path)
            path_col = next((c for c in ("file_path", "filepath", "path") if c in frame.columns), None)
            if path_col:
                examples = []
                for raw in frame[path_col].dropna().astype(str).head(sample_files):
                    resolved = resolve_recording_path(root, task_dir, raw)
                    item: dict[str, Any] = {
                        "reference": raw,
                        "exists": resolved is not None,
                    }
                    if resolved is not None and resolved.suffix.lower() in {".h5", ".hdf5"}:
                        item["hdf5"] = inspect_h5(resolved)
                    examples.append(item)
                summary["file_examples"] = examples
                summary["existing_file_examples"] = sum(1 for x in examples if x["exists"])
            summary["status"] = "metadata_loaded"
            report["tasks"][task] = summary
        except Exception as exc:
            report["tasks"][task] = {
                "status": "metadata_read_error",
                "error": f"{type(exc).__name__}: {exc}",
            }

    uid = frames.get("HumanIdentification")
    for task in ("HumanActivityRecognition", "ProximityRecognition"):
        other = frames.get(task)
        name = f"HumanIdentification_vs_{task}"
        if uid is None or other is None:
            report["cross_task_alignment"][name] = {"status": "not_assessed"}
            continue
        key = choose_join_key(uid, other)
        if key is None:
            report["cross_task_alignment"][name] = {
                "status": "no_common_candidate_key",
                "uid_columns": list(map(str, uid.columns)),
                "other_columns": list(map(str, other.columns)),
            }
            continue
        left = set(uid[key].dropna().astype(str))
        right = set(other[key].dropna().astype(str))
        report["cross_task_alignment"][name] = {
            "status": "key_overlap_measured",
            "join_key": key,
            "uid_unique_keys": len(left),
            "other_unique_keys": len(right),
            "common_keys": len(left & right),
            "uid_coverage": len(left & right) / max(1, len(left)),
            "other_coverage": len(left & right) / max(1, len(right)),
            "warning": (
                "A common key is necessary but not sufficient: inspect duplicate keys, "
                "one-to-many mappings and record-level label consistency before joining."
            ),
        }

    report["admission_decision"] = (
        "NOT_ADMITTED: review this report, confirm dataset terms, verify label alignment, "
        "and establish valid session/time splits before creating experiment CSVs."
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Root of the extracted CSI-Bench dataset")
    parser.add_argument("--sample-files", type=int, default=5, help="Number of file references to inspect per task")
    parser.add_argument("--output", default="outputs/csi_bench_qualification.json")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.exists():
        raise FileNotFoundError(root)
    report = qualify(root, sample_files=args.sample_files)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nSaved qualification report: {output}")


if __name__ == "__main__":
    main()

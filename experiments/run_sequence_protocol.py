"""Run session-disjoint, chronological repeated-release privacy experiments.

Input CSV requires identity, activity, session, timestamp (recommended), and
numeric feature columns. This script evaluates known-identity re-identification
across held-out sessions; it is not an unseen-identity open-set protocol.
"""
from pathlib import Path
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import load_feature_csv
from src.metrics import macro_auc
from src.privacy import sanitize
from src.risk_gate import GateThresholds, release_decision
from src.sequences import build_sequences, split_sessions_by_identity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Feature CSV with identity/activity/session/timestamp")
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--sanitizer", default="none", choices=["none", "noise", "quantize", "clip"])
    parser.add_argument("--strength", type=float, default=0.25)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--test-fraction", type=float, default=0.25)
    parser.add_argument("--min-task-purity", type=float, default=0.8)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    seed = args.seed if args.seed is not None else int(cfg["seed"])

    frame = pd.read_csv(args.csv).reset_index(drop=True)
    required = {"identity", "activity", "session"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    excluded = {"identity", "activity", "session", "timestamp", "environment", "device", "radio"}
    feature_cols = [
        col for col in frame.columns
        if col not in excluded and pd.api.types.is_numeric_dtype(frame[col])
    ]
    if not feature_cols:
        raise ValueError("No numeric feature columns found")

    train_idx, test_idx = split_sessions_by_identity(
        frame, test_fraction=args.test_fraction, seed=seed
    )
    train_frame = frame.iloc[train_idx].copy()
    test_frame = frame.iloc[test_idx].copy()
    train_sessions = set(map(str, train_frame["identity"].astype(str) + "::" + train_frame["session"].astype(str)))
    test_sessions = set(map(str, test_frame["identity"].astype(str) + "::" + test_frame["session"].astype(str)))
    if train_sessions & test_sessions:
        raise RuntimeError("Session leakage detected between train and test partitions")

    thresholds = GateThresholds(
        allow_auc_max=float(cfg["privacy"]["allow_auc_max"]),
        block_auc_min=float(cfg["privacy"]["block_auc_min"]),
        min_utility_f1=float(cfg["utility"]["min_macro_f1"]),
    )
    rows = []
    for k in cfg["release_counts"]:
        X_train, y_task_train, y_id_train, _ = build_sequences(
            train_frame, feature_cols, int(k), min_task_purity=args.min_task_purity
        )
        X_test, y_task_test, y_id_test, _ = build_sequences(
            test_frame, feature_cols, int(k), min_task_purity=args.min_task_purity
        )
        if len(X_train) < 20 or len(X_test) < 10:
            rows.append({"release_count": int(k), "status": "insufficient_sequences"})
            continue
        if set(np.unique(y_id_train)) != set(np.unique(y_id_test)):
            raise RuntimeError("Closed-set identity labels differ between train and test")

        Xtr = sanitize(X_train, args.sanitizer, args.strength, seed)
        Xte = sanitize(X_test, args.sanitizer, args.strength, seed + 1)

        utility = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=3000, random_state=seed),
        )
        utility.fit(Xtr, y_task_train)
        utility_pred = utility.predict(Xte)
        utility_f1 = f1_score(
            y_task_test, utility_pred, labels=utility.classes_,
            average="macro", zero_division=0
        )

        attacker = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=3000, random_state=seed),
        )
        t0 = time.perf_counter()
        attacker.fit(Xtr, y_id_train)
        probabilities = attacker.predict_proba(Xte)
        attack_ms = (time.perf_counter() - t0) * 1000
        attack_pred = attacker.predict(Xte)
        attack_f1 = f1_score(
            y_id_test, attack_pred, labels=attacker.classes_,
            average="macro", zero_division=0
        )
        try:
            attack_auc = macro_auc(y_id_test, probabilities, attacker.classes_)
        except ValueError:
            attack_auc = float("nan")

        rows.append({
            "release_count": int(k),
            "status": "ok",
            "sanitizer": args.sanitizer,
            "strength": args.strength,
            "utility_macro_f1": float(utility_f1),
            "identity_attack_macro_f1": float(attack_f1),
            "identity_attack_macro_auc": float(attack_auc),
            "decision": release_decision(float(attack_auc), float(utility_f1), thresholds)
                if np.isfinite(attack_auc) else "UNASSESSED",
            "attack_fit_eval_ms": float(attack_ms),
            "n_train_sequences": int(len(X_train)),
            "n_test_sequences": int(len(X_test)),
        })

    output = Path("outputs")
    output.mkdir(exist_ok=True)
    stem = f"sequence_protocol_{args.sanitizer}"
    result_frame = pd.DataFrame(rows)
    result_frame.to_csv(output / f"{stem}.csv", index=False)
    metadata = {
        "protocol": "session-disjoint chronological sequence evaluation",
        "source": str(args.csv),
        "seed": seed,
        "feature_columns": feature_cols,
        "release_counts": list(map(int, cfg["release_counts"])),
        "sanitizer": args.sanitizer,
        "strength": args.strength,
        "test_fraction": args.test_fraction,
        "min_task_purity": args.min_task_purity,
        "train_rows": int(len(train_frame)),
        "test_rows": int(len(test_frame)),
        "train_session_groups": len(train_sessions),
        "test_session_groups": len(test_sessions),
        "note": "Empirical attacker metrics are not a formal DP budget or information-theoretic leakage guarantee.",
    }
    (output / f"{stem}.metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(result_frame.to_string(index=False))
    print("metadata:", output / f"{stem}.metadata.json")


if __name__ == "__main__":
    main()

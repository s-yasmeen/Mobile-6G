"""Controlled ESP-Fi HAR pilot for Phase 2.

Expected filenames: scenario-participant-activity-trial.csv.
Raw data are not committed. This script intentionally excludes packet metadata
and filename-derived labels from X; filenames are used only to select/label
recordings.
"""
from __future__ import annotations
import ast, itertools, re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NAME = re.compile(r"(\d+)-(\d+)-(\d+)-(\d+)\.csv$")

def parse_name(path: Path):
    m = NAME.match(path.name)
    if not m:
        raise ValueError(f"Unexpected ESP-Fi filename: {path.name}")
    return tuple(map(int, m.groups()))

def csi_features(path: Path) -> np.ndarray:
    df = pd.read_csv(path, usecols=["data"])
    rows = []
    for value in df["data"].dropna():
        raw = np.asarray(ast.literal_eval(value), dtype=float)
        if raw.size % 2:
            raw = raw[:-1]
        z = raw[0::2] + 1j * raw[1::2]
        rows.append(np.abs(z))
    if not rows:
        raise ValueError(f"No CSI rows in {path}")
    n = min(map(len, rows))
    amp = np.vstack([r[:n] for r in rows])
    delta = np.diff(amp, axis=0)
    return np.r_[
        amp.mean(0), amp.std(0),
        np.quantile(amp, .25, axis=0),
        np.quantile(amp, .50, axis=0),
        np.quantile(amp, .75, axis=0),
        np.mean(np.abs(delta), axis=0),
        np.std(delta, axis=0),
    ]

def models(seed: int):
    return {
        "logistic": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=5000, random_state=seed),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=500, class_weight="balanced",
            random_state=seed, n_jobs=-1,
        ),
    }

def load_records(root: Path):
    out = []
    for path in sorted(root.glob("*.csv")):
        try:
            scenario, participant, activity, trial = parse_name(path)
        except ValueError:
            continue
        out.append({
            "path": path, "scenario": scenario, "participant": participant,
            "activity": activity, "trial": trial, "x": csi_features(path),
        })
    return out

def oof_trial_metrics(records, label: str, model_name: str):
    classes = sorted({r[label] for r in records})
    y_all, p_all, pred_all = [], [], []
    trials = sorted({r["trial"] for r in records})
    for trial in trials:
        train = [r for r in records if r["trial"] != trial]
        test = [r for r in records if r["trial"] == trial]
        model = models(100 + trial)[model_name]
        model.fit(np.vstack([r["x"] for r in train]), [r[label] for r in train])
        prob = model.predict_proba(np.vstack([r["x"] for r in test]))
        order = [list(model.classes_).index(c) for c in classes]
        y_all.extend(r[label] for r in test)
        p_all.extend(prob[:, order])
        pred_all.extend(model.predict(np.vstack([r["x"] for r in test])))
    y, prob, pred = np.asarray(y_all), np.asarray(p_all), np.asarray(pred_all)
    return {
        "macro_ovr_auc": roc_auc_score(y, prob, labels=classes, multi_class="ovr", average="macro"),
        "macro_f1": f1_score(y, pred, average="macro"),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
    }

def main(root: str):
    records = load_records(Path(root))
    privacy = [r for r in records if r["scenario"] == 1 and r["activity"] == 7
               and r["participant"] in {1, 2, 8} and 1 <= r["trial"] <= 10]
    utility = [r for r in records if r["scenario"] == 1 and r["participant"] == 1
               and r["activity"] in {1, 5, 7} and 1 <= r["trial"] <= 10]
    if len(privacy) != 30 or len(utility) != 30:
        raise RuntimeError("Pilot requires balanced 3-class x 10-trial subsets.")
    for task, subset, label in [
        ("privacy", privacy, "participant"), ("utility", utility, "activity")
    ]:
        for model_name in models(1):
            print(task, model_name, oof_trial_metrics(subset, label, model_name))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    main(ap.parse_args().data_dir)

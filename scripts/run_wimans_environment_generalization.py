"""WiMANS held-out-environment generalization benchmark.

Trains on two physical environments and evaluates on the unseen third.
Reports activity-recognition utility and participant-associated identity
inference using LR, RF, and MLP. WiMANS is used as Wi-Fi CSI evidence
relevant to next-generation wireless sensing; this script does not claim
native 6G measurements or invariant biometric identity.
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, f1_score, balanced_accuracy_score

OUT = Path("/kaggle/working/wimans_phase2")
X = np.load(OUT / "wimans_single_user_features.npz")["X"].astype(np.float32)
meta = pd.read_csv(OUT / "wimans_single_user_metadata.csv")

assert len(X) == len(meta)
assert np.isfinite(X).all()
X = X[:, np.std(X, axis=0) > 0]

act_enc, id_enc = LabelEncoder(), LabelEncoder()
y_activity = act_enc.fit_transform(meta["activity"].astype(str)).astype(np.int64)
y_identity = id_enc.fit_transform(meta["identity"].astype(str)).astype(np.int64)
env = meta["environment"].astype(str).values
environments = sorted(np.unique(env))

print("Environments:", environments)
print(pd.crosstab(meta["identity"], meta["environment"]))
print(pd.crosstab(meta["activity"], meta["environment"]))

for e in environments:
    idx = np.where(env == e)[0]
    assert len(np.unique(y_identity[idx])) == len(np.unique(y_identity))
    assert len(np.unique(y_activity[idx])) == len(np.unique(y_activity))


def make_models(seed=11):
    return {
        "LR": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)),
        ]),
        "RF": RandomForestClassifier(
            n_estimators=300, class_weight="balanced_subsample",
            random_state=seed, n_jobs=-1
        ),
        "MLP": Pipeline([
            ("scale", StandardScaler()),
            ("model", MLPClassifier(
                hidden_layer_sizes=(128, 64), max_iter=400, batch_size=64,
                learning_rate_init=0.001, early_stopping=True,
                validation_fraction=0.15, random_state=seed
            )),
        ]),
    }


def macro_ovr_auc(model, x_test, y_test):
    prob = model.predict_proba(x_test)
    scores = []
    for j, cls in enumerate(np.asarray(model.classes_)):
        binary = (y_test == cls).astype(int)
        if len(np.unique(binary)) == 2:
            scores.append(roc_auc_score(binary, prob[:, j]))
    return float(np.mean(scores)) if scores else np.nan


results = []
tasks = {"UTILITY_ACTIVITY": y_activity, "PRIVACY_IDENTITY": y_identity}

for held_out in environments:
    train_idx = np.where(env != held_out)[0]
    test_idx = np.where(env == held_out)[0]
    assert len(np.intersect1d(train_idx, test_idx)) == 0

    print(f"\nHELD-OUT: {held_out} | train={len(train_idx)} test={len(test_idx)}")
    for task_name, y in tasks.items():
        for model_name, model in make_models().items():
            start = time.time()
            model.fit(X[train_idx], y[train_idx])
            pred = model.predict(X[test_idx])
            auc = macro_ovr_auc(model, X[test_idx], y[test_idx])
            f1 = f1_score(y[test_idx], pred, average="macro", zero_division=0)
            bal = balanced_accuracy_score(y[test_idx], pred)
            runtime = time.time() - start
            print(f"{task_name} {model_name}: AUC={auc:.4f} F1={f1:.4f} BalAcc={bal:.4f}")
            results.append({
                "heldout_environment": held_out, "task": task_name, "model": model_name,
                "n_train": len(train_idx), "n_test": len(test_idx),
                "macro_ovr_auc": auc, "macro_f1": f1,
                "balanced_accuracy": bal, "runtime_seconds": runtime,
            })

results_df = pd.DataFrame(results)
results_df.to_csv(OUT / "wimans_heldout_environment_results.csv", index=False)

summary = results_df.groupby(["task", "model"]).agg(
    N_environment=("heldout_environment", "count"),
    AUC_mean=("macro_ovr_auc", "mean"), AUC_std=("macro_ovr_auc", "std"),
    F1_mean=("macro_f1", "mean"), F1_std=("macro_f1", "std"),
    BalAcc_mean=("balanced_accuracy", "mean"), BalAcc_std=("balanced_accuracy", "std"),
).reset_index()
summary.to_csv(OUT / "wimans_heldout_environment_summary.csv", index=False)

print("\nMEAN ACROSS HELD-OUT ENVIRONMENTS")
print(summary.round(4).to_string(index=False))

baseline_file = OUT / "wimans_5seed_summary_corrected.csv"
if baseline_file.exists():
    baseline = pd.read_csv(baseline_file)
    comparison = baseline[["task","model","AUC_mean","F1_mean","BalAcc_mean"]].merge(
        summary[["task","model","AUC_mean","F1_mean","BalAcc_mean"]],
        on=["task","model"], suffixes=("_random","_heldout_env")
    )
    comparison["AUC_drop"] = comparison["AUC_mean_random"] - comparison["AUC_mean_heldout_env"]
    comparison["F1_drop"] = comparison["F1_mean_random"] - comparison["F1_mean_heldout_env"]
    comparison["BalAcc_drop"] = comparison["BalAcc_mean_random"] - comparison["BalAcc_mean_heldout_env"]
    comparison.to_csv(OUT / "wimans_random_vs_environment_comparison.csv", index=False)
    print("\nRANDOM SPLIT vs HELD-OUT ENVIRONMENT")
    print(comparison.round(4).to_string(index=False))

print("\nIdentity chance balanced accuracy:", round(1 / len(np.unique(y_identity)), 4))
print("Activity chance balanced accuracy:", round(1 / len(np.unique(y_activity)), 4))

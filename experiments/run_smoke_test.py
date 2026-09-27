from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.pipeline import make_pipeline

from src.synthetic import make_synthetic_rf
from src.risk_gate import GateThresholds, release_decision

SEED = 42
X, y_task, y_id = make_synthetic_rf(seed=SEED)
idx = np.arange(len(X))
tr, te = train_test_split(idx, test_size=0.3, random_state=SEED, stratify=y_task)

utility = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1500))
utility.fit(X[tr], y_task[tr])
utility_f1 = f1_score(y_task[te], utility.predict(X[te]), average="macro")

attacker = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1500))
attacker.fit(X[tr], y_id[tr])
proba = attacker.predict_proba(X[te])
classes = attacker.classes_
y_bin = label_binarize(y_id[te], classes=classes)
auc = roc_auc_score(y_bin, proba, average="macro", multi_class="ovr")

t = GateThresholds()
decision = release_decision(auc, utility_f1, t)
result = pd.DataFrame([{"release_count": 1, "utility_macro_f1": utility_f1,
                        "identity_macro_auc": auc, "decision": decision}])
Path("outputs").mkdir(exist_ok=True)
result.to_csv("outputs/smoke_test.csv", index=False)
print(result.to_string(index=False))

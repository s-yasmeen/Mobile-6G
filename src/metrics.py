import numpy as np
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize


def macro_auc(y, proba, classes):
    yb=label_binarize(y,classes=classes)
    if len(classes)==2: return roc_auc_score(yb,proba[:,1])
    return roc_auc_score(yb,proba,average="macro",multi_class="ovr")


def bootstrap_ci(y_true,y_pred,metric="f1",n=500,seed=42):
    rng=np.random.default_rng(seed); vals=[]; nobs=len(y_true)
    for _ in range(n):
        ix=rng.integers(0,nobs,nobs)
        if metric=="f1": vals.append(f1_score(np.asarray(y_true)[ix],np.asarray(y_pred)[ix],average="macro"))
    return tuple(np.quantile(vals,[.025,.975]))

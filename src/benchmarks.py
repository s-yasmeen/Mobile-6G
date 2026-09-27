import time
import numpy as np
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score


def build_model(name, seed=42):
    if name=="logistic_regression": return make_pipeline(StandardScaler(),LogisticRegression(max_iter=2500,random_state=seed))
    if name=="random_forest": return RandomForestClassifier(n_estimators=300,class_weight="balanced",random_state=seed,n_jobs=-1)
    if name=="mlp": return make_pipeline(StandardScaler(),MLPClassifier(hidden_layer_sizes=(128,64),max_iter=500,early_stopping=True,random_state=seed))
    raise ValueError(name)


def _macro_auc(y,prob,classes):
    y=np.asarray(y); present=np.unique(y)
    if len(present)<2: return float("nan")
    cols=[int(np.where(np.asarray(classes)==c)[0][0]) for c in present if c in classes]
    pp=prob[:,cols]; pp=pp/pp.sum(axis=1,keepdims=True)
    return float(roc_auc_score(y,pp,labels=present,multi_class="ovr",average="macro"))


def evaluate_classifier(model,Xtr,ytr,Xte,yte,privacy=False,return_predictions=False):
    t=time.perf_counter(); model.fit(Xtr,ytr); pred=model.predict(Xte); prob=model.predict_proba(Xte) if privacy and hasattr(model,"predict_proba") else None; elapsed=(time.perf_counter()-t)*1000
    out={"macro_f1":float(f1_score(yte,pred,average="macro")),"balanced_accuracy":float(balanced_accuracy_score(yte,pred)),"fit_eval_ms":elapsed}
    if prob is not None: out["macro_ovr_auc"]=_macro_auc(yte,prob,model.classes_)
    if return_predictions: return out,pred,prob,getattr(model,"classes_",None)
    return out


def bootstrap_metrics(y,pred,prob=None,classes=None,n=1000,confidence=.95,seed=42):
    rng=np.random.default_rng(seed); y=np.asarray(y); pred=np.asarray(pred); stats={"macro_f1":[],"balanced_accuracy":[],"macro_ovr_auc":[]}
    for _ in range(n):
        ix=rng.integers(0,len(y),len(y)); yy=y[ix]; pp=pred[ix]
        stats["macro_f1"].append(f1_score(yy,pp,average="macro")); stats["balanced_accuracy"].append(balanced_accuracy_score(yy,pp))
        if prob is not None and len(np.unique(yy))>1:
            try: stats["macro_ovr_auc"].append(_macro_auc(yy,prob[ix],classes))
            except ValueError: pass
    alpha=(1-confidence)/2; out={}
    for k,v in stats.items():
        if v: out[k+"_ci_low"]=float(np.quantile(v,alpha)); out[k+"_ci_high"]=float(np.quantile(v,1-alpha))
    return out


def permutation_baseline(model_factory,Xtr,ytr,Xte,yte,n=200,seed=42,privacy=False):
    rng=np.random.default_rng(seed); vals=[]
    for i in range(n):
        yp=rng.permutation(ytr); r=evaluate_classifier(model_factory(seed+i),Xtr,yp,Xte,yte,privacy=privacy); vals.append(r)
    out={}
    for metric in ["macro_f1","balanced_accuracy","macro_ovr_auc"]:
        a=np.array([r[metric] for r in vals if metric in r and np.isfinite(r[metric])])
        if len(a): out[f"permutation_{metric}_mean"]=float(a.mean()); out[f"permutation_{metric}_p95"]=float(np.quantile(a,.95))
    return out


def group_bootstrap_metrics(y,pred,groups,prob=None,classes=None,n=1000,confidence=.95,seed=42):
    """Cluster bootstrap: resample whole sessions/experiments, not correlated windows."""
    rng=np.random.default_rng(seed); y=np.asarray(y); pred=np.asarray(pred); groups=np.asarray(groups); unique=np.unique(groups)
    stats={"macro_f1":[],"balanced_accuracy":[],"macro_ovr_auc":[]}
    for _ in range(n):
        sampled=rng.choice(unique,size=len(unique),replace=True); ix=np.concatenate([np.flatnonzero(groups==g) for g in sampled]); yy=y[ix]; pp=pred[ix]
        stats["macro_f1"].append(f1_score(yy,pp,average="macro")); stats["balanced_accuracy"].append(balanced_accuracy_score(yy,pp))
        if prob is not None and len(np.unique(yy))>1:
            try: stats["macro_ovr_auc"].append(_macro_auc(yy,prob[ix],classes))
            except ValueError: pass
    alpha=(1-confidence)/2; out={}
    for k,v in stats.items():
        if v: out[k+"_ci_low"]=float(np.quantile(v,alpha)); out[k+"_ci_high"]=float(np.quantile(v,1-alpha))
    return out

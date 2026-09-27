import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, balanced_accuracy_score
from src.metrics import macro_auc


def build_model(name, seed=42):
    if name=="logistic_regression": return make_pipeline(StandardScaler(),LogisticRegression(max_iter=2500,random_state=seed))
    if name=="random_forest": return RandomForestClassifier(n_estimators=300,class_weight="balanced",random_state=seed,n_jobs=-1)
    if name=="mlp": return make_pipeline(StandardScaler(),MLPClassifier(hidden_layer_sizes=(128,64),max_iter=500,early_stopping=True,random_state=seed))
    raise ValueError(name)


def evaluate_classifier(model,Xtr,ytr,Xte,yte,privacy=False):
    t=time.perf_counter(); model.fit(Xtr,ytr); pred=model.predict(Xte); elapsed=(time.perf_counter()-t)*1000
    out={"macro_f1":f1_score(yte,pred,average="macro"),"balanced_accuracy":balanced_accuracy_score(yte,pred),"fit_eval_ms":elapsed}
    if privacy and hasattr(model,"predict_proba"): out["macro_ovr_auc"]=macro_auc(yte,model.predict_proba(Xte),model.classes_)
    return out


def permutation_baseline(model_factory,Xtr,ytr,Xte,yte,n=200,seed=42,privacy=False):
    rng=np.random.default_rng(seed); vals=[]
    for i in range(n):
        yp=rng.permutation(ytr); m=model_factory(seed+i); r=evaluate_classifier(m,Xtr,yp,Xte,yte,privacy=privacy); vals.append(r["macro_f1"])
    return {"permutation_macro_f1_mean":float(np.mean(vals)),"permutation_macro_f1_p95":float(np.quantile(vals,.95))}

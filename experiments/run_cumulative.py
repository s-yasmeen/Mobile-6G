from pathlib import Path
import argparse,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from src.synthetic import make_synthetic_rf
from src.data import load_feature_csv
from src.privacy import sanitize,aggregate_releases
from src.metrics import macro_auc
from src.risk_gate import GateThresholds,release_decision

p=argparse.ArgumentParser(); p.add_argument("--csv"); p.add_argument("--sanitizer",default="none",choices=["none","noise","quantize","clip"]); p.add_argument("--strength",type=float,default=.25); p.add_argument("--seed",type=int,default=42); a=p.parse_args()
if a.csv: X,yt,yi=load_feature_csv(a.csv)
else: X,yt,yi=make_synthetic_rf(n_samples=6000,seed=a.seed)
idx=np.arange(len(X)); tr,te=train_test_split(idx,test_size=.35,random_state=a.seed,stratify=yt)
Xs=sanitize(X,a.sanitizer,a.strength,a.seed)
utility=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)); utility.fit(Xs[tr],yt[tr]); uf1=f1_score(yt[te],utility.predict(Xs[te]),average="macro")
rows=[]
for k in [1,2,5,10,20]:
    Xtr,ytr=aggregate_releases(Xs[tr],yi[tr],k); Xte,yte=aggregate_releases(Xs[te],yi[te],k)
    if len(np.unique(ytr))<2 or len(yte)<10: continue
    t0=time.perf_counter(); atk=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)); atk.fit(Xtr,ytr); prob=atk.predict_proba(Xte); auc=macro_auc(yte,prob,atk.classes_); ms=(time.perf_counter()-t0)*1000
    rows.append({"release_count":k,"sanitizer":a.sanitizer,"strength":a.strength,"utility_macro_f1":uf1,"identity_macro_auc":auc,"decision":release_decision(auc,uf1,GateThresholds()),"attack_fit_eval_ms":ms})
out=Path("outputs"); out.mkdir(exist_ok=True); df=pd.DataFrame(rows); df.to_csv(out/f"cumulative_{a.sanitizer}.csv",index=False); print(df.to_string(index=False))

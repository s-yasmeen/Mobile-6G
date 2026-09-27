from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd,yaml
from src.data import load_feature_csv
from src.quality import audit_arrays
from src.splits import known_identity_session_split,stratified_split
from src.benchmarks import build_model,evaluate_classifier,permutation_baseline

p=argparse.ArgumentParser(); p.add_argument("--csv",required=True); p.add_argument("--group-col",default="session"); p.add_argument("--config",default="configs/phase2.yaml"); a=p.parse_args()
cfg=yaml.safe_load(open(a.config,encoding="utf-8")); raw=pd.read_csv(a.csv)
X,yt,yi=load_feature_csv(a.csv); groups=raw[a.group_col].to_numpy() if a.group_col in raw else None
out=Path("outputs/phase2"); out.mkdir(parents=True,exist_ok=True); (out/"data_quality.json").write_text(json.dumps(audit_arrays(X,yt,yi,groups),indent=2),encoding="utf-8")
rows=[]
for seed in cfg["seeds"]:
 utr,ute=stratified_split(yt,cfg["split"]["test_size"],seed)
 if groups is not None: ptr,pte=known_identity_session_split(yi,groups,cfg["split"]["test_size"],seed)
 else: ptr,pte=stratified_split(yi,cfg["split"]["test_size"],seed)
 for name in cfg["benchmarks"]["attackers"]:
  ur=evaluate_classifier(build_model(name,seed),X[utr],yt[utr],X[ute],yt[ute]); rows.append({"seed":seed,"role":"utility","model":name,**ur})
  pr=evaluate_classifier(build_model(name,seed),X[ptr],yi[ptr],X[pte],yi[pte],privacy=True); rows.append({"seed":seed,"role":"privacy","model":name,**pr})
pd.DataFrame(rows).to_csv(out/"baseline_results.csv",index=False); print(pd.DataFrame(rows).groupby(["role","model"]).mean(numeric_only=True).to_string())

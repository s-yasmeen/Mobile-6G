from pathlib import Path
import argparse,json,sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd,yaml
from src.data import load_feature_csv
from src.quality import audit_arrays
from src.splits import known_identity_session_split,stratified_split,group_split
from src.benchmarks import build_model,evaluate_classifier,permutation_baseline,bootstrap_metrics,group_bootstrap_metrics

p=argparse.ArgumentParser(); p.add_argument("--csv",required=True); p.add_argument("--group-col",default="session"); p.add_argument("--config",default="configs/phase2.yaml"); p.add_argument("--permutations",type=int); a=p.parse_args()
cfg=yaml.safe_load(open(a.config,encoding="utf-8")); raw=pd.read_csv(a.csv); X,yt,yi=load_feature_csv(a.csv); groups=raw[a.group_col].to_numpy() if a.group_col in raw else None
out=Path("outputs/phase2"); out.mkdir(parents=True,exist_ok=True); (out/"data_quality.json").write_text(json.dumps(audit_arrays(X,yt,yi,groups),indent=2),encoding="utf-8")
rows=[]; perms=[]; manifests=[]
for seed in cfg["seeds"]:
 utr,ute=(group_split(groups,cfg["split"]["test_size"],seed) if groups is not None else stratified_split(yt,cfg["split"]["test_size"],seed)); ptr,pte=(known_identity_session_split(yi,groups,cfg["split"]["test_size"],seed) if groups is not None else stratified_split(yi,cfg["split"]["test_size"],seed))
 manifests += [{"seed":seed,"role":"utility","train_indices":utr.tolist(),"test_indices":ute.tolist()},{"seed":seed,"role":"privacy","train_indices":ptr.tolist(),"test_indices":pte.tolist()}]
 for name in cfg["benchmarks"]["attackers"]:
  ur,up,_,_=evaluate_classifier(build_model(name,seed),X[utr],yt[utr],X[ute],yt[ute],return_predictions=True); ur.update(group_bootstrap_metrics(yt[ute],up,groups[ute],n=int(cfg["benchmarks"]["bootstrap_iterations"]),confidence=float(cfg["benchmarks"]["confidence_level"]),seed=seed) if groups is not None else bootstrap_metrics(yt[ute],up,n=int(cfg["benchmarks"]["bootstrap_iterations"]),confidence=float(cfg["benchmarks"]["confidence_level"]),seed=seed)); rows.append({"seed":seed,"role":"utility","model":name,**ur})
  pr,pp,prob,classes=evaluate_classifier(build_model(name,seed),X[ptr],yi[ptr],X[pte],yi[pte],privacy=True,return_predictions=True); pr.update(group_bootstrap_metrics(yi[pte],pp,groups[pte],prob,classes,n=int(cfg["benchmarks"]["bootstrap_iterations"]),confidence=float(cfg["benchmarks"]["confidence_level"]),seed=seed) if groups is not None else bootstrap_metrics(yi[pte],pp,prob,classes,n=int(cfg["benchmarks"]["bootstrap_iterations"]),confidence=float(cfg["benchmarks"]["confidence_level"]),seed=seed)); rows.append({"seed":seed,"role":"privacy","model":name,**pr})
  n=a.permutations if a.permutations is not None else int(cfg["benchmarks"]["chance_permutations"])
  if n>0: perms.append({"seed":seed,"role":"privacy","model":name,"n_permutations":n,**permutation_baseline(lambda s:build_model(name,s),X[ptr],yi[ptr],X[pte],yi[pte],n=n,seed=seed,privacy=True)})
df=pd.DataFrame(rows); df.to_csv(out/"baseline_results.csv",index=False); pd.DataFrame(perms).to_csv(out/"permutation_baselines.csv",index=False); (out/"split_manifest.json").write_text(json.dumps(manifests),encoding="utf-8")
summary=df.groupby(["role","model"]).agg(["mean","std"]).round(5); summary.to_csv(out/"baseline_summary.csv")
try: commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
except Exception: commit="unknown"
meta={"input":a.csv,"config":a.config,"group_column":a.group_col,"commit":commit,"seeds":cfg["seeds"],"models":cfg["benchmarks"]["attackers"]}; (out/"run_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8"); print(summary.to_string())

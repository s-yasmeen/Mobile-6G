"""Prepare leakage-safe window features from official OPERAnet UWB1 CSV files.
Labels: activity (utility), person_id (privacy); exp_no is grouping metadata only.
Ground-truth coordinates, room, experiment IDs and timestamps are NEVER model features.
"""
from pathlib import Path
import argparse,json,re
import numpy as np,pandas as pd
p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",default="data/processed/operanet_uwb1.csv"); p.add_argument("--window-ms",type=int,default=1000); p.add_argument("--stride-ms",type=int,default=500); a=p.parse_args()
files=sorted(Path(a.input).glob("*.csv"));
if not files: raise SystemExit("No CSV files found")
rows=[]; audit={"files":len(files),"packets":0,"windows":0,"skipped_windows":0}
for f in files:
 d=pd.read_csv(f); req={"timestamp","activity","exp_no","person_id","room_no"}; miss=req-set(d.columns)
 if miss: raise SystemExit(f"{f.name}: missing {sorted(miss)}")
 d=d.dropna(subset=["timestamp","activity","exp_no","person_id"]).copy(); d["timestamp"]=pd.to_numeric(d.timestamp,errors="coerce"); d=d.dropna(subset=["timestamp"]); audit["packets"]+=len(d)
 # Strict RF feature whitelist. Metadata/ground truth cannot enter X.
 cir=[c for c in d.columns if re.fullmatch(r"(?i)(cir|cfr)[_ -]?\\d+",str(c))]
 power=[c for c in ["fp_pow_dbm","rx_pow_dbm"] if c in d.columns]
 rf=cir+power
 if not rf: raise SystemExit(f"{f.name}: no CIR/CFR or RF-power columns detected; inspect schema before proceeding")
 for c in rf:
  if d[c].dtype==object:
   d[c]=d[c].map(lambda v: abs(complex(str(v).replace("i","j"))) if pd.notna(v) else np.nan)
  else: d[c]=pd.to_numeric(d[c],errors="coerce")
 for (exp,person,activity),g in d.groupby(["exp_no","person_id","activity"],dropna=False):
  g=g.sort_values("timestamp"); lo=float(g.timestamp.min()); hi=float(g.timestamp.max()); start=lo
  while start+a.window_ms<=hi:
   w=g[(g.timestamp>=start)&(g.timestamp<start+a.window_ms)]
   if len(w)<2: audit["skipped_windows"]+=1; start+=a.stride_ms; continue
   vals=w[rf].to_numpy(float); feat={"activity":activity,"identity":person,"session":exp,"room_no":str(w.room_no.iloc[0]),"window_start":start,"packet_count":len(w)}
   for j,c in enumerate(rf):
    v=vals[:,j]; feat[f"{c}_mean"]=np.nanmean(v); feat[f"{c}_std"]=np.nanstd(v); feat[f"{c}_median"]=np.nanmedian(v)
   rows.append(feat); audit["windows"]+=1; start+=a.stride_ms
out=pd.DataFrame(rows); Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False); audit.update({"output":a.output,"identities":int(out.identity.nunique()) if len(out) else 0,"activities":int(out.activity.nunique()) if len(out) else 0,"sessions":int(out.session.nunique()) if len(out) else 0}); print(json.dumps(audit))

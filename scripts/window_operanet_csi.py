"""Window packet-level OPERAnet CSI magnitudes without crossing experiment/activity/person boundaries."""
from pathlib import Path
import argparse
import numpy as np,pandas as pd
p=argparse.ArgumentParser(); p.add_argument("--input",default="data/processed/operanet_packets.csv"); p.add_argument("--output",default="data/processed/operanet_features.csv"); p.add_argument("--window-ms",type=int,default=1000); p.add_argument("--stride-ms",type=int,default=500); a=p.parse_args()
df=pd.read_csv(a.input); feats=[c for c in df if c.startswith("abs_tx")]
rows=[]
for (session,identity,activity,room),g in df.groupby(["session","identity","activity","room_no"],sort=False):
 g=g.sort_values("timestamp"); t=g.timestamp.to_numpy(dtype=float); start=t.min(); end=t.max()
 while start+a.window_ms<=end:
  w=g[(g.timestamp>=start)&(g.timestamp<start+a.window_ms)]
  if len(w)>=10:
   vals=w[feats].to_numpy(float); row={"activity":activity,"identity":identity,"session":session,"room_no":room,"window_start":start,"packet_count":len(w)}
   for j,c in enumerate(feats): row[f"{c}_mean"]=float(np.mean(vals[:,j])); row[f"{c}_std"]=float(np.std(vals[:,j])); row[f"{c}_median"]=float(np.median(vals[:,j]))
   rows.append(row)
  start+=a.stride_ms
out=pd.DataFrame(rows); Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False); print(a.output,len(out),"windows")

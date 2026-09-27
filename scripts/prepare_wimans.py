"""Prepare WiMANS single-user CSI for the Phase-2 K=1 joint utility/privacy benchmark.
Identity follows the official WiMANS definition: which anonymized user slot (1..6) is present.
Activity is that occupied user's activity. Multi-user samples are intentionally excluded here.
"""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
p=argparse.ArgumentParser(); p.add_argument("--root",required=True); p.add_argument("--output",default="data/processed/wimans_single_user.csv"); p.add_argument("--band",default=None); p.add_argument("--environment",default=None); a=p.parse_args()
root=Path(a.root); ann=pd.read_csv(root/"annotation.csv",dtype=str); amp=root/"wifi_csi"/"amp"
required={"label","number_of_users","wifi_band","environment"}|{f"user_{i}_location" for i in range(1,7)}|{f"user_{i}_activity" for i in range(1,7)}
missing=required-set(ann.columns)
if missing: raise SystemExit(f"WiMANS columns missing: {sorted(missing)}")
ann=ann[ann.number_of_users=="1"].copy()
if a.band: ann=ann[ann.wifi_band==a.band]
if a.environment: ann=ann[ann.environment==a.environment]
rows=[]; skipped=0
for _,r in ann.iterrows():
 occupied=[i for i in range(1,7) if pd.notna(r[f"user_{i}_location"]) and str(r[f"user_{i}_location"]).lower()!="nan"]
 if len(occupied)!=1: skipped+=1; continue
 ident=occupied[0]; activity=r[f"user_{ident}_activity"]; f=amp/(str(r.label)+".npy")
 if not f.exists(): skipped+=1; continue
 x=np.asarray(np.load(f)); mag=np.abs(x).astype(float)
 # Per-sample distributional CSI features; no label enters feature extraction.
 flat=mag.reshape(-1); q=np.quantile(flat,[.05,.25,.5,.75,.95])
 row={"activity":activity,"identity":str(ident),"sample_id":r.label,"environment":r.environment,"wifi_band":r.wifi_band,"mean":flat.mean(),"std":flat.std(),"min":flat.min(),"max":flat.max(),"q05":q[0],"q25":q[1],"q50":q[2],"q75":q[3],"q95":q[4]}
 # Preserve antenna/subcarrier structure through axis-wise summary moments.
 for axis in range(1,mag.ndim):
  reduce=tuple(i for i in range(mag.ndim) if i!=axis); m=mag.mean(axis=reduce); s=mag.std(axis=reduce)
  for j,v in enumerate(np.ravel(m)): row[f"axis{axis}_mean_{j}"]=float(v)
  for j,v in enumerate(np.ravel(s)): row[f"axis{axis}_std_{j}"]=float(v)
 rows.append(row)
out=pd.DataFrame(rows); Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False)
print(json.dumps({"rows":len(out),"identities":int(out.identity.nunique()) if len(out) else 0,"activities":int(out.activity.nunique()) if len(out) else 0,"skipped":skipped,"output":a.output}))

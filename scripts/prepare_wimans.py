"""Build a compact Phase-2 feature table from official WiMANS preprocessed CSI amplitudes.
The dataset's annotation.csv is the authoritative label source. No video is used.
"""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
p=argparse.ArgumentParser(); p.add_argument("--root",required=True); p.add_argument("--output",default="data/processed/wimans_features.csv"); a=p.parse_args()
root=Path(a.root); ann=pd.read_csv(root/"annotation.csv",dtype=str); amp=root/"wifi_csi"/"amp"
# WiMANS annotation naming can evolve; preserve source columns and require explicit identity/activity discovery.
def pick(candidates):
 for c in candidates:
  if c in ann.columns:return c
 raise SystemExit(f"None of {candidates} found. Columns: {list(ann.columns)}")
filecol=pick(["sample","sample_id","name","id","file"]); activity=pick(["activity","activities","activity_label"]); identity=pick(["identity","user","user_id","person_id"])
rows=[]
for _,r in ann.iterrows():
 stem=str(r[filecol]); stem=stem[:-4] if stem.endswith(".npy") else stem; f=amp/(stem+".npy")
 if not f.exists(): continue
 x=np.asarray(np.load(f)); mag=np.abs(x).astype(float).reshape(-1)
 # Compact fixed-dimensional distributional representation; no label information enters feature extraction.
 q=np.quantile(mag,[.05,.25,.5,.75,.95]); row={"activity":r[activity],"identity":r[identity],"session":stem,"mean":mag.mean(),"std":mag.std(),"min":mag.min(),"max":mag.max(),"q05":q[0],"q25":q[1],"q50":q[2],"q75":q[3],"q95":q[4]}
 rows.append(row)
out=pd.DataFrame(rows); Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False)
print(json.dumps({"rows":len(out),"identities":int(out.identity.nunique()) if len(out) else 0,"activities":int(out.activity.nunique()) if len(out) else 0,"output":a.output}))

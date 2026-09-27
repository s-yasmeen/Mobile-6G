"""Prepare packet-level OPERAnet Wi-Fi CSI exported as CSV.
Expected official fields follow the OPERAnet Data Descriptor. Complex CSI values
may be serialized by the MAT-to-CSV export and are converted to magnitudes.
Windowing is deliberately a later step and must group by experiment before split.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",default="data/processed/operanet_packets.csv"); a=p.parse_args()
df=pd.read_csv(a.input)
required={"activity","person_id","exp_no","room_no","timestamp"}; missing=required-set(df.columns)
if missing: raise SystemExit(f"Official OPERAnet metadata missing: {sorted(missing)}")
csi=[c for c in df.columns if c.startswith("tx") and "rx" in c and "_sub" in c]
if len(csi)!=270: raise SystemExit(f"Expected 270 Wi-Fi CSI fields; found {len(csi)}. Inspect MAT export before proceeding.")
def magnitude(v):
 try: return abs(complex(str(v).replace("i","j")))
 except Exception: return np.nan
features=pd.DataFrame({f"abs_{c}":df[c].map(magnitude) for c in csi})
labels=df[["activity","person_id","exp_no","room_no","timestamp"]].rename(columns={"person_id":"identity","exp_no":"session"})
out=pd.concat([labels.reset_index(drop=True),features],axis=1).dropna()
Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False)
print(a.output,len(out),"packets",len(csi),"CSI magnitudes")

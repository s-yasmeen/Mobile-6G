"""Prepare an OPERAnet-derived feature table after the user downloads official data.
This intentionally does not scrape or redistribute the dataset.
"""
from pathlib import Path
import argparse
import pandas as pd

p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",default="data/processed/operanet_features.csv"); a=p.parse_args()
df=pd.read_csv(a.input)
required={"activity","person_id","exp_no"}; missing=required-set(df.columns)
if missing: raise SystemExit(f"Required OPERAnet metadata missing: {sorted(missing)}")
# Preserve numeric RF-derived fields only; raw identifiers remain labels/groups.
labels=df[["activity","person_id","exp_no"]].rename(columns={"person_id":"identity","exp_no":"session"})
features=df.drop(columns=[c for c in df.columns if c in {"activity","person_id","exp_no"}]).select_dtypes("number")
out=pd.concat([labels.reset_index(drop=True),features.reset_index(drop=True)],axis=1).dropna()
Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False); print(a.output,len(out),"rows",len(features.columns),"numeric features")

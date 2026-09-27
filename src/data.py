from pathlib import Path
import pandas as pd
import numpy as np


def load_feature_csv(path, task_col="activity", identity_col="identity"):
    """Generic adapter for extracted RF/ISAC feature CSV files."""
    df=pd.read_csv(Path(path))
    missing={task_col,identity_col}-set(df.columns)
    if missing: raise ValueError(f"Missing label columns: {sorted(missing)}")
    feature_cols=[c for c in df.columns if c not in {task_col,identity_col,"timestamp","session"}]
    X=df[feature_cols].select_dtypes(include=[np.number]).to_numpy(float)
    if X.shape[1]==0: raise ValueError("No numeric feature columns found")
    return X,df[task_col].to_numpy(),df[identity_col].to_numpy()

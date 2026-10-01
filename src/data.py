from pathlib import Path
import pandas as pd
import numpy as np

# Columns that may encode labels, grouping, acquisition context, or file identity.
# They are never admitted automatically as model features.
DEFAULT_METADATA = {
    "timestamp","session","sample_id","scenario","participant","trial","environment",
    "wifi_band","room_no","window_start","packet_count","exp_no","person_id",
    "filename","file","path","label","group","recording","recording_id"
}

def load_feature_csv(path, task_col="activity", identity_col="identity", extra_metadata=None):
    """Load an extracted feature table with a fail-closed metadata exclusion policy."""
    df=pd.read_csv(Path(path))
    missing={task_col,identity_col}-set(df.columns)
    if missing: raise ValueError(f"Missing label columns: {sorted(missing)}")
    blocked=DEFAULT_METADATA|{task_col,identity_col}|set(extra_metadata or [])
    feature_cols=[c for c in df.columns if c not in blocked and pd.api.types.is_numeric_dtype(df[c])]
    if not feature_cols: raise ValueError("No numeric feature columns remain after metadata exclusion")
    X=df[feature_cols].to_numpy(float)
    if not np.isfinite(X).all(): raise ValueError("Feature matrix contains NaN/Inf")
    return X,df[task_col].to_numpy(),df[identity_col].to_numpy()

import numpy as np
from collections import Counter


def audit_arrays(X,y_task,y_identity,groups=None):
    X=np.asarray(X); yt=np.asarray(y_task); yi=np.asarray(y_identity)
    if not (len(X)==len(yt)==len(yi)): raise ValueError("Feature/label length mismatch")
    report={"n_samples":int(len(X)),"n_features":int(X.shape[1]),"nan_count":int(np.isnan(X).sum()),"inf_count":int(np.isinf(X).sum()),"task_counts":dict(Counter(map(str,yt))),"identity_counts":dict(Counter(map(str,yi))),"duplicate_rows":int(len(X)-len(np.unique(X,axis=0)))}
    if groups is not None: report["n_groups"]=int(len(np.unique(groups)))
    return report

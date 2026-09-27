import numpy as np


def sanitize(X, method="noise", strength=0.25, seed=42):
    X=np.asarray(X,float); rng=np.random.default_rng(seed)
    if method=="none": return X.copy()
    if method=="noise": return X+rng.normal(0,strength,X.shape)
    if method=="quantize":
        step=max(float(strength),1e-6); return np.round(X/step)*step
    if method=="clip": return np.clip(X,-abs(strength),abs(strength))
    raise ValueError(f"Unknown sanitizer: {method}")


def aggregate_releases(X, identities, k):
    """Average non-overlapping groups of k observations per identity."""
    X=np.asarray(X); identities=np.asarray(identities); xs=[]; ys=[]
    for person in np.unique(identities):
        z=X[identities==person]
        for i in range(0,len(z)-k+1,k):
            xs.append(z[i:i+k].mean(axis=0)); ys.append(person)
    if not xs: return np.empty((0,X.shape[1])),np.array([])
    return np.vstack(xs),np.asarray(ys)

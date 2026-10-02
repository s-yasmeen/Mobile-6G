import numpy as np
from sklearn.model_selection import GroupShuffleSplit, train_test_split


def known_identity_session_split(y_identity,groups,test_size=.2,seed=42,max_tries=200):
    """Group-disjoint split while retaining every test identity in training."""
    y=np.asarray(y_identity); groups=np.asarray(groups); idx=np.arange(len(y))
    for s in range(seed,seed+max_tries):
        tr,te=next(GroupShuffleSplit(n_splits=1,test_size=test_size,random_state=s).split(idx,y,groups))
        if set(np.unique(y[te])).issubset(set(np.unique(y[tr]))): return tr,te
    raise ValueError("Could not form group-disjoint known-identity split; inspect sessions per identity.")


def group_split(groups,test_size=.2,seed=42):
    idx=np.arange(len(groups)); return next(GroupShuffleSplit(n_splits=1,test_size=test_size,random_state=seed).split(idx,groups=groups))


def stratified_split(y,test_size=.2,seed=42):
    idx=np.arange(len(y)); return train_test_split(idx,test_size=test_size,random_state=seed,stratify=y)

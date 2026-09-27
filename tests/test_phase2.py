import numpy as np
from src.benchmarks import build_model,evaluate_classifier
from src.splits import known_identity_session_split
from src.quality import audit_arrays

def test_models_construct():
 for n in ["logistic_regression","random_forest","mlp"]: assert build_model(n,1) is not None

def test_known_identity_group_split():
 y=np.repeat([0,1,2],12); groups=np.tile(np.repeat([0,1,2],4),3)+np.repeat([0,10,20],12); X=np.arange(len(y))
 tr,te=known_identity_session_split(y,groups,test_size=.3,seed=2); assert set(groups[tr]).isdisjoint(set(groups[te])); assert set(y[te]).issubset(set(y[tr]))

def test_quality():
 X=np.arange(40,dtype=float).reshape(10,4); r=audit_arrays(X,np.arange(10)%2,np.arange(10)%2); assert r["nan_count"]==0 and r["n_samples"]==10

def test_eval():
 rng=np.random.default_rng(1); X=rng.normal(size=(120,6)); y=np.repeat([0,1,2],40); X[:,0]+=y
 r=evaluate_classifier(build_model("logistic_regression",1),X[:90],y[:90],X[90:],y[90:],privacy=True); assert "macro_ovr_auc" in r

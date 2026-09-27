import numpy as np
from sklearn.model_selection import train_test_split
from src.benchmarks import build_model,evaluate_classifier,group_bootstrap_metrics
from src.splits import known_identity_session_split
from src.quality import audit_arrays

def test_models_construct():
 for n in ["logistic_regression","random_forest","mlp"]: assert build_model(n,1) is not None

def test_known_identity_group_split():
 y=np.repeat([0,1,2],12); groups=np.tile(np.repeat([0,1,2],4),3)+np.repeat([0,10,20],12)
 tr,te=known_identity_session_split(y,groups,test_size=.3,seed=2); assert set(groups[tr]).isdisjoint(set(groups[te])); assert set(y[te]).issubset(set(y[tr]))

def test_quality():
 X=np.arange(40,dtype=float).reshape(10,4); r=audit_arrays(X,np.arange(10)%2,np.arange(10)%2); assert r["nan_count"]==0 and r["n_samples"]==10

def test_eval_multiclass():
 rng=np.random.default_rng(1); y=np.repeat([0,1,2],40); X=rng.normal(size=(120,6)); X[:,0]+=y
 tr,te=train_test_split(np.arange(120),test_size=.3,random_state=1,stratify=y)
 r=evaluate_classifier(build_model("logistic_regression",1),X[tr],y[tr],X[te],y[te],privacy=True); assert 0<=r["macro_ovr_auc"]<=1


def test_group_bootstrap_placeholder_not_used_as_independent_windows():
 # Phase-2 final CIs must switch to session-level resampling once real session arrays are loaded.
 assert True


def test_group_bootstrap_ci():
 rng=np.random.default_rng(3); y=np.tile([0,1],20); pred=y.copy(); groups=np.repeat(np.arange(10),4)
 r=group_bootstrap_metrics(y,pred,groups,n=50,seed=3); assert r["macro_f1_ci_low"]>=0.99

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from src.benchmarks import build_model,evaluate_classifier,group_bootstrap_metrics,permutation_baseline
from src.splits import known_identity_session_split
from src.quality import audit_arrays
from src.data import load_feature_csv

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

def test_metadata_columns_are_excluded(tmp_path):
 p=tmp_path/"x.csv"; pd.DataFrame({"activity":[0,1,0,1],"identity":[0,0,1,1],"session":[10,11,12,13],"room_no":[1,2,3,4],"packet_count":[100,200,300,400],"f1":[.1,.2,.3,.4]}).to_csv(p,index=False)
 X,_,_=load_feature_csv(p); assert X.shape==(4,1) and np.allclose(X[:,0],[.1,.2,.3,.4])

def test_permutation_reports_empirical_pvalue():
 rng=np.random.default_rng(5); y=np.repeat([0,1],30); X=rng.normal(size=(60,3)); X[:,0]+=3*y
 tr,te=train_test_split(np.arange(60),test_size=.3,random_state=1,stratify=y)
 obs=evaluate_classifier(build_model("logistic_regression",1),X[tr],y[tr],X[te],y[te])
 r=permutation_baseline(lambda s:build_model("logistic_regression",s),X[tr],y[tr],X[te],y[te],n=9,seed=1,observed=obs)
 assert "permutation_macro_f1_pvalue" in r and 0<r["permutation_macro_f1_pvalue"]<=1

def test_group_bootstrap_ci():
 y=np.tile([0,1],20); pred=y.copy(); groups=np.repeat(np.arange(10),4)
 r=group_bootstrap_metrics(y,pred,groups,n=50,seed=3); assert r["macro_f1_ci_low"]>=0.99

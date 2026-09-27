import numpy as np
from src.risk_gate import GateThresholds,release_decision
from src.privacy import sanitize,aggregate_releases

def test_gate():
 t=GateThresholds(); assert release_decision(.5,.9,t)=="ALLOW"; assert release_decision(.65,.9,t)=="SANITIZE"; assert release_decision(.8,.9,t)=="BLOCK"; assert release_decision(.5,.2,t)=="BLOCK"
def test_sanitize_shape():
 x=np.ones((10,3)); assert sanitize(x,"noise").shape==x.shape

def test_aggregate():
 x=np.arange(24).reshape(8,3); y=np.array([0]*4+[1]*4); z,labels=aggregate_releases(x,y,2); assert z.shape==(4,3); assert len(labels)==4

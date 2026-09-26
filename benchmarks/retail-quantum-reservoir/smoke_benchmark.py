"""Deterministic smoke benchmark for the Retail Quantum Reservoir track.

This is a simulator-only falsifiability harness. It does not claim quantum
advantage or quantum-hardware execution. Both arms receive the same sequence
and use the same ridge-regression readout.
"""
from __future__ import annotations
import json, math, random, time
from pathlib import Path

SEED = 20260926
TRAIN = 180
TEST = 60
RIDGE = 1e-3
ESN_DIM = 8
QUBITS = 3

def sequence(n=TRAIN+TEST+1):
    # Deterministic nonlinear temporal signal; intentionally not retail data.
    return [0.55*math.sin(i*0.17)+0.25*math.sin(i*0.047)+0.2*math.sin(i*0.011*i) for i in range(n)]

def ridge_fit(X, y, lam=RIDGE):
    # Dependency-free normal equations with Gaussian elimination.
    p=len(X[0]); a=[[sum(r[i]*r[j] for r in X)+(lam if i==j else 0.0) for j in range(p)] for i in range(p)]
    b=[sum(r[i]*t for r,t in zip(X,y)) for i in range(p)]
    for i in range(p):
        pivot=max(range(i,p), key=lambda k:abs(a[k][i])); a[i],a[pivot]=a[pivot],a[i]; b[i],b[pivot]=b[pivot],b[i]
        d=a[i][i]
        if abs(d)<1e-12: raise ValueError("singular ridge system")
        for j in range(i,p): a[i][j]/=d
        b[i]/=d
        for k in range(p):
            if k==i: continue
            f=a[k][i]
            for j in range(i,p): a[k][j]-=f*a[i][j]
            b[k]-=f*b[i]
    return b

def dot(a,b): return sum(x*y for x,y in zip(a,b))

def esn_features(xs):
    rng=random.Random(SEED)
    win=[rng.uniform(-0.8,0.8) for _ in range(ESN_DIM)]
    rec=[[rng.uniform(-0.18,0.18) for _ in range(ESN_DIM)] for _ in range(ESN_DIM)]
    s=[0.0]*ESN_DIM; out=[]
    for x in xs:
        s=[math.tanh(win[i]*x+sum(rec[i][j]*s[j] for j in range(ESN_DIM))) for i in range(ESN_DIM)]
        out.append([1.0]+s)
    return out

def quantum_features(xs):
    # Exact state-vector simulation of 3 qubits with input-dependent Ry-like
    # rotations and fixed nearest-neighbour phase coupling. Measurements are
    # expectation values <Z_i> and pair correlations <Z_i Z_j>.
    dim=1<<QUBITS; state=[0j]*dim; state[0]=1+0j; out=[]
    phases=[0.31,0.53]
    for x in xs:
        for q in range(QUBITS):
            th=(q+1)*0.7*x+0.13*(q+1); c=math.cos(th/2); s=math.sin(th/2)
            new=state[:]; bit=1<<q
            for k in range(dim):
                if k&bit: continue
                a,b=state[k],state[k|bit]; new[k]=c*a-s*b; new[k|bit]=s*a+c*b
            state=new
        for q,phi in enumerate(phases):
            mask=(1<<q)|(1<<(q+1))
            for k in range(dim):
                if (k&mask)==mask: state[k]*=complex(math.cos(phi),math.sin(phi))
        probs=[abs(a)**2 for a in state]
        z=[]
        for q in range(QUBITS):
            z.append(sum(p*(1 if not(k&(1<<q)) else -1) for k,p in enumerate(probs)))
        zz=[]
        for q in range(QUBITS-1):
            zz.append(sum(p*(1 if bool(k&(1<<q))==bool(k&(1<<(q+1))) else -1) for k,p in enumerate(probs)))
        out.append([1.0]+z+zz)
    return out

def evaluate(name, feats, ys):
    Xtr=feats[:TRAIN]; ytr=ys[:TRAIN]; Xte=feats[TRAIN:TRAIN+TEST]; yte=ys[TRAIN:TRAIN+TEST]
    t=time.perf_counter(); w=ridge_fit(Xtr,ytr); pred=[dot(w,r) for r in Xte]; elapsed=time.perf_counter()-t
    mae=sum(abs(a-b) for a,b in zip(pred,yte))/len(yte)
    denom=sum(abs(v) for v in yte); wape=sum(abs(a-b) for a,b in zip(pred,yte))/denom if denom else None
    return {"model":name,"mae":mae,"wape":wape,"readout_seconds":elapsed,"feature_dimension":len(feats[0])}

def main():
    raw=sequence(); inputs=raw[:-1]; targets=raw[1:]
    results=[]
    for name,fn in [("classical_esn",esn_features),("quantum_statevector_simulator",quantum_features)]:
        t=time.perf_counter(); f=fn(inputs); feature_s=time.perf_counter()-t
        r=evaluate(name,f,targets); r["feature_seconds"]=feature_s; results.append(r)
    payload={"status":"smoke_only","seed":SEED,"train_points":TRAIN,"test_points":TEST,"ridge":RIDGE,
             "quantum_hardware":False,"claim":"No quantum advantage claimed.","results":results}
    path=Path(__file__).with_name("metrics.json"); path.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps(payload,indent=2))

if __name__=="__main__": main()

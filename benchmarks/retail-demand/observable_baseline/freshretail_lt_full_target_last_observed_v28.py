"""FreshRetailNet-LT v2.8: historical-only full-target last-observed baseline.
EVAL supplies target keys only; no future sales, stock flags or labels are read.
A software coverage pass is not an official score or latent-demand evidence.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, io, json, math, os, platform
from pathlib import Path
from freshretail_lt_source_gate_v18 import TRAIN_BYTES,TRAIN_SHA256,EVAL_BYTES,EVAL_SHA256,REVISION,verify_file

ORIGIN=dt.date(2025,7,14)
DAYS=tuple(ORIGIN+dt.timedelta(days=i) for i in range(7))
FIELDS=('store_id','product_id','dt','prediction')
class FullTargetError(ValueError): pass

def ident(v):
    if type(v) is not int or not 0<=v<10**18: raise FullTargetError('invalid identifier')
    return v

def day(v):
    if type(v) is dt.date: return v
    if type(v) is str:
        try: d=dt.date.fromisoformat(v)
        except ValueError as e: raise FullTargetError('invalid date') from e
        if d.isoformat()==v: return d
    raise FullTargetError('noncanonical date')

def historical(rows,expected=None):
    latest={}; n=0
    for r in rows:
        try:
            k=(ident(r['store_id']),ident(r['product_id']))
            d=day(r['dt']); q=r['sale_amount']
        except (KeyError,TypeError) as e: raise FullTargetError('invalid TRAIN row') from e
        if d>=ORIGIN: raise FullTargetError('future TRAIN leakage')
        if type(q) not in (int,float): raise FullTargetError('invalid quantity type')
        q=float(q)
        if not math.isfinite(q) or q<0: raise FullTargetError('invalid quantity')
        old=latest.get(k)
        if old is None or d>old[0]: latest[k]=(d,q)
        elif d==old[0]: raise FullTargetError('duplicate latest history')
        n+=1
    if not n or (expected is not None and n!=expected):
        raise FullTargetError('TRAIN count mismatch')
    return latest,n

def forecast(latest,targets,expected=70000):
    if type(expected) is not int or expected<1: raise FullTargetError('invalid expected')
    seen=set(); records=[]; fallback=0
    per_day={d:0 for d in DAYS}
    for r in targets:
        try: k=(ident(r['store_id']),ident(r['product_id'])); d=day(r['dt'])
        except (KeyError,TypeError) as e: raise FullTargetError('invalid EVAL key') from e
        if d not in DAYS: raise FullTargetError('date outside horizon')
        full=(k[0],k[1],d.isoformat())
        if full in seen: raise FullTargetError('duplicate target')
        seen.add(full)
        if len(seen)>expected: raise FullTargetError('too many targets')
        per_day[d]+=1
        prior=latest.get(k)
        if prior is None: fallback+=1
        records.append((*full,0.0 if prior is None else prior[1]))
    if len(seen)!=expected: raise FullTargetError('incomplete targets')
    buf=io.StringIO(newline='')
    writer=csv.writer(buf,lineterminator='\n')
    writer.writerow(FIELDS)
    for a,b,d,q in sorted(records): writer.writerow((a,b,d,format(q,'.17g')))
    raw=buf.getvalue().encode('utf-8')
    return raw,{'target_rows':len(seen),'predicted_rows':len(records),
                'historical_series':len(latest),'zero_fallback_rows':fallback,
                'per_day':{d.isoformat():per_day[d] for d in DAYS},
                'csv_sha256':hashlib.sha256(raw).hexdigest(),'csv_bytes':len(raw),
                'model':'last observed TRAIN sale_amount; zero for unseen series',
                'evaluation_labels_read':False,'evaluation_features_read':False,
                'official_scoring_mask_applied':False,'full_target_gate':'TBD',
                'forecast_accuracy':'TBD','latent_demand':'TBD',
                'leaderboard_comparable':False,'maturity_change':'NONE'}

def parquet_rows(path,columns):
    import pyarrow.parquet as pq
    p=pq.ParquetFile(path)
    if not set(columns).issubset(p.schema_arrow.names):
        raise FullTargetError('required source columns absent')
    for batch in p.iter_batches(batch_size=8192,columns=list(columns)):
        yield from batch.to_pylist()

def run(train,eval_path):
    train,eval_path=Path(train),Path(eval_path)
    if train.resolve()==eval_path.resolve(): raise FullTargetError('same source path')
    t=verify_file(train,TRAIN_BYTES,TRAIN_SHA256)
    e=verify_file(eval_path,EVAL_BYTES,EVAL_SHA256)
    latest,n=historical(parquet_rows(train,('store_id','product_id','dt','sale_amount')),7869549)
    raw,summary=forecast(latest,parquet_rows(eval_path,FIELDS[:3]))
    if verify_file(train,TRAIN_BYTES,TRAIN_SHA256)!=t or verify_file(eval_path,EVAL_BYTES,EVAL_SHA256)!=e:
        raise FullTargetError('source bytes changed during run')
    import pyarrow
    return raw,{'experiment':'retail-lt-v28-full-target-last-observed',
                'provenance':{'dataset':'Dingdong-Inc/FreshRetailNet-LT',
                    'revision':REVISION,'train_sha256':t['sha256'],
                    'eval_sha256_keys_only':e['sha256'],'train_rows':n,
                    'python':platform.python_version(),'pyarrow':pyarrow.__version__,
                    'os':platform.system(),'commit':os.environ.get('GITHUB_SHA','TBD'),
                    'publisher_independent_authenticity':'TBD'},
                'result':summary}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('train','eval','predictions','report'): p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    paths=[x.resolve() for x in (a.train,a.eval,a.predictions,a.report)]
    if len(set(paths))!=4 or a.predictions.exists() or a.report.exists():
        raise SystemExit('distinct, new output paths required')
    raw,report=run(a.train,a.eval)
    a.predictions.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    with a.predictions.open('xb') as f: f.write(raw)
    with a.report.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(report,f,sort_keys=True,indent=2,allow_nan=False); f.write('\n')
    print(json.dumps({'rows':report['result']['target_rows'],
                      'fallback':report['result']['zero_fallback_rows'],
                      'sha256':report['result']['csv_sha256'],
                      'evaluation_labels_read':False},sort_keys=True))
if __name__=='__main__': main()

import zipfile,gzip,os,json
import pandas as pd,numpy as np
from scipy.special import xlogy
from pathlib import Path
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve(); SRC=ROOT/'Intraday_Cleaned_Datasets_v1(1).zip'; OUT=ROOT/'R05_SemiMarkov_30min_v1'; OUT.mkdir(exist_ok=True)
classes=['DOWN','FLAT','UP']; periods={'discovery':(2008,2019),'validation':(2020,2023),'holdout':(2024,2026)}
records=[]; metrics=[]; rows=[]
with zipfile.ZipFile(SRC) as z:
 for sym in ['SPY','QQQ']:
  with gzip.open(z.open(f'{sym}_clean_rth_1min.csv.gz'),'rt') as f: df=pd.read_csv(f, usecols=['session_date','timestamp_et','open','close'],parse_dates=['session_date','timestamp_et'])
  df=df[df.session_date.dt.year>=2008].sort_values(['session_date','timestamp_et'])
  df['minute_idx']=df.groupby('session_date').cumcount();df['bin']=df.minute_idx//30
  bars=df.groupby(['session_date','bin'],sort=True).agg(o=('open','first'),c=('close','last'),n=('close','size')).reset_index()
  bars=bars[bars.n==30].copy();bars['ret']=bars.c/bars.o-1
  bars['state']=np.select([bars.ret<-.0005,bars.ret>.0005],[0,2],default=1).astype('int8')
  # Cumulative run length within sessions; resets on state changes and each session.
  bars['change']=(bars.state!=bars.groupby('session_date').state.shift()) | bars['bin'].eq(0)
  bars['run_group']=bars.change.cumsum()
  bars['run_length']=bars.groupby('run_group').cumcount()+1
  bars['next_state']=bars.groupby('session_date').state.shift(-1)
  trans=bars[bars.next_state.notna()].copy();trans['next_state']=trans.next_state.astype('int8');trans['bucket']=trans.run_length.clip(upper=4)
  trans['year']=trans.session_date.dt.year
  for pname,(a,b) in periods.items():
   t=trans[trans.year.between(a,b)];rows.append({'symbol':sym,'period':pname,'sessions':t.session_date.nunique(),'transitions':len(t),'run_length_1':int((t.bucket==1).sum()),'run_length_2':int((t.bucket==2).sum()),'run_length_3':int((t.bucket==3).sum()),'run_length_4plus':int((t.bucket==4).sum())})
  disc=trans[trans.year.between(2008,2019)]
  state_counts=np.bincount(disc.next_state,minlength=3);base=(state_counts+1)/(state_counts.sum()+3)
  c1=np.zeros((3,3),dtype=int);c2=np.zeros((3,4,3),dtype=int)
  for a,b in zip(disc.state,disc.next_state):c1[a,b]+=1
  for a,k,b in zip(disc.state,disc.bucket,disc.next_state):c2[a,k-1,b]+=1
  p1=(c1+1)/(c1.sum(axis=1,keepdims=True)+3)
  # Pre-defined hierarchical smoothing: 100 first-order pseudo-observations per duration bucket.
  p2=(c2+100*p1[:,None,:])/(c2.sum(axis=2,keepdims=True)+100)
  for s in range(3):
   for k in range(1,5):
    for target in range(3):
     records.append(dict(symbol=sym,current=classes[s],duration_bucket=f'{k}' if k<4 else '4+',next_state=classes[target],discovery_count=int(c2[s,k-1,target]),first_order_probability=float(p1[s,target]),duration_probability=float(p2[s,k-1,target])))
  for pname,(a,b) in periods.items():
   t=trans[trans.year.between(a,b)].copy()
   y=t.next_state.to_numpy();q0=np.broadcast_to(base,(len(y),3));q1=p1[t.state.to_numpy()];q2=p2[t.state.to_numpy(),t.bucket.to_numpy()-1]
   onehot=np.eye(3)[y];d=t.session_date.to_numpy()
   for model,q in [('unconditional',q0),('first_order_Markov',q1),('duration_conditioned',q2)]:
    brier=((q-onehot)**2).sum(axis=1);ll=-np.log(q[np.arange(len(y)),y]);acc=(q.argmax(axis=1)==y)
    metrics.append(dict(symbol=sym,period=pname,model=model,transitions=len(y),sessions=t.session_date.nunique(),accuracy=float(acc.mean()),brier=float(brier.mean()),log_loss=float(ll.mean())))
   if pname!='discovery':
    comparison=pd.DataFrame({'session_date':d,'brier_gain_vs_markov':((q1-onehot)**2).sum(axis=1)-((q2-onehot)**2).sum(axis=1),'logloss_gain_vs_markov':(-np.log(q1[np.arange(len(y)),y]))-(-np.log(q2[np.arange(len(y)),y]))})
    daily=comparison.groupby('session_date').agg(brier_gain=('brier_gain_vs_markov','mean'),logloss_gain=('logloss_gain_vs_markov','mean'),n=('brier_gain_vs_markov','size'))
    # Bootstrap sessions, with variable count weighted properly; percentile CI.
    rng=np.random.default_rng(12345);G=daily[['brier_gain','logloss_gain','n']].to_numpy();N=len(G);bootstrap=[]
    for _ in range(1200):
     ix=rng.integers(0,N,size=N);v=G[ix];bootstrap.append([(v[:,0]*v[:,2]).sum()/v[:,2].sum(),(v[:,1]*v[:,2]).sum()/v[:,2].sum()])
    ci=np.percentile(bootstrap,[2.5,97.5],axis=0)
    records.append(dict(symbol=sym,period=pname,metric='delta_brier_markov_minus_duration',estimate=float(comparison.brier_gain_vs_markov.mean()),ci_lower=float(ci[0,0]),ci_upper=float(ci[1,0])))
    records.append(dict(symbol=sym,period=pname,metric='delta_logloss_markov_minus_duration',estimate=float(comparison.logloss_gain_vs_markov.mean()),ci_lower=float(ci[0,1]),ci_upper=float(ci[1,1])))
  # empirical conditional probabilities on discovery for transparency
  for s in [0,2]:
   for k in range(1,5):
    t=disc[(disc.state==s)&(disc.bucket==k)];counts=np.bincount(t.next_state,minlength=3)
    print(sym,classes[s],k,len(t),'empirical',np.round(counts/max(len(t),1),4),'shrunk',np.round(p2[s,k-1],4),flush=True)
  pd.DataFrame({'date':trans.session_date.dt.strftime('%Y-%m-%d'),'bin':trans.bin,'current_state':trans.state.map(dict(enumerate(classes))),'streak_length':trans.run_length,'next_state':trans.next_state.map(dict(enumerate(classes))),'return_30min':trans.ret}).to_csv(OUT/f'{sym}_transitions.csv.gz',index=False,compression='gzip')
pd.DataFrame(metrics).to_csv(OUT/'model_metrics.csv',index=False)
pd.DataFrame(rows).to_csv(OUT/'sample_sizes.csv',index=False)
pd.DataFrame([r for r in records if 'next_state' in r]).to_csv(OUT/'discovery_duration_transition_probabilities.csv',index=False)
pd.DataFrame([r for r in records if 'metric' in r]).to_csv(OUT/'bootstrap_uncertainty.csv',index=False)
print('METRICS');print(pd.DataFrame(metrics).to_string(index=False));print('UNCERTAINTY');print(pd.DataFrame([r for r in records if 'metric' in r]).to_string(index=False))

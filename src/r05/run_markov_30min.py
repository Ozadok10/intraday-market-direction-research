import os
from pathlib import Path
import io,zipfile,gzip
import numpy as np,pandas as pd
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve()
ARCHIVE=ROOT/'Intraday_Cleaned_Datasets_v1(1).zip'
if not ARCHIVE.exists(): ARCHIVE=ROOT/'Intraday_Cleaned_Datasets_v1.zip'
THRESHOLD=0.05 # percent points
classes=np.array(['DOWN','FLAT','UP']); splits={'discovery':(2008,2019),'validation':(2020,2023),'holdout':(2024,2026)}
all_events=[]
with zipfile.ZipFile(ARCHIVE) as z:
 for sym in ['SPY','QQQ']:
  raw=z.read(f'{sym}_clean_rth_1min.csv.gz')
  df=pd.read_csv(io.BytesIO(gzip.decompress(raw)),usecols=['session_date','timestamp_et','open','close'])
  df=df[(df.session_date>='2008-01-01')&(df.session_date<='2026-09-30')].copy()
  df['minute']=pd.to_datetime(df.timestamp_et).dt.hour*60+pd.to_datetime(df.timestamp_et).dt.minute-570
  df['block']=df.minute//30
  # every 5-minute bar must consist of thirty source rows, and adjacent blocks must be consecutive
  b=df.groupby(['session_date','block'],sort=True).agg(first_open=('open','first'),end_close=('close','last'),n=('close','size')).reset_index()
  b=b[b.n==30].copy()
  b['prev_close']=b.groupby('session_date').end_close.shift(1)
  b['ret_pct']=100*(b.end_close/b.prev_close-1)
  b['state']=np.select([b.ret_pct<-THRESHOLD,b.ret_pct>THRESHOLD],['DOWN','UP'],default='FLAT')
  b['next_state']=b.groupby('session_date').state.shift(-1)
  b['next_block']=b.groupby('session_date').block.shift(-1)
  b=b[(b.prev_close.notna())&(b.next_state.notna())&(b.next_block==b.block+1)].copy()
  b['ticker']=sym
  b['year']=b.session_date.str[:4].astype(int)
  b['period']=np.select([b.year<=2019,b.year<=2023],['discovery','validation'],default='holdout')
  all_events.append(b[['ticker','session_date','block','year','period','ret_pct','state','next_state']])
events=pd.concat(all_events,ignore_index=True)
events.to_csv(ROOT/'R05_30min_State_Transitions_v1.csv',index=False)
counts=events.groupby(['ticker','period','state','next_state']).size().rename('n').reset_index()
idx=pd.MultiIndex.from_product([['SPY','QQQ'],list(splits),classes,classes],names=['ticker','period','state','next_state'])
counts=counts.set_index(['ticker','period','state','next_state']).reindex(idx,fill_value=0).reset_index()
counts['state_total']=counts.groupby(['ticker','period','state'])['n'].transform('sum')
counts['transition_pct']=np.where(counts.state_total>0,100*counts.n/counts.state_total,np.nan)
counts.to_csv(ROOT/'R05_30min_Transition_Matrices_v1.csv',index=False)
summary=[]; annual=[]
for sym in ['SPY','QQQ']:
 train=events[(events.ticker==sym)&(events.period=='discovery')]
 ns=train.next_state.value_counts().reindex(classes,fill_value=0).to_numpy(dtype=float)
 base=(ns+1)/(ns.sum()+3)
 mat=np.zeros((3,3))
 for i,s in enumerate(classes):
  n=train[train.state==s].next_state.value_counts().reindex(classes,fill_value=0).to_numpy(dtype=float)
  mat[i]=(n+1)/(n.sum()+3)
 for period in splits:
  test=events[(events.ticker==sym)&(events.period==period)]
  for year,group in [('all',test)]+[(str(int(y)),g) for y,g in test.groupby('year')]:
   yt=pd.Categorical(group.next_state,categories=classes).codes
   xt=pd.Categorical(group.state,categories=classes).codes
   pm=mat[xt];pb=np.tile(base,(len(group),1)); yoh=np.eye(3)[yt]
   accm=(np.argmax(pm,axis=1)==yt).mean();accb=(np.argmax(pb,axis=1)==yt).mean()
   bm=np.mean(np.sum((pm-yoh)**2,axis=1));bb=np.mean(np.sum((pb-yoh)**2,axis=1))
   lm=np.mean(-np.log(pm[np.arange(len(group)),yt]));lb=np.mean(-np.log(pb[np.arange(len(group)),yt]))
   d={'ticker':sym,'period':period,'year':year,'n':len(group),'markov_accuracy_pct':100*accm,'baseline_accuracy_pct':100*accb,'markov_brier':bm,'baseline_brier':bb,'brier_improvement_pct':100*(bb-bm)/bb,'markov_log_loss':lm,'baseline_log_loss':lb,'log_loss_improvement_pct':100*(lb-lm)/lb}
   (summary if year=='all' else annual).append(d)
pd.DataFrame(summary).to_csv(ROOT/'R05_30min_Model_Performance_v1.csv',index=False)
pd.DataFrame(annual).to_csv(ROOT/'R05_30min_Annual_Performance_v1.csv',index=False)
print(pd.DataFrame(summary).to_string(index=False))
print('Rows',len(events),'days',events.groupby('ticker').session_date.nunique().to_dict())

#!/usr/bin/env python3
import os
"""R06 v2: 0.50% entry + 0.50% first-touch barriers; 30/60/90/EOD and EOD close.
Re-run: set INTRADAY_WORKDIR to a directory containing the input ZIP, or pass --source.
"""
import argparse, gzip, zipfile, sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve()
CHECKPOINTS=('10:00','10:30','11:30','13:00','14:30','15:30')
MOVE=BARRIER=0.005
PERIODS={'discovery':(2008,2019),'validation':(2020,2023),'holdout':(2024,2026)}
HORIZONS=(30,60,90)
def period(year):
 for p,(lo,hi) in PERIODS.items():
  if lo<=year<=hi:return p
 return None

def read_symbol(z,sym):
 with z.open(sym+'_clean_rth_1min.csv.gz') as compressed:
  with gzip.GzipFile(fileobj=compressed) as f:
   return pd.read_csv(f,parse_dates=['timestamp_et'],usecols=['timestamp_et','session_date','open','high','low','close','volume'])

def collect(z,sym):
 df=read_symbol(z,sym)
 df=df[df.timestamp_et.dt.year>=2008]
 events=[]
 for date,g in df.groupby('session_date',sort=False):
  p=period(int(str(date)[:4]));
  if p is None:continue
  g=g.sort_values('timestamp_et')
  times=g.timestamp_et.dt.strftime('%H:%M').to_numpy(); loc={t:i for i,t in enumerate(times)}
  close=g.close.to_numpy(); high=g.high.to_numpy();low=g.low.to_numpy()
  n=len(g)
  for clock in CHECKPOINTS:
   if clock not in loc:continue
   i=loc[clock]
   if i<30:continue
   prev=close[i-30];anchor=close[i]
   prior_ret=anchor/prev-1
   if abs(prior_ret)<MOVE:continue
   direction='UP' if prior_ret>0 else 'DOWN';sign=1 if prior_ret>0 else -1
   available=n-i-1
   if available<=0:continue
   h=high[i+1:];l=low[i+1:]
   if sign==1:
    c=(h>=anchor*(1+BARRIER));r=(l<=anchor*(1-BARRIER))
   else:
    c=(l<=anchor*(1-BARRIER));r=(h>=anchor*(1+BARRIER))
   hits=np.flatnonzero(c|r)
   if len(hits):
    first=int(hits[0]);hit_minute=first+1
    kind='AMBIGUOUS' if c[first] and r[first] else ('CONTINUATION' if c[first] else 'REVERSAL')
   else:
    hit_minute=available;kind='CENSORED'
   elapsed=hit_minute-1 if kind=='AMBIGUOUS' else hit_minute
   eod_close=close[-1];signed_eod=(eod_close/anchor-1)*sign*100
   # close status in significant-threshold and sign-only formats
   cls='CONTINUATION' if signed_eod>=0.5 else 'REVERSAL' if signed_eod<=-0.5 else 'WITHIN_BARRIERS'
   sign_cls='CONTINUATION' if signed_eod>0 else 'REVERSAL' if signed_eod<0 else 'UNCHANGED'
   events.append(dict(symbol=sym,period=p,session_date=str(date),checkpoint_et=clock,
    previous_move_direction=direction,previous_30m_return_pct=round(prior_ret*100,8),
    anchor_price=float(anchor),minutes_available=available,elapsed_minutes=elapsed,
    event_type='CENSORED' if kind=='AMBIGUOUS' else kind,ambiguous=int(kind=='AMBIGUOUS'),
    continuation_hit=int(kind=='CONTINUATION'),reversal_hit=int(kind=='REVERSAL'),
    censored=int(kind in ('AMBIGUOUS','CENSORED')),
    eod_close_price=float(eod_close),eod_signed_return_pct=round(signed_eod,8),
    eod_absolute_return_pct=round((eod_close/anchor-1)*100,8),
    eod_close_threshold_state=cls,eod_close_sign_state=sign_cls))
 return pd.DataFrame(events)

def event_at_horizon(g,horizon):
 # use full follow-up for fixed horizons, avoid comparing early and late checkpoints with unequal exposure
 eligible=g if horizon=='EOD' else g[g.minutes_available>=horizon]
 N=len(eligible)
 if N==0:return None
 if horizon=='EOD':ev=eligible
 else:ev=eligible[eligible.elapsed_minutes<=horizon]
 cont=int((ev.event_type=='CONTINUATION').sum());rev=int((ev.event_type=='REVERSAL').sum())
 amb=int(((ev.event_type=='CENSORED') & (ev.ambiguous==1)).sum())
 return dict(horizon=str(horizon),observations=N,continuation_first=cont,reversal_first=rev,
  unresolved=N-cont-rev,ambiguous_first=amb,
  continuation_first_rate=cont/N,reversal_first_rate=rev/N,unresolved_rate=(N-cont-rev)/N)

def aj(g):
 time=g.elapsed_minutes.to_numpy();typ=g.event_type.to_numpy();mx=int(time.max()); S=1.;Fc=Fr=0.;rows=[]
 for minute in range(mx+1):
  risk=int((time>=minute).sum());dc=int(((time==minute)&(typ=='CONTINUATION')).sum());dr=int(((time==minute)&(typ=='REVERSAL')).sum());cen=int(((time==minute)&(typ=='CENSORED')).sum())
  if risk:
   Fc+=S*dc/risk;Fr+=S*dr/risk;S*=1-(dc+dr)/risk
  rows.append(dict(elapsed_minutes=minute,at_risk=risk,continuation_events=dc,reversal_events=dr,censored_at_minute=cen,prob_neither_event=S,cum_prob_continuation=Fc,cum_prob_reversal=Fr))
 return rows

def main(source):
 with zipfile.ZipFile(source) as z:
  events=pd.concat([collect(z,s) for s in ('SPY','QQQ')],ignore_index=True)
 if events.empty:raise RuntimeError('No qualifying events')
 events.to_csv(ROOT/'r06_v2_checkpoint_events.csv',index=False)
 key=['symbol','period','previous_move_direction']
 horizon=[]; curves=[];close=[];group=[]
 for keys,g in events.groupby(key,sort=True):
  ids=dict(zip(key,keys));n=len(g)
  for h in (*HORIZONS,'EOD'):
   res=event_at_horizon(g,h)
   if res:horizon.append(dict(**ids,**res))
  for row in aj(g):curves.append(dict(**ids,**row))
  counts=g.eod_close_threshold_state.value_counts()
  signs=g.eod_close_sign_state.value_counts()
  close.append(dict(**ids,observations=n,avg_eod_signed_return_pct=g.eod_signed_return_pct.mean(),median_eod_signed_return_pct=g.eod_signed_return_pct.median(),
   eod_continuation_0p5_count=int(counts.get('CONTINUATION',0)),eod_reversal_0p5_count=int(counts.get('REVERSAL',0)),eod_within_0p5_count=int(counts.get('WITHIN_BARRIERS',0)),
   eod_continuation_0p5_rate=counts.get('CONTINUATION',0)/n,eod_reversal_0p5_rate=counts.get('REVERSAL',0)/n,eod_within_0p5_rate=counts.get('WITHIN_BARRIERS',0)/n,
   eod_positive_direction_count=int(signs.get('CONTINUATION',0)),eod_negative_direction_count=int(signs.get('REVERSAL',0)),
   eod_positive_direction_rate=signs.get('CONTINUATION',0)/n,eod_negative_direction_rate=signs.get('REVERSAL',0)/n))
  group.append(dict(**ids,observations=n,continuations=int(g.continuation_hit.sum()),reversals=int(g.reversal_hit.sum()),censored=int(g.censored.sum()),ambiguous=int(g.ambiguous.sum()),mean_minutes_observed=g.elapsed_minutes.mean(),median_minutes_observed=g.elapsed_minutes.median()))
 tables={'r06_v2_checkpoint_events':events,'r06_v2_first_touch_horizons':pd.DataFrame(horizon),
  'r06_v2_competing_risks_curves':pd.DataFrame(curves),'r06_v2_eod_close_summary':pd.DataFrame(close),
  'r06_v2_group_summary':pd.DataFrame(group)}
 # checkpoint and direction EOD/horizon summary for Tableau breakdowns
 for table,df in tables.items():
  if table!='r06_v2_checkpoint_events':df.to_csv(ROOT/(table+'.csv'),index=False)
 with sqlite3.connect(ROOT/'r06_v2_dashboard_ready.sqlite') as cn:
  for name,df in tables.items():df.to_sql(name,cn,index=False,if_exists='replace')
  cn.execute('CREATE INDEX idx_r06_v2_event ON r06_v2_checkpoint_events (symbol,period,session_date,checkpoint_et,previous_move_direction)')
 print('EVENTS',len(events),'\n',tables['r06_v2_group_summary'].to_string(index=False))
 print('HORIZONS\n',tables['r06_v2_first_touch_horizons'].to_string(index=False))
 print('EOD\n',tables['r06_v2_eod_close_summary'].to_string(index=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',default=str(ROOT/'Intraday_Cleaned_Datasets_v1(1).zip'));main(ap.parse_args().source)

import os
from pathlib import Path
from scipy.stats import binomtest,ttest_1samp
from statsmodels.stats.proportion import proportion_confint
import csv,zipfile,io,collections,statistics,math
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve(); SRC=ROOT/'Intraday_Research_Eligibility_v3(1).zip'; OUT=ROOT/'R01_Final_Holdout_2024_2026_v1';OUT.mkdir(exist_ok=True)
CHECKS=[('10:00','opening','09:30:00','09:59:00','10:00:00','10:29:00'),('10:30','opening','10:00:00','10:29:00','10:30:00','10:59:00'),('11:30','midday','11:00:00','11:29:00','11:30:00','11:59:00'),('13:00','midday','12:30:00','12:59:00','13:00:00','13:29:00'),('14:30','closing','14:00:00','14:29:00','14:30:00','14:59:00'),('15:30','closing','15:00:00','15:29:00','15:30:00','15:59:00')]
NEED={t for _,_,a,b,c,d in CHECKS for t in (a,b,c,d)}
cols=['ticker','session_date','checkpoint_et','session_group','lookback_return_pct','forward_return_pct','signed_forward_return_pct','signal','continuation','reversal','volume_eligible']
events=[];counts=collections.Counter()
with zipfile.ZipFile(SRC) as outer:
 for ticker in ['SPY','QQQ']:
  raw=outer.read(f'intraday_research_v3/{ticker}_research_bars_v3.zip')
  with zipfile.ZipFile(io.BytesIO(raw)) as inner:
   with inner.open(f'{ticker}_regular_session_bars.csv') as stream:
    reader=csv.DictReader(io.TextIOWrapper(stream))
    day=None;bars={};n=0;valid=True;vol=True
    def flush():
     if day is None:return
     counts[(ticker,'read')]+=1
     if n!=390 or not valid: counts[(ticker,'skipped')]+=1;return
     counts[(ticker,'eligible')]+=1
     for ck,grp,a,b,c,d in CHECKS:
      if any(t not in bars for t in (a,b,c,d)):raise ValueError((ticker,day,'missing',ck))
      aa,bb,cc,dd=[bars[t] for t in (a,b,c,d)]
      prev=100*(float(bb['close'])/float(aa['close'])-1)
      forward=100*(float(dd['close'])/float(cc['open'])-1)
      direction=1 if prev>=0.3 else -1 if prev<=-0.3 else 0
      signed=direction*forward if direction else None
      events.append(dict(ticker=ticker,session_date=day,checkpoint_et=ck,session_group=grp,lookback_return_pct=f'{prev:.8f}',forward_return_pct=f'{forward:.8f}',signed_forward_return_pct=f'{signed:.8f}' if signed is not None else '',signal='up' if direction==1 else 'down' if direction==-1 else 'neutral',continuation=int(signed>0) if direction else '',reversal=int(signed<0) if direction else '',volume_eligible=int(vol)))
    for row in reader:
     date=row['timestamp_et'][:10]
     if not '2024-01-01'<=date<='2026-09-30':continue
     if date!=day:
      flush();day=date;bars={};n=0;valid=True;vol=True
     n+=1;valid &= row['price_eligible']=='1';vol &= row['volume_eligible']=='1'
     t=row['timestamp_et'][11:]
     if t in NEED:bars[t]=row
    flush()
  print(ticker,dict((key[1],v) for key,v in counts.items() if key[0]==ticker),flush=True)
events.sort(key=lambda r:(r['ticker'],r['session_date'],r['checkpoint_et']))
with (OUT/'R01_Holdout_Events_v1.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(events)
def summarize(xs):
 n=len(xs)
 if not n:return dict(signal_count=0)
 pos=sum(x>0 for x in xs);neg=sum(x<0 for x in xs);nonflat=pos+neg
 p=binomtest(pos,nonflat,0.5,alternative='two-sided').pvalue if nonflat else None
 low,high=proportion_confint(pos,nonflat,alpha=.05,method='wilson') if nonflat else (None,None)
 ttest=ttest_1samp(xs,0).pvalue if n>1 else None
 return dict(signal_count=n,continuation_count=pos,reversal_count=neg,flat_count=n-nonflat,continuation_pct=round(pos/n*100,4),continuation_nonflat_pct=round(pos/nonflat*100,4) if nonflat else None,avg_signed_forward_pct=round(statistics.mean(xs),7),median_signed_forward_pct=round(statistics.median(xs),7),avg_continuation_pct=round(statistics.mean(x for x in xs if x>0),7) if pos else None,avg_reversal_pct=round(statistics.mean(x for x in xs if x<0),7) if neg else None,binomial_p_two_sided=round(p,7) if p is not None else None,continuation_ci95_low_pct=round(low*100,4) if low is not None else None,continuation_ci95_high_pct=round(high*100,4) if high is not None else None,mean_p_two_sided=round(ttest,7) if ttest is not None else None)
summary=[];annual=[]
for ticker in ('SPY','QQQ'):
 for ck,group,*_ in CHECKS:
  subset=[e for e in events if e['ticker']==ticker and e['checkpoint_et']==ck and e['signal']!='neutral']
  summary.append(dict(ticker=ticker,checkpoint_et=ck,session_group=group,**summarize([float(e['signed_forward_return_pct']) for e in subset])))
  for year in (2024,2025,2026):
   vals=[float(e['signed_forward_return_pct']) for e in subset if e['session_date'].startswith(str(year))]
   annual.append(dict(ticker=ticker,year=year,checkpoint_et=ck,session_group=group,**summarize(vals)))
for name,rows in [('R01_Holdout_Summary_v1.csv',summary),('R01_Holdout_Annual_v1.csv',annual)]:
 with (OUT/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('main results')
for r in summary:
 print(r['ticker'],r['checkpoint_et'],r['signal_count'],r['continuation_pct'],r['avg_signed_forward_pct'],r['binomial_p_two_sided'],r['mean_p_two_sided'])

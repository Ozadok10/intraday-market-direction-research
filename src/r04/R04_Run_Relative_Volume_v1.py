import os
import csv, zipfile, io, math, statistics
from collections import defaultdict, deque
from pathlib import Path
from scipy.stats import binomtest
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve(); OUT=ROOT/'R04_Relative_Volume_v1'; OUT.mkdir(exist_ok=True)
CHECKS={'10:00':(570,600),'10:30':(600,630),'11:30':(660,690),'13:00':(750,780),'14:30':(840,870),'15:30':(900,930)}
lookup=defaultdict(dict)
with (ROOT/'R01_Six_Checkpoint_Study_v1/R01_Six_Checkpoint_Events_v1.csv').open() as f:
 for x in csv.DictReader(f):
  if x['signal']!='neutral' and x['volume_eligible']=='1':lookup[x['ticker']][(x['session_date'],x['checkpoint_et'])]=x
results=[]
outer=zipfile.ZipFile(ROOT/'Intraday_Research_Eligibility_v3(1).zip')
for ticker in ('SPY','QQQ'):
 inner=zipfile.ZipFile(io.BytesIO(outer.read(f'intraday_research_v3/{ticker}_research_bars_v3.zip')))
 daily={}
 curr_date=None; minvol={}; good=True; minutes=0
 def flush():
  if curr_date is None or curr_date<'2008-01-01' or curr_date>'2019-12-31':return
  if not good or minutes!=390:return
  if all(all(m in minvol for m in range(a,b)) for a,b in CHECKS.values()):
   daily[curr_date]={ck:sum(minvol[m] for m in range(a,b)) for ck,(a,b) in CHECKS.items()}
 with inner.open(f'{ticker}_regular_session_bars.csv') as fp:
  for x in csv.DictReader(io.TextIOWrapper(fp)):
   d=x['timestamp_et'][:10]
   if d!=curr_date:
    flush();curr_date=d;minvol={};good=True;minutes=0
   if d<'2008-01-01' or d>'2019-12-31':continue
   minutes+=1
   if x['volume_eligible']!='1' or x['price_eligible']!='1':good=False
   t=x['timestamp_et'][11:];m=int(t[:2])*60+int(t[3:5]);minvol[m]=float(x['volume'])
  flush()
 history={ck:deque(maxlen=20) for ck in CHECKS}
 for d,volumes in sorted(daily.items()):
  for ck,vol in volumes.items():
   h=history[ck];e=lookup[ticker].get((d,ck))
   if e and len(h)==20:
    base=sum(h)/20
    if base>0:
     rvol=vol/base;band='low' if rvol<.75 else ('normal' if rvol<1.25 else 'high')
     results.append(dict(ticker=ticker,session_date=d,checkpoint_et=ck,signal=e['signal'],lookback_return_pct=e['lookback_return_pct'],prior_30m_volume=vol,prior_20_session_avg_volume=round(base,3),relative_volume_30m=round(rvol,6),volume_band=band,signed_forward_return_pct=e['signed_forward_return_pct'],continuation=e['continuation'],reversal=e['reversal']))
   h.append(vol)
 print(ticker,'eligible signals',len([x for x in results if x['ticker']==ticker]),'candidate',len(lookup[ticker]),flush=True)
cols=['ticker','session_date','checkpoint_et','signal','lookback_return_pct','prior_30m_volume','prior_20_session_avg_volume','relative_volume_30m','volume_band','signed_forward_return_pct','continuation','reversal']
with (OUT/'R04_Relative_Volume_Events_v1.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,cols);w.writeheader();w.writerows(results)
def summarize(checkpoint=False):
 groups=defaultdict(list)
 for r in results:groups[(r['ticker'],r['checkpoint_et'],r['volume_band']) if checkpoint else (r['ticker'],r['volume_band'])].append(r)
 res=[]
 for k,rs in sorted(groups.items()):
  vals=[float(r['signed_forward_return_pct']) for r in rs];con=sum(v>0 for v in vals);rev=sum(v<0 for v in vals);flat=len(rs)-con-rev
  row=dict(zip(['ticker','checkpoint_et','volume_band'] if checkpoint else ['ticker','volume_band'],k))
  row.update(signals=len(vals),continuations=con,reversions=rev,flats=flat,continuation_pct=round(100*con/(con+rev),2) if con+rev else '',mean_signed_forward_pct=round(statistics.mean(vals),6),median_signed_forward_pct=round(statistics.median(vals),6),binomial_p_unadjusted=round(binomtest(con,con+rev,.5).pvalue,6) if con+rev else '')
  res.append(row)
 return res
for fname,rows in [('R04_Relative_Volume_Overall_v1.csv',summarize()),('R04_Relative_Volume_By_Checkpoint_v1.csv',summarize(True))]:
 with (OUT/fname).open('w',newline='') as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('SUMMARY');[print(r) for r in summarize()]
(OUT/'R04_Relative_Volume_Methodology_v1.md').write_text('''# R04 Test 2: Relative Volume — discovery 2008–2019\n\nSix R01 checkpoints and ±0.30% last-30-minute move rule unchanged. Only original discovery period.\n\nFor each checkpoint, compute total share volume in the 30 fully elapsed minutes before the checkpoint. Divide it by the arithmetic average volume of the *same 30-minute clock window* over the preceding 20 full, volume-eligible trading sessions for the same ticker. No current day's later data included. First 20 eligible sessions used for warm-up. Exclude volume-ineligible and non-390-minute sessions. Prior valid sessions (not strictly the immediately prior 20 calendar sessions) are the reference.\n\nPredefined bands: low <0.75; normal >=0.75 and <1.25; high >=1.25. Bands exploratory, not optimized. Probability denominator excludes flat forward outcomes. Two-sided exact binomial p-values compare continuation to 50% and are unadjusted; they do NOT test band-to-band differences, which require separate analyses and correction for selection. Multiple comparisons and ETF/day correlations apply. Market behavior only, no trading strategy.\n\nFlat SQL-ready event table, pooled group results, checkpoint group results, and reproducible script. Save package to 03_Research/R04_Indicators. Does not replace earlier files.\n''')
(OUT/'R04_Run_Relative_Volume_v1.py').write_text(Path(__file__).read_text())
with zipfile.ZipFile(ROOT/'R04_Relative_Volume_v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.iterdir()):z.write(p,p.name)

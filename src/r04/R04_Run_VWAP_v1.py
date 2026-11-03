import os
import csv, io, zipfile, math
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import binomtest
ROOT=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve(); OUT=ROOT/'R04_VWAP_Analysis_v1';OUT.mkdir(exist_ok=True)
STUDY=ROOT/'R01_Six_Checkpoint_Study_v1/R01_Six_Checkpoint_Events_v1.csv'
CHECKS={'10:00':'09:59:00','10:30':'10:29:00','11:30':'11:29:00','13:00':'12:59:00','14:30':'14:29:00','15:30':'15:29:00'}
by_ticker=defaultdict(dict)
with STUDY.open() as fh:
 for e in csv.DictReader(fh):
  if e['signal']=='neutral' or e['volume_eligible']!='1':continue
  by_ticker[e['ticker']][(e['session_date'],e['checkpoint_et'])]=e
outrows=[]
outer=zipfile.ZipFile(ROOT/'Intraday_Research_Eligibility_v3(1).zip')
for ticker in ('SPY','QQQ'):
 inner=zipfile.ZipFile(io.BytesIO(outer.read(f'intraday_research_v3/{ticker}_research_bars_v3.zip')))
 with inner.open(f'{ticker}_regular_session_bars.csv') as raw:
  reader=csv.DictReader(io.TextIOWrapper(raw,encoding='utf-8'))
  prevday=None; pv=vv=0.0; day_valid=True
  for bar in reader:
   dt=bar['timestamp_et'][:10]
   if dt<'2008-01-01':continue
   if dt>'2019-12-31':continue
   tm=bar['timestamp_et'][11:]
   if dt!=prevday:pv=vv=0.;prevday=dt;day_valid=True
   if bar['volume_eligible']!='1':day_valid=False
   vol=float(bar['volume'])
   pv+=((float(bar['high'])+float(bar['low'])+float(bar['close']))/3)*vol
   vv+=vol
   if tm not in CHECKS.values():continue
   checkpoint=next((k for k,v in CHECKS.items() if v==tm),None)
   event=by_ticker[ticker].get((dt,checkpoint))
   if not event or not day_valid or vv<=0:continue
   vwap=pv/vv; last_close=float(bar['close'])
   direction=1 if event['signal']=='up' else -1
   signed_distance_pct=direction*(last_close/vwap-1)*100
   band='behind_vwap' if signed_distance_pct<-.15 else ('near_vwap' if signed_distance_pct<.15 else 'extended_from_vwap')
   outrows.append({'ticker':ticker,'session_date':dt,'checkpoint_et':checkpoint,'signal':event['signal'],
     'lookback_return_pct':event['lookback_return_pct'],'vwap_at_checkpoint':round(vwap,6),
     'checkpoint_previous_close':last_close,'signed_vwap_distance_pct':round(signed_distance_pct,7),
     'vwap_position_band':band,'signed_forward_return_pct':event['signed_forward_return_pct'],
     'continuation':event['continuation'],'reversal':event['reversal']})
 print(ticker,'included',sum(x['ticker']==ticker for x in outrows),'of eligible events',len(by_ticker[ticker]),flush=True)
fields=list(outrows[0]);events=OUT/'R04_VWAP_Events_v1.csv'
with events.open('w',newline='') as f:
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows(outrows)

def summary(rows, checkpoint=False):
 groups=defaultdict(list)
 for e in rows:
  key=(e['ticker'],e['checkpoint_et'],e['vwap_position_band']) if checkpoint else (e['ticker'],e['vwap_position_band'])
  groups[key].append(e)
 result=[]
 for key,rs in sorted(groups.items()):
  signed=np.array([float(r['signed_forward_return_pct']) for r in rs]); cont=int((signed>0).sum());rev=int((signed<0).sum());flat=int((signed==0).sum());n=cont+rev
  entry=dict(zip(['ticker','checkpoint_et','vwap_position_band'] if checkpoint else ['ticker','vwap_position_band'],key))
  entry.update({'signals':len(rs),'continuations':cont,'reversions':rev,'flat':flat,
   'continuation_pct':round(cont/n*100,3) if n else '',
   'mean_signed_forward_pct':round(float(signed.mean()),6),
   'median_signed_forward_pct':round(float(np.median(signed)),6),
   'binomial_p_unadjusted':round(binomtest(cont,n,0.5).pvalue,6) if n else ''})
  result.append(entry)
 return result
for name, rows in [('R04_VWAP_Overall_v1.csv',summary(outrows)),('R04_VWAP_By_Checkpoint_v1.csv',summary(outrows,True))]:
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('SUMMARY:')
for x in summary(outrows): print(x)
readme='''# R04 — VWAP Distance: Discovery Study v1

Market-behavior research, not a trading strategy. Uses frozen v3 inputs and existing six-checkpoint R01 discovery events, 2008–2019 only. The 2020–2023 validation and 2024–2026 holdout were not examined for VWAP relationships.

## Definition
For each checkpoint, construct regular-session VWAP from 9:30 through the PREVIOUS complete minute bar (e.g., through 09:59 for 10:00), using sum((high+low+close)/3 * volume) / sum(volume). This is an OHLCV typical-price VWAP proxy, NOT trade-tick actual VWAP. Distance uses previous-minute close: 100*(previous close/VWAP -1) multiplied by +1 for preceding upward price move and -1 for preceding downward move. This signed relative distance measures whether current price lies along the prior directional move, not an unsigned distance.

Pre-set bands: `behind_vwap` when signed distance <-0.15 percentage points; `near_vwap` from -0.15 inclusive to +0.15 exclusive; `extended_from_vwap` at +0.15 or more. These are exploratory fixed illustrative cutoffs, not optimized parameters or established significance thresholds. All qualifying signals have abs(previous 30m return)>=0.30%. Same existing next-30-minute outcome definitions; flat outcomes excluded only from probability denominator.

Use ONLY volume-eligible sessions, as marked in v3. Do not invent missing data. Fixed band results and all unadjusted binomial tests are exploratory; numerous checkpoint/band comparisons, ETF correlation, and within-session dependence mean p-values should not be interpreted as confirmatory. The analysis does not establish causation or a forecast. The existing v3 price-only baseline includes some additional volume-ineligible sessions; use matched eligible-only baselines when comparing VWAP groups.

## Files
- `R04_VWAP_Events_v1.csv`: flat, one row per signal, SQL-friendly keys ticker/session_date/checkpoint_et.
- `R04_VWAP_Overall_v1.csv`: one row per ticker and VWAP band, pooled across six checkpoints.
- `R04_VWAP_By_Checkpoint_v1.csv`: one row per ticker, checkpoint, VWAP band.
- `R04_Run_VWAP_v1.py`: reproducible source.

Save to `03_Research/R04_Indicators/`. Replaces none of the earlier phases.
'''
(OUT/'R04_VWAP_Methodology_v1.md').write_text(readme)
(OUT/'R04_Run_VWAP_v1.py').write_text(Path(__file__).read_text())
with zipfile.ZipFile(ROOT/'R04_VWAP_Analysis_v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for file in OUT.iterdir():z.write(file,file.name)

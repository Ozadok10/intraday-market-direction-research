import os
import zipfile, io, csv, collections, math, statistics, pathlib, json
ROOT=pathlib.Path(os.environ.get('INTRADAY_WORKDIR', pathlib.Path.cwd())).expanduser().resolve(); SRC=ROOT/'Intraday_Research_Eligibility_v3(1).zip'; OUT=ROOT/'R01_Out_Of_Sample_2020_2023_v1';OUT.mkdir(exist_ok=True)
CHECKS=[('10:00','opening','09:30:00','09:59:00','10:00:00','10:29:00'),('10:30','opening','10:00:00','10:29:00','10:30:00','10:59:00'),('11:30','midday','11:00:00','11:29:00','11:30:00','11:59:00'),('13:00','midday','12:30:00','12:59:00','13:00:00','13:29:00'),('14:30','closing','14:00:00','14:29:00','14:30:00','14:59:00'),('15:30','closing','15:00:00','15:29:00','15:30:00','15:59:00')]
NEED={t for _,_,a,b,c,d in CHECKS for t in (a,b,c,d)}
cols=['ticker','session_date','checkpoint_et','session_group','lookback_return_pct','forward_return_pct','signed_forward_return_pct','signal','continuation','reversal','volume_eligible']
events=[]; eligible_days=collections.Counter(); skip=collections.Counter(); observed=collections.Counter()
with zipfile.ZipFile(SRC) as outer:
 for ticker in ('SPY','QQQ'):
  raw=outer.read(f'intraday_research_v3/{ticker}_research_bars_v3.zip')
  with zipfile.ZipFile(io.BytesIO(raw)) as inner:
   with inner.open(f'{ticker}_regular_session_bars.csv') as fp:
    reader=csv.DictReader(io.TextIOWrapper(fp))
    curr=None; bars={};n=0;good=True;vgood=True
    def flush():
     if curr is None:return
     observed[ticker]+=1
     if n!=390 or not good: skip[(ticker,'bad_session')]+=1; return
     eligible_days[ticker]+=1
     for ck,group,a,b,c,d in CHECKS:
      if not all(k in bars for k in (a,b,c,d)):skip[(ticker,'missing_ckpt')]+=1;continue
      aa,bb,cc,dd=[bars[k] for k in (a,b,c,d)]
      back=100*(float(bb['close'])/float(aa['close'])-1)
      future=100*(float(dd['close'])/float(cc['open'])-1)
      direction=1 if back>=0.30 else -1 if back<=-0.30 else 0
      signed=direction*future if direction else None
      events.append(dict(ticker=ticker,session_date=curr,checkpoint_et=ck,session_group=group,lookback_return_pct=f'{back:.8f}',forward_return_pct=f'{future:.8f}',signed_forward_return_pct=f'{signed:.8f}' if signed is not None else '',signal=('up' if direction==1 else 'down' if direction==-1 else 'neutral'),continuation=int(signed>0) if direction else '',reversal=int(signed<0) if direction else '',volume_eligible=int(vgood)))
    for row in reader:
     date=row['timestamp_et'][:10]
     if not '2020-01-01'<=date<='2023-12-31':continue
     if date!=curr:
      flush();curr=date;bars={};n=0;good=True;vgood=True
     n+=1;good=good and row['price_eligible']=='1';vgood=vgood and row['volume_eligible']=='1'
     t=row['timestamp_et'][11:]
     if t in NEED:bars[t]=row
    flush()
  print(ticker,'sessions read',observed[ticker],'eligible',eligible_days[ticker],'skips',dict(skip),flush=True)
events.sort(key=lambda x:(x['ticker'],x['session_date'],x['checkpoint_et']))
with (OUT/'R01_OOS_Events_v1.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(events)
def calc(xs):
 n=len(xs)
 if not n:return None
 pos=[x for x in xs if x>0];neg=[x for x in xs if x<0]; flat=n-len(pos)-len(neg)
 return {'signal_count':n,'avg_signed_forward_pct':statistics.mean(xs),'continuation_pct':len(pos)/n*100,'reversal_pct':len(neg)/n*100,'flat_pct':flat/n*100,'avg_continuation_pct':statistics.mean(pos) if pos else None,'avg_reversal_pct':statistics.mean(neg) if neg else None,'median_signed_forward_pct':statistics.median(xs)}
rows=[]
for ticker in ('SPY','QQQ'):
 for ck,group,*_ in CHECKS:
  xs=[float(e['signed_forward_return_pct']) for e in events if e['ticker']==ticker and e['checkpoint_et']==ck and e['signal']!='neutral']
  rows.append(dict(ticker=ticker,checkpoint_et=ck,session_group=group,**calc(xs)))
cols2=['ticker','checkpoint_et','session_group','signal_count','avg_signed_forward_pct','continuation_pct','reversal_pct','flat_pct','avg_continuation_pct','avg_reversal_pct','median_signed_forward_pct']
with (OUT/'R01_OOS_Summary_v1.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols2);w.writeheader();w.writerows(rows)
yr=[]
for ticker in ('SPY','QQQ'):
 for year in range(2020,2024):
  for ck,group,*_ in CHECKS:
   xs=[float(e['signed_forward_return_pct']) for e in events if e['ticker']==ticker and e['session_date'].startswith(str(year)) and e['checkpoint_et']==ck and e['signal']!='neutral']
   if xs:yr.append(dict(ticker=ticker,year=year,checkpoint_et=ck,session_group=group,**calc(xs)))
with (OUT/'R01_OOS_Annual_v1.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['ticker','year']+cols2[1:]);w.writeheader();w.writerows(yr)
(OUT/'R01_OOS_Methodology_v1.md').write_text('''# R01 — 2020–2023 out-of-sample validation (v1)\n\nSource: Intraday_Research_Eligibility_v3(1).zip. SPY and QQQ eligible full 390-minute sessions; price_eligible=1. No interpolation. Volume-ineligible sessions are retained for price-only tests.\n\nSix checkpoint times ET: 10:00, 10:30, 11:30, 13:00, 14:30, 15:30. At each: previous 30-minute close-to-close proxy = close of checkpoint-1 minute / close of checkpoint-31 minute - 1; signed move trigger >= +0.30% or <= -0.30%. Forward window = close of checkpoint+29 minute / open at checkpoint - 1. Signed forward = forward return times original signal direction. Positive is momentum continuation, negative is mean reversion. Observations classified neutral stay in events, but not in directional summary.\n\nNo performance or profitability inference is intended. Six checkpoints overlap in informational context even though their forward windows do not overlap. This OOS period must not be used to tune checkpoint choices or threshold. The 2024–2026 holdout remains untouched.\n\nCSV files are flat, one observation per row. This version adds validation data; it does not replace earlier discovery research or vendor ZIP.\n''')
print('EVENTS',len(events),'signals',sum(e['signal']!='neutral' for e in events));
for r in rows:print(r)

import os
from pathlib import Path
import zipfile, io, csv, collections, statistics, math, json, textwrap
base=Path(os.environ.get('INTRADAY_WORKDIR', Path.cwd())).expanduser().resolve()
out=base/"R01_Six_Checkpoint_Study_v1"
out.mkdir(exist_ok=True)
source=base/"Intraday_Research_Eligibility_v3.zip"
times={"10:00":("09:30:00","09:59:00","10:00:00","10:29:00","opening"),
       "10:30":("10:00:00","10:29:00","10:30:00","10:59:00","opening"),
       "11:30":("11:00:00","11:29:00","11:30:00","11:59:00","midday"),
       "13:00":("12:30:00","12:59:00","13:00:00","13:29:00","midday"),
       "14:30":("14:00:00","14:29:00","14:30:00","14:59:00","closing"),
       "15:30":("15:00:00","15:29:00","15:30:00","15:59:00","closing")}
keep={v for item in times.values() for v in item[:4]}
fields=["ticker","session_date","checkpoint_et","session_group","sample_period","lookback_return_pct","forward_return_pct","signed_forward_return_pct","signal","continuation","reversal","entry_open","exit_close","volume_eligible"]
allobs=collections.defaultdict(list)
annual=collections.defaultdict(list)
processed=collections.Counter()
with zipfile.ZipFile(source) as outer, (out/"R01_Six_Checkpoint_Events_v1.csv").open("w",newline="") as outfile:
    writer=csv.DictWriter(outfile,fieldnames=fields);writer.writeheader()
    for ticker in ("SPY","QQQ"):
        payload=outer.read(f"intraday_research_v3/{ticker}_research_bars_v3.zip")
        with zipfile.ZipFile(io.BytesIO(payload)) as inner:
            with inner.open(f"{ticker}_regular_session_bars.csv") as stream:
                reader=csv.DictReader(io.TextIOWrapper(stream,encoding="utf-8"))
                date=None; rows={}; n=0; eligible=True; vol_ok=True
                def flush():
                    if date is None or n!=390 or not eligible: return
                    processed[(ticker,"days")]+=1
                    for ck,(a,b,c,d,group) in times.items():
                        if not all(k in rows for k in (a,b,c,d)):
                            processed[(ticker,"missing")]+=1;continue
                        A,B,C,D=[rows[k] for k in (a,b,c,d)]
                        back=float(B["close"])/float(A["close"])-1
                        fwd=float(D["close"])/float(C["open"])-1
                        sig=1 if back>=0.003 else -1 if back<=-0.003 else 0
                        signed=sig*fwd*100 if sig else None
                        s="up" if sig==1 else "down" if sig==-1 else "neutral"
                        result={"ticker":ticker,"session_date":date,"checkpoint_et":ck,"session_group":group,
                                "sample_period":"discovery_2008_2019","lookback_return_pct":round(back*100,7),
                                "forward_return_pct":round(fwd*100,7),"signed_forward_return_pct":round(signed,7) if sig else "",
                                "signal":s,"continuation":int(signed>0) if sig else "", "reversal":int(signed<0) if sig else "",
                                "entry_open":C["open"],"exit_close":D["close"],"volume_eligible":int(vol_ok)}
                        writer.writerow(result)
                        processed[(ticker,"all")]+=1
                        if sig:
                            for k in [(ticker,ck,"combined"),(ticker,ck,s),(ticker,group,"combined"),(ticker,"ALL","combined")]:
                                allobs[k].append(signed)
                            annual[(ticker,date[:4],group)].append(signed)
                            processed[(ticker,"signals")]+=1
                for row in reader:
                    d=row["timestamp_et"][:10]
                    if d<"2008-01-01" or d>"2019-12-31": continue
                    if d!=date:
                        flush();date=d;rows={};n=0;eligible=True;vol_ok=True
                    n+=1;eligible &= row["price_eligible"]=="1";vol_ok &= row["volume_eligible"]=="1"
                    hh=row["timestamp_et"][11:]
                    if hh in keep:rows[hh]=row
                flush()
        print(ticker, "days",processed[(ticker,"days")],"checkpoints",processed[(ticker,"all")],"signals",processed[(ticker,"signals")])
def summarize(vals):
    n=len(vals)
    return [n,round(statistics.mean(vals),6),round(statistics.median(vals),6),
            round(100*sum(x>0 for x in vals)/n,3),round(100*sum(x<0 for x in vals)/n,3),
            round(100*sum(x==0 for x in vals)/n,3),
            round(statistics.stdev(vals)/math.sqrt(n),6) if n>1 else ""]
sf=["ticker","checkpoint_or_group","signal_group","event_count","mean_signed_forward_pct","median_signed_forward_pct","continuation_pct","reversal_pct","flat_pct","naive_standard_error_pct"]
with (out/"R01_Six_Checkpoint_Summary_v1.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(sf)
    for k,v in sorted(allobs.items()):w.writerow(list(k)+summarize(v))
with (out/"R01_Six_Checkpoint_Annual_v1.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["ticker","year","session_group"]+sf[3:])
    for k,v in sorted(annual.items()):w.writerow(list(k)+summarize(v))
print("SUMMARY")
for k,v in sorted(allobs.items()):
    if k[2]=="combined" and k[1] in times:
        print(k, summarize(v)[:5])
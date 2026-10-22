import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import re
from bs4 import BeautifulSoup
import pandas as pd, numpy as np
D=RAW
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def num(x):
    if '–' in x.split(' ')[0]: return np.nan
    m=re.match(r'^\s*([\d.]+)',x); return float(m.group(1)) if m else np.nan
def endd(s,yr_default):
    s=s.split('–')[-1].strip(); m=re.match(r'(\d+)\s+([A-Z][a-z]{2})(?:\s+(\d{4}))?',s)
    if not m: return None
    return (int(m.group(1)),MON[m.group(2)],int(m.group(3)) if m.group(3) else None)
E={'op_2023.html':('2023-07-23',{'R':['PP','Vox'],'L':['PSOE','Sumar']},{'PP':33.1,'Vox':12.4,'PSOE':31.7,'Sumar':12.3}),
   'op_November_2019.html':('2019-11-10',{'R':['PP','Vox','Cs'],'L':['PSOE','Unidas Podemos','Más País']},{'PP':20.8,'Vox':15.1,'Cs':6.8,'PSOE':28.0,'Unidas Podemos':12.9,'Más País':2.4}),
   'op_April_2019.html':('2019-04-28',{'R':['PP','Vox','Cs'],'L':['PSOE','Unidas Podemos']},{'PP':16.7,'Vox':10.3,'Cs':15.9,'PSOE':28.7,'Unidas Podemos':14.3}),
   'op_2016.html':('2016-06-26',{'R':['PP',"C's"],'L':['PSOE','Unidos Podemos']},{'PP':33.0,"C's":13.1,'PSOE':22.6,'Unidos Podemos':21.2})}
H=[3,7,14,21,30,45,60,90,120]
res=[]
for fn,(ed,bl,rr) in E.items():
    ed=pd.Timestamp(ed); soup=BeautifulSoup(open(D+fn).read(),'lxml')
    rows=[]
    for tb in soup.find_all('table',class_='wikitable')[:6]:
        hdr=[]
        for th in tb.find_all('tr')[0].find_all(['th','td']):
            a=th.find('a'); name=(a.get('title') if a else th.get_text(' ',strip=True))
            for _ in range(int(th.get('colspan',1))): hdr.append(name)
        if 'Fieldwork date' not in hdr or not all(p in hdr for p in rr): continue
        h0=tb.find_previous(['h2','h3']).get_text(strip=True)
        if 'Nationwide' not in h0 or 'Turnout' not in hdr: continue
        for tr in tb.find_all('tr')[1:]:
            txt=[]
            for td in tr.find_all(['td','th']):
                for _ in range(int(td.get('colspan',1))): txt.append(td.get_text(' ',strip=True))
            if len(txt)!=len(hdr): continue
            d=dict(zip(hdr,txt)); f=re.sub(r'\s*\[.*','',d[hdr[0]]).strip()
            if 'election' in f.lower() or f in('PSOE','PP','Podemos','Vox','Cs','CIS (Tezanos)'): continue
            e=endd(d['Fieldwork date'],None)
            if not e: continue
            day,mo,yr=e
            if yr is None: yr=ed.year if mo<=ed.month else ed.year-1
            dt=pd.Timestamp(yr,mo,day)
            if dt>ed: dt=pd.Timestamp(yr-1,mo,day)
            vals={p:num(d.get(p,'')) for p in bl['R']+bl['L']}
            rows.append(dict(firm=f,dt=dt,**vals))
    df=pd.DataFrame(rows).drop_duplicates()
    for h in H:
        c=ed-pd.Timedelta(days=h); w=df[(df.dt<=c)&(df.dt>c-pd.Timedelta(days=10))].sort_values('dt',ascending=False).drop_duplicates('firm')
        if len(w)<3: continue
        avg={p:w[p].mean() for p in rr}
        eR=sum(avg[p]-rr[p] for p in bl['R']); eL=sum(avg[p]-rr[p] for p in bl['L'])
        mae=np.mean([abs(avg[p]-rr[p]) for p in rr])
        res.append(dict(elec=fn[3:-5],h=h,n=len(w),eR=round(eR,2),eL=round(eL,2),mae=round(mae,2)))
R=pd.DataFrame(res); print(R.pivot(index='h',columns='elec',values='eR')); print(R.pivot(index='h',columns='elec',values='mae'))
S=R.groupby('h').agg(rmsR=('eR',lambda x: np.sqrt((x**2).mean())),rmsL=('eL',lambda x: np.sqrt((x**2).mean())),mae=('mae','mean'),k=('eR','size'))
print(S.round(2))
R.to_csv(os.path.join(ROOT,'data','hist_horizon.csv'),index=False)

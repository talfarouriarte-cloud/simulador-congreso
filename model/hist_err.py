import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import re,sys
from bs4 import BeautifulSoup
import pandas as pd, numpy as np
D=RAW
def parse(fn):
    soup=BeautifulSoup(open(D+fn).read(),'lxml'); tb=soup.find_all('table',class_='wikitable')[0]
    hdr=[]
    for th in tb.find_all('tr')[0].find_all(['th','td']):
        a=th.find('a'); name=(a.get('title') if a else th.get_text(' ',strip=True))
        for _ in range(int(th.get('colspan',1))): hdr.append(name)
    rows=[]
    for tr in tb.find_all('tr')[1:]:
        txt=[]
        for td in tr.find_all(['td','th']):
            for _ in range(int(td.get('colspan',1))): txt.append(td.get_text(' ',strip=True))
        if len(txt)==len(hdr): rows.append(txt)
    return hdr,rows
for fn in ['op_2023.html','op_November_2019.html','op_April_2019.html','op_2016.html']:
    h,r=parse(fn); print(fn,h); 
    for x in r[:12]: print('   ',[y[:16] for y in x])

MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def endd(s,yr):
    s=s.split('–')[-1].strip(); m=re.match(r'(\d+)\s+([A-Z][a-z]{2})',s)
    return pd.Timestamp(yr,MON[m.group(2)],int(m.group(1))) if m else None
def num(x):
    m=re.match(r'^\s*([\d.]+)(?!\S*–)',x); 
    if '–' in x.split(' ')[0]: return None
    return float(m.group(1)) if m else None
E={'op_2023.html':(2023,'2023-07-23',{'R':['PP','Vox'],'L':['PSOE','Sumar']}),
   'op_November_2019.html':(2019,'2019-11-10',{'R':['PP','Vox','Cs'],'L':['PSOE','Unidas Podemos','Más País']}),
   'op_April_2019.html':(2019,'2019-04-28',{'R':['PP','Vox','Cs'],'L':['PSOE','Unidas Podemos']}),
   'op_2016.html':(2016,'2016-06-26',{'R':['PP',"C's"],'L':['PSOE','Unidos Podemos']})}
print('\n=== errores (encuesta - resultado), últimos 14 días, una por empresa ===')
out=[]
for fn,(yr,ed,bl) in E.items():
    h,r=parse(fn); ed=pd.Timestamp(ed)
    res=None; polls=[]
    for x in r:
        d=dict(zip(h,x))
        if 'election' in d[h[0]].lower() or 'general ele' in d[h[0]]:
            if res is None: res=d
            continue
        firm=re.sub(r'\s*\[.*','',d[h[0]]).strip()
        if firm in('PSOE','PP','Podemos','Vox','Cs') : continue
        dt=endd(d['Fieldwork date'],yr)
        if dt is None or dt<ed-pd.Timedelta(days=14) or dt>ed: continue
        polls.append((firm,dt,d))
    seen=set(); P=[]
    for f,dt,d in polls:
        if f in seen: continue
        seen.add(f); P.append(d)
    parties=bl['R']+bl['L']
    avg={p:np.nanmean([num(d[p]) if num(d[p]) is not None else np.nan for d in P]) for p in parties}
    rr={p:num(res[p]) for p in parties}
    if None in rr.values(): print('RES',fn,{p:res[p] for p in parties})
    e={p:round(avg[p]-rr[p],2) for p in parties}
    eR=sum(avg[p] for p in bl['R'])-sum(rr[p] for p in bl['R']); eL=sum(avg[p] for p in bl['L'])-sum(rr[p] for p in bl['L'])
    print(fn,len(P),'polls',e,'| bloque dcha',round(eR,2),'izda',round(eL,2))
    out.append((eR,eL,e))
R=np.array([o[0] for o in out]); L=np.array([o[1] for o in out])
print('RMS dcha',np.sqrt((R**2).mean()).round(2),'RMS izda',np.sqrt((L**2).mean()).round(2),'corr',np.corrcoef(R,L)[0,1].round(2))
allp=[v for o in out for v in o[2].values()]; print('RMS por partido',np.sqrt(np.mean(np.square(allp))).round(2))

import pandas as pd, re, sys
from bs4 import BeautifulSoup
s=open(sys.argv[1]).read()
soup=BeautifulSoup(s,'lxml')
T=soup.find_all('table',class_='wikitable')
C0=['firm','date','n','turnout','PP','PSOE','Vox','FA','FV','ERC','Junts','EH Bildu','PNV','BNG','CC','AA','Podemos','SALF','lead']
C1=['firm','date','n','turnout','PP','PSOE','Vox','Sumar','ERC','Junts','EH Bildu','PNV','BNG','CC','UPN','AA','Podemos','SALF','AC','lead']
C2=['firm','date','n','turnout','PP','PSOE','Vox','Sumar','ERC','Junts','EH Bildu','PNV','BNG','CC','UPN','Podemos','SALF','AC','lead']
YEAR={0:2026,1:2026,2:2025}
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def enddate(x,yr=2026):
    x=x.split('–')[-1].split('-')[-1].strip()
    m=re.match(r'(\d+)\s+([A-Z][a-z]{2})',x)
    return pd.Timestamp(yr,MON[m.group(2)],int(m.group(1))) if m else pd.NaT
def first(x):
    m=re.match(r'^\s*([\d.]+)',str(x)); return float(m.group(1)) if m else None
def notefv(tr):
    t=tr.get_text(' ',strip=True)
    return None
rows=[]
for k,cols in ((0,C0),(1,C1),(2,C2)):
    for tr in T[k].find_all('tr')[1:]:
        txt=[];cid=[]
        for ci,td in enumerate(tr.find_all(['td','th'])):
            for _ in range(int(td.get('colspan',1))): txt.append(td.get_text(' ',strip=True)); cid.append(ci)
        if len(txt)!=len(cols): continue
        d=dict(zip(cols,txt)); d['table']=k
        # FA y Compromís en una sola celda (lista conjunta): FA lleva el total y FV queda vacío
        comb=k==0 and cid[cols.index('FA')]==cid[cols.index('FV')]
        if comb: d['FV']=''
        d['FAFV_comb']=comb
        for c in cols[4:-1]: d[c]=first(d[c])
        # nota Compromís separada dentro de Sumar
        m=re.search(r'Compromís , with ([\d.]+)%',' '.join(
            soup.find(id=a['href'].split('#')[-1]).get_text(' ',strip=True) for a in tr.select('sup a[href*=cite_note]') if soup.find(id=a['href'].split('#')[-1])))
        if m and k==1: d['FV_note']=float(m.group(1))
        rows.append(d)
df=pd.DataFrame(rows)
df['firm']=df.firm.str.replace(r'\s*\[.*?\]','',regex=True).str.strip()
df['end']=[enddate(d,YEAR[t]) for d,t in zip(df.date,df.table)]
df['n']=pd.to_numeric(df.n.str.replace(',',''),errors='coerce')
df.to_csv(sys.argv[2],index=False)
pd.set_option('display.width',260); pd.set_option('display.max_columns',30)
print(len(df)); print(df[df.end>='2026-08-20'].drop(columns=['turnout','lead','date']).to_string())

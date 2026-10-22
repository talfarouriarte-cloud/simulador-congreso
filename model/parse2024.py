import pandas as pd, re, sys
from io import StringIO
from bs4 import BeautifulSoup
s=open(sys.argv[1]).read()
soup=BeautifulSoup(s,'lxml')
out=[]
for tb in soup.find_all('table',class_='wikitable'):
    h=tb.find_previous(['h2','h3','h4'])
    cap=tb.find('caption')
    title=(cap.get_text(' ',strip=True) if cap else '')+' || '+(h.get_text(' ',strip=True) if h else '')
    try: t=pd.read_html(StringIO(str(tb)))[0]
    except Exception: continue
    if t.shape[1]!=5: continue
    t.columns=['a','party','votes','pct','pp']
    d={'title':title}
    for r in t.itertuples():
        p=str(r.party); v=pd.to_numeric(str(r.votes).replace(',',''),errors='coerce')
        if pd.isna(v): continue
        if re.search(r'\(SALF\)|Party is Over|Se Acab',p): k='SALF'
        elif re.search(r'Podemos|We Can',p) and 'Sumar' not in p: k='Podemos'
        elif 'Sumar' in p: k='Sumar'
        elif re.search(r"People's Party|\(PP\)",p): k='PP'
        elif re.search(r"PSOE|PSC|Socialist",p): k='PSOE'
        elif re.search(r"\(Vox\)",p): k='Vox'
        elif p.startswith('Blank'): k='blank'
        elif p.startswith('Valid'): k='valid'
        elif p in ('Total','Invalid votes','Votes cast / turnout','Abstentions','Registered voters'): continue
        else: k='Otros'
        d[k]=d.get(k,0)+v
    out.append(d)
df=pd.DataFrame(out).fillna(0)
df.to_csv(sys.argv[2],index=False)
pd.set_option('display.width',250)
print(df[['title','PP','PSOE','Vox','Sumar','Podemos','SALF','valid']].to_string())

import pandas as pd, glob, os, re, json, sys
D=sys.argv[1]
SEATS={}
def norm(p):
    p=str(p)
    rules=[('PP',r"People's Party|\(PP\)"),('PSOE',r"Socialist|PSOE|PSC|PSdeG|PSE"),('Vox',r"\(Vox\)"),
           ("Sumar",r"Sumar"),('ERC',r"\(ERC"),('Junts',r"Junts"),('EH Bildu',r"Bildu"),
           ('PNV',r"PNV"),('BNG',r"\(BNG\)"),('CC',r"\(CCa\)|Canarian Coalition"),('UPN',r"\(UPN\)")]
    for k,rx in rules:
        if re.search(rx,p): return k
    return 'Otros'
rows=[]
for f in sorted(glob.glob(D+'/*.html')):
    name=os.path.basename(f)[:-5]
    ts=pd.read_html(f)
    tab=None
    for t in ts:
        if t.shape[1]==7 and 'Parties and alliances' in str(t.columns[0]):
            txt=t.to_string()
            if 'Sumar' in txt and 'Total' in txt:
                tab=t;break
    t=tab; t.columns=['a','party','votes','pct','pp','seats','ds']
    d={'prov':name}
    for r in t.itertuples():
        p=str(r.party)
        if p=='nan' or p.startswith('Sources') or p.startswith('Footnotes'): continue
        v=pd.to_numeric(str(r.votes).replace(',',''),errors='coerce')
        if p.startswith('Blank'): d['blank']=v; continue
        if p=='Total': d['seats']=int(r.seats); d['valid_chk']=v; continue
        if p in('Valid votes','Invalid votes','Votes cast / turnout','Abstentions','Registered voters'):
            d[p]=v; continue
        k=norm(p); d[k]=d.get(k,0)+v
        s=pd.to_numeric(r.seats,errors='coerce')
        d['S_'+k]=d.get('S_'+k,0)+(0 if pd.isna(s) else int(s))
    rows.append(d)
df=pd.DataFrame(rows).fillna(0)
df.to_csv(sys.argv[2],index=False)
P=['PP','PSOE','Vox','Sumar','ERC','Junts','EH Bildu','PNV','BNG','CC','UPN']
print(df[['prov','seats']+P].to_string())
print('seats',df.seats.sum(), {p:int(df['S_'+p].sum()) for p in P if 'S_'+p in df})
print({p:int(df[p].sum()) for p in P}, 'valid',df['Valid votes'].sum(),'blank',df.blank.sum())

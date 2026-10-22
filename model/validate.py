import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import pandas as pd, numpy as np, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from engine import dhondt
df=pd.read_csv(os.path.join(ROOT,'data','base2023.csv'))
P=['PP','PSOE','Vox','Sumar','ERC','Junts','EH Bildu','PNV','BNG','CC','UPN']
bad=0; tot=dict.fromkeys(P,0)
for r in df.itertuples(index=False):
    d=r._asdict()
    v=[d.get(p.replace(' ','_'),0) for p in P]
    # namedtuple renames 'EH Bildu'
    v=[df.loc[df.prov==r.prov,p].iloc[0] for p in P]
    s=dhondt(v,int(r.seats),valid=df.loc[df.prov==r.prov,'Valid votes'].iloc[0])
    off=[int(df.loc[df.prov==r.prov,'S_'+p].iloc[0]) for p in P]
    for p,x in zip(P,s): tot[p]+=int(x)
    if list(s)!=off: bad+=1; print('MISMATCH',r.prov,dict(zip(P,s)),off)
print('provincias con discrepancia:',bad); print(tot)

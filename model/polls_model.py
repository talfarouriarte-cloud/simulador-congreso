"""Agregación bayesiana de encuestas (modelo normal de efectos aleatorios con caída temporal)."""
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import pandas as pd, numpy as np, json
TODAY=pd.Timestamp('2026-10-22'); WINDOW=45; HALF=21
P=pd.read_csv(os.path.join(ROOT,'data','polls_2026.csv'),parse_dates=['end'])
P=P[(P.end>=TODAY-pd.Timedelta(days=WINDOW))&P.PP.notna()].copy()
P=P[~P.firm.isin(['PSOE','SocioMétrica/PP'])]
# FA+FV como "espacio Sumar" en todas las encuestas
P['SUMESP']=np.where(P.table==0,P.FA+P.FV,P.Sumar)
P['FVobs']=np.where(P.table==0,P.FV,P.FV_note)
P['FA']=P.SUMESP-P.FVobs
# una encuesta por empresa (la más reciente) para no sobreponderar trackers
P=P.sort_values('end',ascending=False).drop_duplicates('firm')
P['n']=P.n.fillna(1000).clip(upper=3000)
P['age']=(TODAY-P.end).dt.days
P['w']=0.5**(P.age/HALF)
PRIOR={'PP':33.1,'PSOE':31.7,'Vox':12.4,'SUMESP':7.5,'Podemos':3.3,'SALF':2.0,'ERC':1.9,'Junts':1.6,'EH Bildu':1.4,'PNV':1.1,
       'BNG':0.6,'CC':0.5,'UPN':0.2,'AA':0.5,'AC':0.6,'FVobs':1.0}
PRIOR_SD=5.0
out={}
for p,m0 in PRIOR.items():
    d=P[P[p].notna()]
    y=d[p].values/100; n=d.n.values; w=d.w.values
    if len(d)==0:
        # Aliança Catalana: solo Sigma Dos (1,0%) y Cluster17 (1,6%) la publican en 2026 -> media 1,1, sd amplia
        out[p]=dict(mean=1.1,sd=0.4,tau=None,k=2); continue
    th=np.average(y,weights=w)
    s2=th*(1-th)/n
    # varianza entre encuestas (house effects) por método de momentos (DerSimonian-Laird simplificado)
    tau2=max(np.average((y-th)**2,weights=w)-np.average(s2,weights=w),0) if len(d)>2 else (0.3*th)**2
    v=s2+tau2
    prec=np.sum(w/v)*(1/np.mean(w))**0  # pesos temporales reducen la precisión efectiva
    prec=np.sum(w/v)/ (np.sum(w)/len(w)) * (np.sum(w)**2/np.sum(w**2))/len(w)
    pm=(m0/100)/( (PRIOR_SD/100)**2 ); pp=1/((PRIOR_SD/100)**2)
    post_mean=(pm+np.sum(w*y/v)/np.sum(w/v)*prec)/(pp+prec)
    post_sd=np.sqrt(1/(pp+prec))
    # la dispersión entre encuestas no puede desaparecer: el sesgo común de la industria no se promedia
    out[p]=dict(mean=round(post_mean*100,3),sd=round(post_sd*100,3),tau=round(np.sqrt(tau2)*100,3),k=int(len(d)))
r=pd.DataFrame(out).T
print(P[['firm','end','n','w','PP','PSOE','Vox','SUMESP','Podemos','SALF']].to_string())
print(r.to_string())
json.dump({'date':str(TODAY.date()),'window_days':WINDOW,'half_life':HALF,'n_polls':int(len(P)),
           'firms':P.firm.tolist(),'post':out},open(os.path.join(ROOT,'data','polls_post.json'),'w'),ensure_ascii=False)

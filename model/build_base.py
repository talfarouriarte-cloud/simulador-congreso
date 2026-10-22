"""Construye las cuotas base por provincia (2023 definitivo + reparto de partidos nuevos)."""
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import pandas as pd, numpy as np, json
B=pd.read_csv(os.path.join(ROOT,'data','base2023.csv'))
E=pd.read_csv(os.path.join(ROOT,'data','eu2024_ccaa.csv'))
E['ccaa']=E.title.str.split(' \|\| ').str[-1]
CCAA={'Andalusia':['Almería','Cádiz','Córdoba','Granada','Huelva','Jaén','Málaga','Seville'],
 'Aragon':['Huesca','Teruel','Zaragoza'],'Asturias':['Asturias'],'Balearic Islands':['Balearic Islands'],
 'Basque Country':['Álava','Biscay','Gipuzkoa'],'Canary Islands':['Las Palmas','Santa Cruz de Tenerife'],
 'Cantabria':['Cantabria'],'Castile and León':['Ávila','Burgos','León','Palencia','Salamanca','Segovia','Soria','Valladolid','Zamora'],
 'Castilla–La Mancha':['Albacete','Ciudad Real','Cuenca','Guadalajara','Toledo'],'Catalonia':['Barcelona','Girona','Lleida','Tarragona'],
 'Extremadura':['Badajoz','Cáceres'],'Galicia':['A Coruña','Lugo','Ourense','Pontevedra'],'La Rioja':['La Rioja'],'Madrid':['Madrid'],
 'Murcia':['Murcia'],'Navarre':['Navarre'],'Valencian Community':['Alicante','Castellón','Valencia'],'Ceuta':['Ceuta'],'Melilla':['Melilla']}
ES={'A Coruña':'A Coruña','Álava':'Álava','Albacete':'Albacete','Alicante':'Alicante','Almería':'Almería','Asturias':'Asturias','Ávila':'Ávila',
'Badajoz':'Badajoz','Balearic Islands':'Baleares','Barcelona':'Barcelona','Biscay':'Bizkaia','Burgos':'Burgos','Cáceres':'Cáceres','Cádiz':'Cádiz',
'Cantabria':'Cantabria','Castellón':'Castellón','Ceuta':'Ceuta','Ciudad Real':'Ciudad Real','Córdoba':'Córdoba','Cuenca':'Cuenca','Gipuzkoa':'Gipuzkoa',
'Girona':'Girona','Granada':'Granada','Guadalajara':'Guadalajara','Huelva':'Huelva','Huesca':'Huesca','Jaén':'Jaén','La Rioja':'La Rioja',
'Las Palmas':'Las Palmas','León':'León','Lleida':'Lleida','Lugo':'Lugo','Madrid':'Madrid','Málaga':'Málaga','Melilla':'Melilla','Murcia':'Murcia',
'Navarre':'Navarra','Ourense':'Ourense','Palencia':'Palencia','Pontevedra':'Pontevedra','Salamanca':'Salamanca','Santa Cruz de Tenerife':'S.C. Tenerife',
'Segovia':'Segovia','Seville':'Sevilla','Soria':'Soria','Tarragona':'Tarragona','Teruel':'Teruel','Toledo':'Toledo','Valencia':'Valencia',
'Valladolid':'Valladolid','Zamora':'Zamora','Zaragoza':'Zaragoza'}
CCAA_ES={'Andalusia':'Andalucía','Aragon':'Aragón','Asturias':'Asturias','Balearic Islands':'Baleares','Basque Country':'País Vasco','Canary Islands':'Canarias',
'Cantabria':'Cantabria','Castile and León':'Castilla y León','Castilla–La Mancha':'Castilla-La Mancha','Catalonia':'Cataluña','Extremadura':'Extremadura',
'Galicia':'Galicia','La Rioja':'La Rioja','Madrid':'Madrid','Murcia':'Murcia','Navarre':'Navarra','Valencian Community':'C. Valenciana','Ceuta':'Ceuta','Melilla':'Melilla'}
p2c={p:c for c,ps in CCAA.items() for p in ps}
B['ccaa']=B.prov.map(p2c); assert B.ccaa.notna().all()
E=E.set_index('ccaa')
# --- supuestos explícitos ---
C_FV=0.70          # fracción de (Sumar23 - Podemos) que corresponde a Compromís en la C. Valenciana
AA_BASE=0.04       # cuota base de Adelante Andalucía en provincias andaluzas (uniforme)
AC_BASE={'Girona':0.07,'Lleida':0.055,'Tarragona':0.04,'Barcelona':0.033}  # cuota base Aliança Catalana (índice relativo)
# Real Decreto 806/2026 (BOE 6-10-2026): Madrid 37->38, Cádiz 9->8; resto igual que en 2023
SEATS_2026={'Madrid':38,'Cádiz':8}
PARTIES=['PP','PSOE','Vox','FA','FV','Podemos','SALF','ERC','Junts','EH Bildu','PNV','BNG','CC','AA','Existe','Otros']
# Candidaturas 29-N: Podemos no se presenta en Cataluña (apoya a ERC), va en Compromís-Front Valencià en la C. Valenciana y en Unidad del Pueblo Canario (con FA y NC-BC) en Canarias;
# FA va dentro de Compromís-FV en la C. Valenciana y no se presenta en Teruel; UPN va en coalición con el PP; Aliança Catalana no se presenta; Coalición Existe en Aragón.
NC2023={'Las Palmas':42430,'Santa Cruz de Tenerife':3165}
EXISTE2023={'Teruel':11348,'Huesca':1312,'Zaragoza':7780}
rows=[]
moved={}; orig={}
def mv(a,b,x,V):
    moved[(a,b)]=moved.get((a,b),0)+x*V
for r in B.itertuples(index=False):
    d=r._asdict(); V=d['_37'] if False else None
for i,r in B.iterrows():
    V=r['Valid votes']; e=E.loc[r.ccaa]
    rpod=e.Podemos/(e.Podemos+e.Sumar)
    sh={p:r.get(p,0)/V for p in ['PP','PSOE','Vox','ERC','Junts','EH Bildu','PNV','BNG','CC','UPN']}
    sumar=r.Sumar/V
    sh['Podemos']=sumar*rpod
    rest=sumar-sh['Podemos']
    if r.ccaa=='Valencian Community': sh['FV']=rest*C_FV; sh['FA']=rest*(1-C_FV)
    else: sh['FV']=0; sh['FA']=rest
    sh['SALF']=e.SALF/e.valid
    sh['AA']=AA_BASE if r.ccaa=='Andalusia' else 0
    sh['Existe']=EXISTE2023.get(r.prov,0)/V
    for p in ['Podemos','FA','UPN']: orig[p]=orig.get(p,0)+sh[p]*V
    # --- ajustes por candidaturas reales del 29-N ---
    if r.ccaa=='Catalonia': mv('Podemos','ERC',sh['Podemos'],V)
    if r.ccaa=='Valencian Community': mv('Podemos','FV',sh['Podemos'],V); mv('FA','FV',sh['FA'],V)
    if r.ccaa=='Canary Islands': mv('Podemos','FA',sh['Podemos'],V)
    if r.prov=='Navarre': mv('UPN','PP',sh['UPN'],V)
    if r.prov=='Teruel': mv('FA','Otros',sh['FA'],V)
    if r.ccaa=='Catalonia': sh['ERC']+=sh['Podemos']; sh['Podemos']=0
    if r.ccaa=='Valencian Community': sh['FV']+=sh['Podemos']+sh['FA']; sh['Podemos']=0; sh['FA']=0
    if r.ccaa=='Canary Islands': sh['FA']+=sh['Podemos']+NC2023.get(r.prov,0)/V; sh['Podemos']=0
    if r.prov=='Navarre': sh['PP']+=sh['UPN']
    sh.pop('UPN')
    if r.prov=='Teruel': sh['FA']=0
    known=sum(sh.values()); sh['Otros']=max(1-known,0.01)
    tot=sum(sh.values()); sh={k:v/tot for k,v in sh.items()}
    rows.append(dict(prov=ES[r.prov],ccaa=CCAA_ES[r.ccaa],seats=SEATS_2026.get(r.prov,int(r.seats)),seats2023=int(r.seats),valid=int(V),**{p:round(sh[p],6) for p in PARTIES}))
D=pd.DataFrame(rows).sort_values('prov')
nat={p:float((D[p]*D.valid).sum()/D.valid.sum()) for p in PARTIES}
D.to_csv(os.path.join(ROOT,'data','base_shares.csv'),index=False)
json.dump({'parties':PARTIES,'provinces':D.to_dict('records'),'base_nat':nat,
           'assumptions':{'C_FV':C_FV,'AA_BASE':AA_BASE},'transfers':[{'from':a,'to':b,'frac':v/orig[a]} for (a,b),v in moved.items() if a!='UPN'],'nc_nat':sum(NC2023.values())/float(B['Valid votes'].sum())},open(os.path.join(ROOT,'data','base.json'),'w'),ensure_ascii=False)
print({k:round(v*100,2) for k,v in nat.items()}); print(D.seats.sum(), len(D))

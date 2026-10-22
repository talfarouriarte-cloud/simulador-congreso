import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw")+"/"
import json
b=json.load(open(os.path.join(ROOT,'data','base.json'))); p=json.load(open(os.path.join(ROOT,'data','polls_post.json')))
po=p['post']
m={k:dict(mean=v['mean'],sd=v['sd']) for k,v in po.items() if k not in('SUMESP','FVobs','AC','UPN')}
m['FV']=dict(mean=po['FVobs']['mean'],sd=po['FVobs']['sd'])
m['FA']=dict(mean=po['SUMESP']['mean']-po['FVobs']['mean']+b['nc_nat']*100,sd=po['SUMESP']['sd'])
m['PP']['mean']+=po['UPN']['mean']
src={k:m[k]['mean'] for k in m}
for t in b['transfers']:
    x=src[t['from']]*t['frac']; m[t['from']]['mean']-=x
    if t['to'] in m: m[t['to']]['mean']+=x
m['Existe']=dict(mean=b['base_nat']['Existe']*100,sd=0.03)
for k in m: m[k]['mean']=round(m[k]['mean'],2)
print({k:v['mean'] for k,v in m.items()})
D={'means':m,'parties':b['parties'],'provinces':b['provinces'],'assumptions':b['assumptions'],'post':p['post'],
   'meta':{'poll_date':'17 de octubre de 2026','window_from':'7 de septiembre de 2026','half_life':p['half_life'],'n_polls':p['n_polls'],'firms':p['firms'],'built':'22 de octubre de 2026'}}
s=open(os.path.join(ROOT,'model','template.html')).read().replace('__DATA__',json.dumps(D,ensure_ascii=False).replace('</','<\\/'))
HEAD='''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Simulador bayesiano de escaños del Congreso para las generales del 29 de noviembre de 2026: media de encuestas, sensibilidad por partido y voto útil por provincia.">
<meta property="og:title" content="Voto útil a la derecha"><meta property="og:description" content="Mueve los votos y mira dónde rinde el voto a cada partido, provincia a provincia.">
<meta property="og:type" content="website"><meta property="og:image" content="__SITE__docs/portada.png"><meta property="og:url" content="__SITE__">
<meta name="twitter:card" content="summary_large_image"><style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}</style></head><body>
'''
SITE=os.environ.get('SITE_URL','')
open(os.path.join(ROOT,'index.html'),'w').write(HEAD.replace('__SITE__',SITE)+s+'\n</body></html>\n')
json.dump(D,open(os.path.join(ROOT,'data','page_data.json'),'w'),ensure_ascii=False)
print(len(s))

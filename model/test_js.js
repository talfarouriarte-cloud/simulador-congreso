const fs=require('fs');const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const code=html.split('/*ENGINE-START*/')[1].split('/*ENGINE-END*/')[0];const m={exports:{}};new Function('module',code)(m);const E=m.exports;
const D=JSON.parse(fs.readFileSync(__dirname+'/../data/page_data.json','utf8'));const M=E.setup(D);const P=D.parties;
// 1) validación: el motor JS reproduce 2023 con las cuotas base sin Podemos/etc no aplica; validar D'Hondt con un caso conocido
const madrid=[1463183,1004599,506164,557780];console.log('Madrid 2023',Array.from(E.dhondt(madrid,37,3524000,[1,1,1,1])));
const post=D.post;const mu=P.map(p=>p==='Otros'?0:D.means[p].mean);
const s=mu.reduce((a,b)=>a+b,0);mu[P.indexOf('Otros')]=Math.max(100-s,0.5);const t=mu.reduce((a,b)=>a+b,0);const muv=mu.map(x=>x/t);
const sd=P.map(p=>p==='Otros'?0.003:D.means[p].sd/100);
let t0=Date.now();const R=E.simulate(M,{N:5000,mu:muv,sd,unc:1,delta:0.01,seed:3});console.log('ms',Date.now()-t0);
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
console.log(JSON.stringify(Object.fromEntries(P.map((p,j)=>[p,+mean(Array.from(R.natSeats[j])).toFixed(1)]))));
console.log('P(PP+Vox>=176)',mean(Array.from(R.blocPV).map(b=>b>=176?1:0)),'media',mean(Array.from(R.blocPV)));
fs.writeFileSync(__dirname+'/../data/js_out.json',JSON.stringify({prov:D.provinces.map(p=>p.prov),conc:R.conc,voxGain:R.voxGain,concNeg:R.concNeg}));
const C=E.central(M,muv);console.log('central',JSON.stringify(Object.fromEntries(P.map((p,j)=>[p,C.seats.reduce((a,x)=>a+x[j],0)]))));
const k=D.provinces.findIndex(p=>p.prov==='Soria');console.log('Soria flip',E.flipNeeded(M,k,C.votes[k],P.indexOf('Vox'),P.indexOf('PP'),P.indexOf('PP'),P.indexOf('Vox')));

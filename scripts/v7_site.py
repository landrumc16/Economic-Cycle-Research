"""V7: human-first market-risk and economic intelligence site (static, dependency-free).

Five destinations, one home per feature:
  index.html (Home: stock-market warning check) · market-risk.html (evidence) ·
  forecast.html (Economy: conditions and tested outlooks; track-record.html linked from it) ·
  sectors.html (+11 sector pages) · research.html (Research & Data).
The homepage summarises and links; detail lives in exactly one place.
All numbers come from gated evidence files; unpublished outlooks render as
"Not enough evidence yet". Nothing here is investment advice.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
from datetime import date
from pathlib import Path

try:
    from .v7_forecast_engine import load as load_fred, shift
    from .v63_historical_replay import assessment_at
    from .v63_interpretation import interpret
except ImportError:
    from v7_forecast_engine import load as load_fred, shift
    from v63_historical_replay import assessment_at
    from v63_interpretation import interpret

NAV = (("Home", "index.html", "home"), ("Market Risk", "market-risk.html", "market"), ("Economy", "forecast.html", "forecast"),
       ("Sectors", "sectors.html", "sectors"), ("Research & Data", "research.html", "research"))
TARGET_LABEL = {"labor_deterioration": "Job market weakens", "recession": "Recession under way",
                "recession_onset": "New recession starts", "inflation_rising": "Inflation picks up"}
TARGET_PLAIN = {
    "labor_deterioration": "Unemployment rises at least 0.5 points",
    "recession": "The economy is in a recession at some point",
    "recession_onset": "A new recession begins",
    "inflation_rising": "The yearly inflation rate is higher than today",
}
CHECK_SHORT = {"calibration": "too confident", "bss_vs_base_rate": "no better than average",
               "auc": "weak at ranking risk", "episodes": "too few episodes"}
REASON_PLAIN = {
    "calibration": "our model spots risk well, but its probabilities have historically been too confident",
    "bss_vs_base_rate": "it has not beaten simply using the long-run average",
    "auc": "it has not reliably told higher-risk periods from lower-risk ones",
    "episodes": "there are too few past episodes to judge",
}
ICONS = {
    "market": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/><path d="M4 10l6-6 6 9 5-5"/>',
    "home": '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "forecast": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "sectors": '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
    "track": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    "research": '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h8M8 8h4"/>',
}

CSS = """
:root{--bg:#f4f6fb;--card:#fff;--ink:#0f1b2d;--muted:#55657a;--line:#dde3ec;--brand:#1f4e89;--brand2:#2f74c0;
--good:#1d7a4f;--warn:#a35a00;--bad:#b3261e;--chip:#eef3fa;--hatch:#c8d2e0;--focus:#ff9e1b;--okbg:#e3f4ea;--okfg:#14563a;
--wbg:#fff2dc;--wfg:#7a4300;--badbg:#fde8e6;--badfg:#8f1d16;--lowbg:#eef1f5;--lowfg:#47566b;--tip:#0f1b2d;--tipfg:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d1420;--card:#152033;--ink:#e8eef7;--muted:#a3b2c6;--line:#26354d;--brand:#7fb0ff;--brand2:#9cc3ff;
--good:#5fd39a;--warn:#ffb74d;--bad:#ff8a80;--chip:#1c2a42;--hatch:#3a4a63;--okbg:#163a2a;--okfg:#8ee0b4;--wbg:#3b2a12;
--wfg:#ffcf8a;--badbg:#3d1a18;--badfg:#ffb4ab;--lowbg:#222e40;--lowfg:#b7c4d6;--tip:#e8eef7;--tipfg:#0d1420;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0d1420;--card:#152033;--ink:#e8eef7;--muted:#a3b2c6;--line:#26354d;--brand:#7fb0ff;--brand2:#9cc3ff;
--good:#5fd39a;--warn:#ffb74d;--bad:#ff8a80;--chip:#1c2a42;--hatch:#3a4a63;--okbg:#163a2a;--okfg:#8ee0b4;--wbg:#3b2a12;
--wfg:#ffcf8a;--badbg:#3d1a18;--badfg:#ffb4ab;--lowbg:#222e40;--lowfg:#b7c4d6;--tip:#e8eef7;--tipfg:#0d1420;color-scheme:dark}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--brand)}a:focus-visible,button:focus-visible,[tabindex]:focus-visible,summary:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:12px;top:12px;background:var(--card);padding:8px 12px;z-index:9}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.bar{max-width:1120px;margin:auto;padding:10px 16px;display:flex;align-items:center;gap:8px 16px;flex-wrap:wrap}
.brand{min-width:0;overflow-wrap:anywhere}
.brand{font-weight:800;color:var(--ink);text-decoration:none;letter-spacing:-.01em;display:flex;align-items:center;gap:8px}
.brand .dot{width:10px;height:10px;border-radius:50%;background:var(--brand2)}
nav.primary{margin-left:auto;display:none;gap:4px}
nav.primary a{text-decoration:none;color:var(--muted);padding:8px 12px;border-radius:999px;font-weight:600;font-size:.95rem}
nav.primary a[aria-current=page]{background:var(--chip);color:var(--brand)}
nav.tabs{position:sticky;bottom:0;background:var(--card);border-top:1px solid var(--line);display:grid;
grid-template-columns:repeat(5,minmax(0,1fr));z-index:6;padding-bottom:env(safe-area-inset-bottom)}
nav.tabs a{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 2px 10px;font-size:.72rem;
color:var(--muted);text-decoration:none;min-height:56px;text-align:center;line-height:1.15;overflow-wrap:anywhere;hyphens:auto;-webkit-hyphens:auto;min-width:0}
nav.tabs a[aria-current=page]{color:var(--brand);font-weight:700}
nav.tabs svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
main{max-width:1120px;margin:auto;padding:18px 16px 24px}
h1{font-size:1.6rem;line-height:1.2;margin:.2em 0 .3em;letter-spacing:-.02em}
h2{font-size:1.2rem;margin:0 0 .5em;line-height:1.25}h3{font-size:1rem;margin:1em 0 .3em}
.lede{color:var(--muted);margin:0 0 1em;max-width:62ch}
.grid{display:grid;gap:14px}.cols-2,.cols-3{grid-template-columns:1fr}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}
.card.hero{background:linear-gradient(135deg,var(--card),var(--chip))}
.eyebrow{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700;margin:0 0 6px}
.big{font-size:2rem;font-weight:800;letter-spacing:-.02em;margin:0}
.chip{display:inline-block;background:var(--chip);color:var(--ink);border-radius:999px;padding:3px 10px;font-size:.82rem;font-weight:600;margin:2px 4px 2px 0}
.chip.good{color:var(--good)}.chip.warn{color:var(--warn)}.chip.bad{color:var(--bad)}.chip.muted{color:var(--muted)}
.muted{color:var(--muted)}small{color:var(--muted)}
ul.clean{padding-left:1.1em;margin:.3em 0}ul.clean li{margin:.35em 0}
.horizons{display:grid;gap:10px;grid-template-columns:1fr}
.hz{border:1px solid var(--line);border-radius:12px;padding:12px}
.hz .label{font-weight:700}.hz .state{font-size:.9rem;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.scroll{overflow-x:auto;position:relative}
.sector-card{display:block;text-decoration:none;color:inherit}
.sector-card:hover{border-color:var(--brand2)}
.pill{font-size:.78rem;font-weight:700;border-radius:8px;padding:2px 8px;display:inline-block}
.p-now{background:var(--okbg);color:var(--okfg)}.p-mon{background:var(--wbg);color:var(--wfg)}.p-low{background:var(--lowbg);color:var(--lowfg)}
details{border:1px solid var(--line);border-radius:12px;padding:10px 14px;background:var(--card);margin:10px 0}
summary{cursor:pointer;font-weight:700;min-height:28px}
.note{border-left:4px solid var(--brand2);padding:8px 12px;background:var(--chip);border-radius:8px;margin:10px 0}
footer{max-width:1120px;margin:auto;padding:0 16px 16px;color:var(--muted);font-size:.85rem}
svg text{fill:currentColor}
.chart{width:100%;height:auto;display:block;color:var(--ink)}
.chart.square{max-width:340px;margin:auto}
ul.dbars{list-style:none;margin:6px 0;padding:0}
ul.dbars li{display:grid;grid-template-columns:minmax(0,9.5em) 1fr 4.8em;gap:8px;align-items:center;margin:6px 0;font-size:.9rem}
.db-label{overflow-wrap:anywhere}.db-val{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
.db-track{position:relative;height:14px;background:var(--chip);border-radius:7px}
.db-zero{position:absolute;left:50%;top:-3px;bottom:-3px;width:2px;background:var(--muted)}
.db-fill{position:absolute;top:0;bottom:0;border-radius:7px}.db-fill.pos{background:var(--good)}.db-fill.neg{background:var(--bad)}
th[scope=row]{text-transform:none;letter-spacing:0;font-size:.92rem;color:var(--ink);font-weight:600}
/* Market-risk dashboard */
.fig{margin:8px 0 0}.fig figcaption{font-size:.85rem;color:var(--muted);margin-top:4px}
.chart.ts{max-width:600px}
.legend i.dash{background:none!important;border-top:2px dashed var(--ink);height:0;border-radius:0}
.legend{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:.85rem;color:var(--muted);margin:6px 0 0;padding:0;list-style:none}
.legend li{display:flex;align-items:center;gap:6px}.legend i{display:inline-block;width:14px;height:4px;border-radius:2px}
.st{display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:.85rem;border-radius:999px;padding:3px 10px;white-space:nowrap}
.st::before{content:"";width:9px;height:9px;border-radius:50%;background:currentColor}
.st-warning{background:var(--badbg);color:var(--badfg)}.st-near{background:var(--wbg);color:var(--wfg)}
.st-clear{background:var(--okbg);color:var(--okfg)}.st-nc{background:var(--chip);color:var(--muted)}
.hero-q{font-size:1.5rem;line-height:1.2;margin:0 0 6px}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:10px 0 0}
.kpi div{background:var(--chip);border-radius:12px;padding:8px 10px}
.kpi b{display:block;font-size:1.15rem;font-variant-numeric:tabular-nums}.kpi span{font-size:.8rem;color:var(--muted)}
.neg{color:var(--bad)}.pos{color:var(--good)}
table.grid7{border-collapse:collapse;width:100%;font-size:.85rem}
table.grid7 th,table.grid7 td{padding:6px 3px;text-align:center;border-bottom:1px solid var(--line)}
table.grid7 th[scope=row]{text-align:left;white-space:nowrap}
.on{color:var(--bad);font-weight:800}.off{color:var(--muted)}
.two{display:grid;gap:12px}.two>*{min-width:0}@media(min-width:720px){.two{grid-template-columns:1fr 1fr}
ul.rows.wgrid{display:grid;grid-template-columns:repeat(3,1fr);column-gap:22px}ul.rows.wgrid li{border-top:1px solid var(--line)}}
/* Interactive charts */
.plot{position:relative}
.rng{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 6px}
.rng button,.theme button{font:inherit;font-size:.85rem;font-weight:700;min-height:36px;min-width:44px;padding:4px 12px;border-radius:999px;
border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.rng button[aria-pressed="true"],.theme button[aria-pressed="true"]{background:var(--ink);color:var(--card);border-color:var(--ink)}
.chart.ts{touch-action:pan-y;cursor:crosshair}
.chart.ts:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.tip{position:absolute;top:0;pointer-events:none;background:var(--tip);color:var(--tipfg);border-radius:8px;padding:6px 8px;
font-size:.8rem;line-height:1.3;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.25);z-index:2;font-variant-numeric:tabular-nums}
.tip b{display:block}.tip i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}
.theme{display:none;gap:4px;margin-left:auto}.theme.on{display:flex}nav.primary+.theme{margin-left:8px}
.theme button{min-height:36px;font-size:.8rem;padding:4px 10px}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
/* Pass C compact mobile components */
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.desk{display:none}
.stack{display:grid;gap:12px}
.card.hero svg{max-width:420px}
.card h2.big{font-size:1.9rem;line-height:1.1}
.row-head{display:flex;align-items:baseline;justify-content:space-between;gap:8px;flex-wrap:wrap}
.row-head a{font-weight:600;font-size:.92rem;white-space:nowrap}
ul.rows{list-style:none;margin:8px 0 0;padding:0}
ul.rows li{border-top:1px solid var(--line)}ul.rows li:first-child{border-top:0}
.rowlink,.rowstatic{display:grid;grid-template-columns:1fr auto;gap:4px 10px;align-items:center;padding:9px 0;min-height:48px;color:inherit;text-decoration:none}
.rowlink:hover .rname{text-decoration:underline}
.rname{font-weight:700}.rsub{grid-column:1/-1;font-size:.88rem;color:var(--muted)}
.rval{font-weight:700;font-variant-numeric:tabular-nums;text-align:right}
.mini{position:relative;height:8px;border-radius:4px;background:var(--chip);grid-column:1/-1}
.mini .fill{position:absolute;top:0;bottom:0;left:0;border-radius:4px;background:var(--brand2)}
.mini .base{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--ink)}
.mini.hatch{background:repeating-linear-gradient(45deg,var(--hatch) 0 3px,transparent 3px 7px)}
.mini.rs .zero{position:absolute;top:-3px;bottom:-3px;left:50%;width:2px;background:var(--muted)}
.mini.rs .pos{position:absolute;top:0;bottom:0;left:50%;border-radius:4px;background:var(--good)}
.mini.rs .neg{position:absolute;top:0;bottom:0;border-radius:4px;background:var(--bad)}
.badges{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.b{font-size:.8rem;font-weight:700;border-radius:8px;padding:3px 8px;background:var(--chip);color:var(--muted);overflow-wrap:anywhere}
.b:not(.ok){background:none;border:1px dashed var(--hatch)}
.b.ok{background:var(--okbg);color:var(--okfg)}
details.fold{margin:0;border-radius:0;border:0;border-top:1px solid var(--line);padding:0;background:none}
details.fold:first-of-type{border-top:0}
details.fold>summary{padding:12px 0;min-height:48px;display:flex;align-items:center;justify-content:space-between;list-style:none}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary::after{content:"+";font-size:1.3rem;color:var(--muted);margin-left:8px}
details.fold[open]>summary::after{content:"−"}
details.fold>div{padding:0 0 12px}
.oneline{margin:.4em 0 0}
.grid>*,.stack>*,.rowlink>*,.rowstatic>*{min-width:0}
main h1,main h2,main p,main li,main summary,.rname,.rsub{overflow-wrap:anywhere}
.row-head a{display:inline-flex;align-items:center;min-height:32px}
code{font-size:.9em;overflow-wrap:anywhere}
@media(max-width:719px){html{scroll-padding-bottom:calc(6rem + env(safe-area-inset-bottom))}main{padding:12px 14px 16px}.card{padding:14px;border-radius:14px}
h1{font-size:1.35rem;margin:.1em 0 .4em}footer{padding:0 14px 12px}}
@media(min-width:720px){.hero-q{font-size:2rem}.desk{display:block}nav.primary{display:flex}nav.tabs{display:none}main{padding-bottom:40px}footer{padding-bottom:30px}
.cols-2{grid-template-columns:1fr 1fr}.cols-3{grid-template-columns:repeat(3,1fr)}.horizons{grid-template-columns:repeat(3,1fr)}h1{font-size:2rem}}
"""


# Progressive enhancement: charts work without it; with it they gain periods, readouts and keyboard stepping.
JS = r"""(function(){
var MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function mx(t){return +t.slice(0,4)*12+(+t.slice(5,7))-1+(t.length>=10?(+t.slice(8,10)-1)/31:0);}
function fmtT(t){return t.length>=10?MON[+t.slice(5,7)-1]+" "+(+t.slice(8,10))+", "+t.slice(0,4):MON[+t.slice(5,7)-1]+" "+t.slice(0,4);}
function num(v,d,u){return (v<0?"−":"")+Math.abs(v).toFixed(d)+u;}
function esc(x){return String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");}
function nice(x){var e=Math.pow(10,Math.floor(Math.log10(x))),f=x/e;return (f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*e;}
function draw(fig,c,start,fit){
  var L=34,R=8,T=8,B=20,w=c.w,h=c.h,y0=c.y0,y1=c.y1,out=[];
  var all=[];c.series.forEach(function(s){s.pts.forEach(function(p){if(p[0]>=start)all.push(p);});});
  if(fit){var vals=all.map(function(p){return p[1];}).filter(function(v){return v!==null;}).concat(c.hlines);
    if(c.y0<=0&&c.y1>=0)vals.push(0);var lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals),st=nice(Math.max(1e-6,(hi-lo)/4));
    y0=Math.floor(lo/st)*st;y1=Math.ceil(hi/st)*st;if(y1-y0<st*2){y1+=st;}}
  var x0=mx(start),x1=Math.max.apply(null,all.map(function(p){return mx(p[0]);}));
  function X(t){return L+(w-L-R)*(mx(t)-x0)/Math.max(1e-9,x1-x0);}
  function Y(v){return T+(h-T-B)*(y1-Math.max(y0,Math.min(y1,v)))/(y1-y0);}
  var runs=[],cur=null;c.shade.filter(function(m){return m>=start;}).forEach(function(m){
    if(cur&&mx(m)-mx(cur[1])<=1){cur[1]=m;}else{cur=[m,m];runs.push(cur);}});
  runs.forEach(function(r){out.push('<rect x="'+X(r[0]).toFixed(1)+'" y="'+T+'" width="'+Math.max(1.2,X(r[1])-X(r[0])+1).toFixed(1)+'" height="'+(h-T-B)+'" fill="var(--hatch)" opacity=".45"/>');});
  [y0,(y0+y1)/2,y1].forEach(function(v){var dec=Math.abs(v-Math.round(v))>1e-9?Math.max(c.ydec,1):c.ydec;out.push('<line x1="'+L+'" x2="'+(w-R)+'" y1="'+Y(v).toFixed(1)+'" y2="'+Y(v).toFixed(1)+'" stroke="var(--line)"/><text x="'+(L-4)+'" y="'+(Y(v)+4).toFixed(1)+'" text-anchor="end" font-size="11">'+num(v,dec,c.unit)+'</text>');});
  var span=(x1-x0)/12,step=c.every||[1,2,5,10,20,25].filter(function(s){return span/s<=6;})[0]||25;
  var lastY=+all.reduce(function(a,p){return p[0]>a?p[0]:a;},"0000").slice(0,4);
  if(span<1.5){for(var k=0;k<=Math.ceil(span*12);k+=Math.max(1,Math.round(span*12/4))){var mi=Math.floor(x0)+k,t=Math.floor(mi/12)+"-"+("0"+(mi%12+1)).slice(-2);var x=X(t);
    if(x>=L&&x<=w-R)out.push('<text x="'+x.toFixed(1)+'" y="'+(h-5)+'" text-anchor="middle" font-size="11">'+MON[mi%12]+(mi%12===0?" "+t.slice(2,4):"")+'</text>');}}
  else{for(var yr=+start.slice(0,4)+((-+start.slice(0,4))%step+step)%step;yr<=lastY;yr+=step){var x=X(yr+"-01");if(x>=L&&x<=w-R)out.push('<text x="'+x.toFixed(1)+'" y="'+(h-5)+'" text-anchor="middle" font-size="11">'+yr+'</text>');}}
  c.hlines.forEach(function(v){out.push('<line x1="'+L+'" x2="'+(w-R)+'" y1="'+Y(v).toFixed(1)+'" y2="'+Y(v).toFixed(1)+'" stroke="var(--ink)" stroke-dasharray="4 3" stroke-width="1.2"/>');});
  c.series.forEach(function(s){var pts=s.pts.filter(function(p){return p[0]>=start&&p[1]!==null;}).map(function(p){return [X(p[0]),Y(p[1])];});
    if(!pts.length)return;var d="M"+pts.map(function(q){return q[0].toFixed(1)+","+q[1].toFixed(1);}).join(" L");
    if(s.area){var b=Y(Math.max(y0,Math.min(y1,0)));out.push('<path d="'+d+' L'+pts[pts.length-1][0].toFixed(1)+','+b.toFixed(1)+' L'+pts[0][0].toFixed(1)+','+b.toFixed(1)+'Z" fill="'+s.color+'" opacity=".25"/>');}
    out.push('<path d="'+d+'" fill="none" stroke="'+s.color+'" stroke-width="1.6"'+(s.dash?' stroke-dasharray="5 3"':'')+' stroke-linejoin="round"/>');});
  var prev=-1e9;c.ann.filter(function(a){return a[0]>=start;}).sort(function(a,b){return a[0]<b[0]?-1:1;}).forEach(function(a){
    var x=X(a[0]),y=Y(a[1]),crowd=x-prev<=70;prev=x;var anchor=x>w*0.8?"end":x<w*0.2?"start":"middle";
    var tx=crowd?x+6:x,ty=crowd?y+4:y+(a[1]<(y0+y1)/2?13:-6);
    out.push('<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="2.6" fill="var(--ink)"/><text x="'+tx.toFixed(1)+'" y="'+ty.toFixed(1)+'" text-anchor="'+(crowd?"start":anchor)+'" font-size="10.5" font-weight="700">'+esc(a[2])+'</text>');});
  out.push('<line class="cur" x1="0" x2="0" y1="'+T+'" y2="'+(h-B)+'" stroke="var(--ink)" stroke-width="1" visibility="hidden"/>');
  var svg=fig.querySelector("svg");svg.innerHTML=out.join("");
  svg.setAttribute("aria-label",c.label.replace(/^(.*?)(\d{4}|[A-Z][a-z]{2} \d{1,2}, \d{4}) to /,"$1"+fmtT(start)+" to "));
  fig._g={X:X,Y:Y,x0:x0,x1:x1,L:L,R:R,w:w,start:start};
}
function nearest(pts,m){var lo=0,hi=pts.length-1;while(hi-lo>1){var mid=(lo+hi)>>1;if(mx(pts[mid][0])<m)lo=mid;else hi=mid;}
  return Math.abs(mx(pts[lo][0])-m)<=Math.abs(mx(pts[hi][0])-m)?pts[lo]:pts[hi];}
function setup(fig){
  var c=JSON.parse(fig.querySelector('script[type="application/json"]').textContent);
  var svg=fig.querySelector("svg"),tip=fig.querySelector(".tip"),live=fig.querySelector("[aria-live]");
  var main=c.series[0].pts,first=c.series.reduce(function(a,s){return s.pts[0][0]<a?s.pts[0][0]:a;},"9999");
  var lastT=main[main.length-1][0],start=c.start,idx=null;
  svg.setAttribute("tabindex","0");
  svg.setAttribute("aria-describedby","");
  draw(fig,c,start);
  var rng=fig.querySelector(".rng");
  if(rng){rng.hidden=false;rng.querySelectorAll("button").forEach(function(b){b.addEventListener("click",function(){
    var yrs=+b.dataset.years;if(yrs){var m=mx(lastT)-12*yrs,t=Math.floor(m/12)+"-"+("0"+(Math.floor(m)%12+1)).slice(-2);start=t<first?first.slice(0,7):t;}else{start=first.slice(0,7);}
    rng.querySelectorAll("button").forEach(function(o){o.setAttribute("aria-pressed",o===b?"true":"false");});
    idx=null;hide();draw(fig,c,start,true);live.textContent="Showing "+fmtT(start)+" to "+fmtT(lastT)+".";});});}
  function show(m){
    var g=fig._g,rows=[],xp=null;
    c.series.forEach(function(s){var vis=s.pts.filter(function(p){return p[0]>=g.start;});if(!vis.length)return;var p=nearest(vis,m);
      if(xp===null){xp=p[0];}rows.push([s,p]);});
    if(xp===null)return;
    var x=g.X(xp),cur=svg.querySelector(".cur");cur.setAttribute("x1",x);cur.setAttribute("x2",x);cur.setAttribute("visibility","visible");
    tip.innerHTML="<b>"+fmtT(xp)+"</b>"+rows.map(function(r){return '<span><i style="background:'+r[0].color+'"></i>'+esc(r[0].name)+": "+num(r[1][1],c.dec,c.unit)+(r[1][0]!==xp?" ("+fmtT(r[1][0])+")":"")+"</span>";}).join("<br>");
    tip.hidden=false;var box=svg.getBoundingClientRect(),px=x/g.w*box.width,tw=tip.offsetWidth;
    tip.style.left=Math.max(0,Math.min(box.width-tw,px-tw/2))+"px";
    return fmtT(xp)+": "+rows.map(function(r){return r[0].name+" "+num(r[1][1],c.dec,c.unit);}).join("; ");
  }
  function hide(){tip.hidden=true;var cur=svg.querySelector(".cur");if(cur)cur.setAttribute("visibility","hidden");}
  function fromEvent(e){var g=fig._g,box=svg.getBoundingClientRect(),x=(e.clientX-box.left)/box.width*g.w;
    return g.x0+(g.x1-g.x0)*(x-g.L)/(g.w-g.L-g.R);}
  svg.addEventListener("pointermove",function(e){show(fromEvent(e));});
  svg.addEventListener("pointerdown",function(e){show(fromEvent(e));});
  svg.addEventListener("pointerleave",function(e){if(e.pointerType==="mouse")hide();});
  svg.addEventListener("blur",hide);
  svg.addEventListener("keydown",function(e){
    var vis=main.filter(function(p){return p[0]>=fig._g.start;});if(!vis.length)return;
    if(idx===null)idx=vis.length-1;
    var step=e.shiftKey?12:1;
    if(e.key==="ArrowLeft")idx=Math.max(0,idx-step);else if(e.key==="ArrowRight")idx=Math.min(vis.length-1,idx+step);
    else if(e.key==="Home")idx=0;else if(e.key==="End")idx=vis.length-1;else if(e.key==="Escape"){hide();return;}else return;
    e.preventDefault();live.textContent=show(mx(vis[idx][0]));});
  svg.addEventListener("focus",function(){live.textContent="Use left and right arrow keys to read values; Shift moves a year.";});
}
document.querySelectorAll("figure[data-chart]").forEach(function(f){try{setup(f);}catch(err){}});
// Stale-data notice: shown when the latest market data are more than four days old on the viewer's own clock.
document.querySelectorAll("[data-through]").forEach(function(el){var t=el.getAttribute("data-through");if(!t)return;
  var days=Math.floor((Date.now()-Date.parse(t+"T00:00:00Z"))/864e5);if(days>4){el.textContent="Market data are "+days+
  " days old. The latest update may have failed, so the last valid assessment is shown.";el.hidden=false;}});
// Colour theme: System, Light or Dark (remembered on this device when storage is available)
var btn=document.querySelector(".theme button"),modes=["system","light","dark"],names={system:"Auto",light:"Light",dark:"Dark"};
function apply(m){if(m==="system")document.documentElement.removeAttribute("data-theme");else document.documentElement.setAttribute("data-theme",m);
  if(btn){btn.textContent="\u25D0 "+names[m];btn.setAttribute("aria-label","Colour theme: "+(m==="system"?"follows your device":names[m])+". Change theme");}}
var mode="system";try{mode=localStorage.getItem("v7-theme")||"system";}catch(e){}
if(document.documentElement.hasAttribute("data-theme")&&mode==="system"){mode="host";}
if(btn){btn.parentNode.classList.add("on");if(mode!=="host")apply(mode);else{apply(document.documentElement.getAttribute("data-theme")==="dark"?"dark":"light");}
  btn.addEventListener("click",function(){var cur=document.documentElement.getAttribute("data-theme")||"system";var next=modes[(modes.indexOf(cur)+1)%3];apply(next);try{localStorage.setItem("v7-theme",next);}catch(e){}});}
})();
"""


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def icon(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def page(title: str, active: str, body: str, description: str) -> str:
    top = "".join(f'<a href="{u}"{" aria-current=page" if k == active else ""}>{esc(t)}</a>' for t, u, k in NAV)
    tabs = "".join(f'<a href="{u}"{" aria-current=page" if k == active else ""}>{icon(k)}<span>{esc(t)}</span></a>'
                   for t, u, k in NAV)
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<meta name=\"description\" content=\"{esc(description)}\"><title>{esc(title)} — Economic Cycle Research</title>"
            f"<style>{CSS}</style></head><body><a class=\"skip\" href=\"#main\">Skip to content</a>"
            "<header class=\"top\"><div class=\"bar\"><a class=\"brand\" href=\"index.html\"><span class=\"dot\" aria-hidden=\"true\"></span>"
            f"Economic Cycle Research</a><nav class=\"primary\" aria-label=\"Primary\">{top}</nav>"
            "<div class=\"theme\"><button type=\"button\">Theme</button></div></div></header>"
            f"<main id=\"main\">{body}</main>"
            "<footer><p><strong>Educational research — not personalized financial advice.</strong> Outlooks are published only "
            "when they pass our historical reliability test; otherwise we say there is not enough evidence. Past performance does "
            "not guarantee future results, and investing involves risk, including loss of principal.</p></footer>"
            f"<nav class=\"tabs\" aria-label=\"Primary\">{tabs}</nav><script>{JS}</script></body></html>")


# --------------------------------------------------------------------------
# Charts (inline SVG, each with a text alternative)
# --------------------------------------------------------------------------
def _mx(t: str) -> float:
    """'YYYY-MM' or 'YYYY-MM-DD' to a fractional month index."""
    y, m = int(t[:4]), int(t[5:7])
    return y * 12 + m - 1 + ((int(t[8:10]) - 1) / 31 if len(t) >= 10 else 0)


def _fmt_month(t: str) -> str:
    return date(int(t[:4]), int(t[5:7]), 1).strftime("%b %Y")


def ts_chart(series, *, y0, y1, start, label, caption="", h=170, w=400, shade=(), hlines=(), yfmt="{:.0f}",
             ann=(), ticks_every=None, tip_dec=1):
    """Time-series chart: series = [{"name", "pts": [[t, y]], "color", "area": bool, "dash": bool}]."""
    L, R, T, B = 34, 8, 8, 20
    pts_all = [p for sr in series for p in sr["pts"] if p[0] >= start]
    x0, x1 = _mx(start), max(_mx(p[0]) for p in pts_all)
    X = lambda t: L + (w - L - R) * (_mx(t) - x0) / max(1e-9, x1 - x0)
    Y = lambda v: T + (h - T - B) * (y1 - max(y0, min(y1, v))) / (y1 - y0)
    out = []
    if shade:  # recession months as bands
        runs, cur = [], None
        for m in sorted(m for m in shade if m >= start):
            if cur and _mx(m) - _mx(cur[1]) <= 1:
                cur[1] = m
            else:
                cur = [m, m]
                runs.append(cur)
        for a_, b_ in runs:
            out.append(f'<rect x="{X(a_):.1f}" y="{T}" width="{max(1.2, X(b_) - X(a_) + 1):.1f}" height="{h - T - B}" '
                       'fill="var(--hatch)" opacity=".45"/>')
    for v in (y0, (y0 + y1) / 2, y1):
        out.append(f'<line x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/>'
                   f'<text x="{L - 4}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="11">{esc(yfmt.format(v))}</text>')
    span = (x1 - x0) / 12
    step = ticks_every or next(s_ for s_ in (1, 2, 5, 10, 20, 25) if span / s_ <= 6)
    y_first = int(start[:4]) + (-int(start[:4]) % step)
    for yr in range(y_first, int(max(p[0] for p in pts_all)[:4]) + 1, step):
        x = X(f"{yr}-01")
        if L <= x <= w - R:
            out.append(f'<text x="{x:.1f}" y="{h - 5}" text-anchor="middle" font-size="11">{yr}</text>')
    for v, txt in hlines:  # threshold lines; their meaning is given in the legend, never drawn over the data
        out.append(f'<line x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--ink)" stroke-dasharray="4 3" '
                   'stroke-width="1.2"/>')
    for sr in series:
        pts = [(X(t), Y(v)) for t, v in sr["pts"] if t >= start and v is not None]
        if not pts:
            continue
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if sr.get("area"):
            base = Y(max(y0, min(y1, 0)))
            out.append(f'<path d="{d} L{pts[-1][0]:.1f},{base:.1f} L{pts[0][0]:.1f},{base:.1f}Z" fill="{sr["color"]}" '
                       'opacity=".25"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{sr["color"]}" stroke-width="{sr.get("width", 1.6)}"'
                   + (' stroke-dasharray="5 3"' if sr.get("dash") else "") + ' stroke-linejoin="round"/>')
    prev_x = -1e9
    for t, v, txt in sorted((a_ for a_ in ann if a_[0] >= start), key=lambda a_: a_[0]):
        x, y = X(t), Y(v)
        anchor = "end" if x > w * 0.8 else "start" if x < w * 0.2 else "middle"
        crowded = x - prev_x <= 70  # a label close to the previous one goes beside its point instead
        prev_x = x
        tx, ty = (x + 6, y + 4) if crowded else (x, y + (13 if v < (y0 + y1) / 2 else -6))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="var(--ink)"/>'
                   f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{"start" if crowded else anchor}" '
                   f'font-size="10.5" font-weight="700">{esc(txt)}</text>')
    legend = ""
    if len(series) > 1 or shade or hlines:
        items = "".join(f'<li><i style="background:{sr["color"]}"></i>{esc(sr["name"])}</li>' for sr in series)
        items += "".join(f'<li><i class="dash"></i>{esc(txt)}</li>' for _, txt in hlines)
        if shade:
            items += '<li><i style="background:var(--hatch);height:10px"></i>Recession</li>'
        legend = f'<ul class="legend" aria-hidden="true">{items}</ul>'
    svg = (f'<svg class="chart ts" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{"".join(out)}</svg>')
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    first = min(p[0] for sr in series for p in sr["pts"])
    last = max(p[0] for sr in series for p in sr["pts"])
    span = (_mx(last) - _mx(first)) / 12
    opts = [(lab, yrs) for lab, yrs in (("1Y", 1), ("5Y", 5), ("10Y", 10), ("30Y", 30)) if yrs < span - 0.5]
    if _mx(first) < _mx(start) - 1 or opts:
        opts.append(("All", 0))
    unit = "%" if yfmt.endswith("%") else ""
    cfg = {"series": [{k: sr[k] for k in ("name", "pts", "color") if k in sr} | {"area": bool(sr.get("area")),
                       "dash": bool(sr.get("dash"))} for sr in series],
           "y0": y0, "y1": y1, "start": start, "h": h, "w": w, "shade": sorted(shade), "hlines": [v for v, _ in hlines],
           "ann": [list(a_) for a_ in ann], "ydec": 1 if "1f" in yfmt else 0, "unit": unit, "dec": tip_dec,
           "every": ticks_every, "label": label}
    rng = ("<div class=\"rng\" role=\"group\" aria-label=\"Time period\" hidden>"
           + "".join(f'<button type="button" data-years="{yrs}" aria-pressed="false">{lab}</button>' for lab, yrs in opts)
           + "</div>") if len(opts) > 1 else ""
    data = json.dumps(cfg, separators=(",", ":")).replace("</", "<\\/")
    return (f'<figure class="fig" data-chart>{rng}<div class="plot">{svg}<div class="tip" hidden></div></div>{legend}{cap}'
            f'<p class="sr-only" aria-live="polite"></p><script type="application/json">{data}</script></figure>')


def probability_bar(p, base, label) -> str:
    """Horizontal bar 0–100% with a marker at the historical base rate."""
    if p is None:
        body = ('<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="6" stroke="var(--hatch)" stroke-width="3"/></pattern></defs>'
                '<rect x="0" y="6" width="300" height="12" rx="6" fill="url(#h)"/>')
        alt = f"{label}: not enough evidence to publish a probability."
    else:
        body = (f'<rect x="0" y="6" width="300" height="12" rx="6" fill="var(--chip)"/>'
                f'<rect x="0" y="6" width="{300 * p:.0f}" height="12" rx="6" fill="var(--brand2)"/>'
                f'<line x1="{300 * base:.0f}" x2="{300 * base:.0f}" y1="2" y2="22" stroke="var(--ink)" stroke-width="2"/>')
        alt = f"{label}: about {p:.0%}, compared with a historical average of {base:.0%}."
    return f'<svg class="chart" viewBox="0 0 300 24" role="img" aria-label="{esc(alt)}">{body}</svg>'


def diverging_bars(rows, unit="pp", width=None) -> str:
    """Responsive HTML bars around zero (rows: (label, value)); readable at any width."""
    vals = [abs(v) for _, v in rows if v is not None] or [1]
    top = max(vals)
    out = []
    for label, v in rows:
        if v is None:
            bar, txt = "", "n/a"
        else:
            pct = 50 * abs(v) / top
            side = f"left:50%;width:{pct:.1f}%" if v >= 0 else f"left:{50 - pct:.1f}%;width:{pct:.1f}%"
            bar = f'<span class="db-fill {"pos" if v >= 0 else "neg"}" style="{side}"></span>'
            txt = f"{v:+.1f}{unit}"
        out.append(f'<li><span class="db-label">{esc(label)}</span><span class="db-track" aria-hidden="true">'
                   f'<span class="db-zero"></span>{bar}</span><span class="db-val">{esc(txt)}</span></li>')
    return f'<ul class="dbars">{"".join(out)}</ul>'


def track_timeline(rows) -> str:
    """Forecast probability over time (line) with shaded months where the outcome occurred."""
    if not rows:
        return ""
    w, h, n = 640, 150, len(rows)
    x = lambda i: 30 + (w - 40) * i / max(1, n - 1)
    shade = "".join(f'<rect x="{x(i):.1f}" y="10" width="{(w - 40) / n + .6:.1f}" height="{h - 40}" fill="var(--warn)" opacity=".18"/>'
                    for i, r in enumerate(rows) if r["outcome"])
    pts = " ".join(f"{x(i):.1f},{10 + (h - 40) * (1 - r['probability']):.1f}" for i, r in enumerate(rows))
    ticks = "".join(f'<text x="{x(i):.1f}" y="{h - 12}" font-size="10" text-anchor="middle">{r["origin"][:4]}</text>'
                    for i, r in enumerate(rows) if r["origin"].endswith("-01") and int(r["origin"][:4]) % 10 == 0)
    grid = "".join(f'<line x1="30" x2="{w - 10}" y1="{10 + (h - 40) * (1 - g):.0f}" y2="{10 + (h - 40) * (1 - g):.0f}" stroke="var(--line)"/>'
                   f'<text x="2" y="{14 + (h - 40) * (1 - g):.0f}" font-size="10">{int(g * 100)}%</text>' for g in (0, .5, 1))
    hits = sum(r["outcome"] for r in rows)
    alt = (f"Monthly out-of-sample forecasts from {rows[0]['origin']} to {rows[-1]['origin']}. Shaded months ({hits}) "
           "are those where unemployment did rise at least 0.5 points within 12 months.")
    return (f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(alt)}">{grid}{shade}'
            f'<polyline points="{pts}" fill="none" stroke="var(--brand2)" stroke-width="1.6"/>{ticks}</svg>')


def calibration_chart(cal) -> str:
    s = 220
    pts = "".join(f'<circle cx="{20 + (s - 30) * c["mean_forecast"]:.1f}" cy="{s - 20 - (s - 30) * c["observed"]:.1f}" '
                  f'r="{4 + min(10, c["n"] / 25):.1f}" fill="var(--brand2)" opacity=".85"/>' for c in cal)
    alt = "; ".join(f"forecasts around {c['mean_forecast']:.0%} happened {c['observed']:.0%} of the time (n={c['n']})" for c in cal)
    return (f'<svg class="chart square" viewBox="0 0 {s} {s}" role="img" aria-label="Calibration: {esc(alt)}">'
            f'<rect x="20" y="10" width="{s - 30}" height="{s - 30}" fill="none" stroke="var(--line)"/>'
            f'<line x1="20" y1="{s - 20}" x2="{s - 10}" y2="10" stroke="var(--muted)" stroke-dasharray="4 4"/>{pts}'
            f'<text x="{s / 2}" y="{s - 4}" font-size="10" text-anchor="middle">Forecast probability</text>'
            f'<text x="8" y="{s / 2}" font-size="10" transform="rotate(-90 8 {s / 2})" text-anchor="middle">How often it happened</text></svg>')


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
def current_assessment(fred: dict):
    common = min(max(fred[n]) for n in ("INDPRO", "UNRATE", "CPIAUCSL"))
    sub = {"INDPRO": fred["INDPRO"], "UNRATE": fred["UNRATE"], "CPIAUCSL": fred["CPIAUCSL"]}
    month = shift(common, 1)
    a = assessment_at(sub, month)
    while a is None or a.get("cpi_inflation_12m_log_pct") is None:
        month = shift(month, -1)
        a = assessment_at(sub, month)
    view = interpret(a, "PASS", date.fromisoformat(a["assessment_date"]))
    return a, view


CRASH_EVIDENCE = "docs/evidence/v7_crash_research_2026-11-18.json"


def load_inputs(forecast_path, research_path, sectors_path, archive_path, fred_dir, crash_path=CRASH_EVIDENCE):
    fred = load_fred(Path(fred_dir))
    a, view = current_assessment(fred)
    archive = []
    with open(archive_path, newline="") as f:
        for r in csv.DictReader(f):
            archive.append({"target": r["target"], "h": int(r["horizon_months"]), "origin": r["origin"],
                            "probability": float(r["probability"]), "outcome": int(r["outcome"])})
    return {"forecast": json.loads(Path(forecast_path).read_text()),
            "research": json.loads(Path(research_path).read_text()),
            "sectors": json.loads(Path(sectors_path).read_text()),
            "archive": archive, "assessment": a, "view": view, "fred": fred,
            "crash": json.loads(Path(crash_path).read_text())}


def outlook_matrix(inp):
    """Every target × horizon with its published state (research onset included)."""
    rows = []
    gate = {(e["target"], e["horizon_months"]): e for e in inp["forecast"]["evaluations"]}
    for e in inp["research"]["recession_onset"]:
        gate[("recession_onset", e["horizon_months"])] = e
    outlooks = {(o["target"], o["horizon_months"]): o for o in inp["forecast"]["current_outlooks"]}
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        for h in (3, 6, 12):
            e = gate.get((target, h))
            o = outlooks.get((target, h), {})
            published = bool(e and e["publishable"] and o.get("state") == "Published")
            failed = [k for k, ok in (e or {}).get("gate_checks", {}).items() if not ok]
            rows.append({"target": target, "h": h, "published": published,
                         "p": o.get("probability") if published else None,
                         "text": o.get("probability_text") if published else None,
                         "band": o.get("band") if published else None,
                         "base": o.get("historical_base_rate") or (e and e["full_sample"]["model"]["events"] / max(1, e["full_sample"]["model"]["n"])),
                         "origin": o.get("forecast_origin"), "inputs": o.get("inputs"),
                         "failed": failed, "eval": e})
    return rows


def plain_reason(failed):
    if not failed:
        return "This outlook has not been evaluated yet."
    return "Not enough evidence yet: " + "; ".join(REASON_PLAIN.get(f, f) for f in failed) + "."


PRIORITY_CLASS = {"Worth researching now": "p-now", "Monitor": "p-mon", "Lower priority for now": "p-low"}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def mini_prob(p, base):
    if p is None:
        return '<span class="mini hatch" aria-hidden="true"></span>'
    return (f'<span class="mini" aria-hidden="true"><span class="fill" style="width:{100 * p:.0f}%"></span>'
            f'<span class="base" style="left:{100 * base:.0f}%"></span></span>')


def mini_rs(v, top):
    if v is None:
        return '<span class="mini" aria-hidden="true"></span>'
    w = 50 * min(1, abs(v) / top)
    bar = (f'<span class="pos" style="width:{w:.0f}%"></span>' if v >= 0
           else f'<span class="neg" style="left:{50 - w:.0f}%;width:{w:.0f}%"></span>')
    return f'<span class="mini rs" aria-hidden="true"><span class="zero"></span>{bar}</span>'


def fold(title, inner, open_=False):
    return f'<details class="fold"{" open" if open_ else ""}><summary>{esc(title)}</summary><div>{inner}</div></details>'


# --------------------------------------------------------------------------
# Market risk: shared pieces
# --------------------------------------------------------------------------
STATUS_TEXT = {"warning": "Warning on", "near": "Near trigger", "clear": "Clear", "not current": "Not current"}
STATUS_CLASS = {"warning": "st-warning", "near": "st-near", "clear": "st-clear", "not current": "st-nc"}
WHY = {
    "curve": "When short-term interest rates rise above long-term rates, markets expect weaker growth ahead. "
             "Inversions came before most U.S. recessions, often a year or more early.",
    "trend": "When the market slips below its 10-month average, selling has begun to outweigh buying. "
             "It tends to flag declines early in their course rather than far in advance.",
    "breadth": "Healthy advances are broad. When fewer industries are rising, gains rest on a narrow group of "
               "leaders and are more fragile.",
    "conditions": "A weekly summary of borrowing costs, lending and leverage across the financial system. "
                  "Tight conditions make shocks harder to absorb.",
    "credit": "Lenders demand more from riskier companies when they expect trouble. A fast widening signals stress.",
    "valuation": "High prices relative to long-run earnings leave more room to fall, but valuations can stay high "
                 "for years. It says “fragile”, not “when”.",
}
INDUSTRY = {"Agric": "Agriculture", "Food": "Food products", "Soda": "Soft drinks", "Beer": "Beer & liquor",
            "Smoke": "Tobacco", "Toys": "Recreation", "Fun": "Entertainment", "Books": "Publishing",
            "Hshld": "Consumer goods", "Clths": "Apparel", "Hlth": "Healthcare services", "MedEq": "Medical equipment",
            "Drugs": "Pharmaceuticals", "Chems": "Chemicals", "Rubbr": "Rubber & plastics", "Txtls": "Textiles",
            "BldMt": "Building materials", "Cnstr": "Construction", "Steel": "Steel", "FabPr": "Fabricated products",
            "Mach": "Machinery", "ElcEq": "Electrical equipment", "Autos": "Autos", "Aero": "Aircraft",
            "Ships": "Ships & railcars", "Guns": "Defense", "Gold": "Precious metals", "Mines": "Mining",
            "Coal": "Coal", "Oil": "Oil & gas", "Util": "Utilities", "Telcm": "Telecom", "PerSv": "Personal services",
            "BusSv": "Business services", "Hardw": "Computer hardware", "Softw": "Software", "Chips": "Semiconductors",
            "LabEq": "Lab equipment", "Paper": "Business supplies", "Boxes": "Packaging", "Trans": "Transportation",
            "Whlsl": "Wholesale", "Rtail": "Retail", "Meals": "Restaurants & hotels", "Banks": "Banks",
            "Insur": "Insurance", "RlEst": "Real estate", "Fin": "Finance", "Other": "Other"}


def num(v, unit="", sign=True, digits=1):
    if v is None:
        return "n/a"
    txt = f"{v:+.{digits}f}" if sign else f"{v:.{digits}f}"
    return txt.replace("-", "−") + unit


def day(d):
    return date.fromisoformat(d[:10]).strftime("%b %-d, %Y") if len(d) >= 10 else _fmt_month(d)


def status_pill(st):
    return f'<span class="st {STATUS_CLASS[st]}">{STATUS_TEXT[st]}</span>'


SHORT = {"curve": lambda w: f'{num(w["value"], digits=2)} pts; 12-month low {num(w.get("low12"), digits=2)}',
         "trend": lambda w: f'S&P 500 {num(w["value"], "%")} vs 10-month average',
         "breadth": lambda w: f'{w["value"]:.0f}% of industries above trend',
         "conditions": lambda w: f'{num(w["value"], digits=2)} (0 = average)',
         "credit": lambda w: f'{num(w["value"], sign=False, digits=2)} pts BAA spread',
         "valuation": lambda w: f'CAPE {w["value"]} is the latest available' if w.get("value") else "Data unavailable"}


def warn_value(w):
    if w["status"] == "not current":
        return f'CAPE {w["value"]} (latest available)' if w.get("value") else "Data unavailable"
    unit = w.get("unit", "")
    v = num(w["value"], "%" if unit == "%" else "", digits=1 if unit == "%" else 2)
    if w["key"] == "breadth":
        v = f'{w["value"]:.0f}%'
    return v


def record_text(w):
    r = w["record"]
    lift = r.get("lift_12m")
    return (f'Since {r["since"]}: when on, a 20% fall followed within a year about {lift:.1f}× as often as usual. '
            f'Missed {r["bears_missed"]} of {r["bears_total"]} bear markets; '
            f'{100 * (r["false_alarm_share"] or 0):.0f}% of warning months were false alarms.')


def counts(ws):
    tested = [w for w in ws if w["status"] != "not current"]
    return (len([w for w in tested if w["status"] == "warning"]), len([w for w in tested if w["status"] == "near"]),
            len(tested), [w for w in ws if w["status"] == "not current"])


def indexes_table(cur, cols=(("1m", "1 month"), ("from_52w_high", "From high"))):
    names = (("SP500", "S&P 500"), ("NASDAQCOM", "Nasdaq"), ("NASDAQ100", "Nasdaq-100"), ("DJIA", "Dow"))
    rows, dates = [], set()
    for k, lab in names:
        r = cur.get(k)
        if not isinstance(r, dict):
            continue
        dates.add(day(r["date"]))
        cells = "".join(f'<td class="{"" if r.get(c) is None else "neg" if r[c] < 0 else "pos"}">{num(r.get(c), "%")}</td>'
                        for c, _ in cols)
        rows.append(f'<tr><th scope="row">{lab}</th>{cells}</tr>')
    head = "".join(f'<th scope="col">{t}</th>' for _, t in cols)
    return (f'<div class="scroll" tabindex="0" role="region" aria-label="Index performance">'
            f'<table class="grid7"><caption class="sr-only">Index performance, daily closes</caption>'
            f'<thead><tr><th scope="col">Index</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'<p class="oneline"><small>Daily closes ({esc(" / ".join(sorted(dates)))}), FRED. “From high” = from the 1-year high.</small></p>')


def drawdown_chart(c, start, h=160, label_min=-40):
    dd = c["site"]["charts"]["drawdown"]
    bears = [b for b in c["bear_markets"] if b["peak"][:7] >= start and b["depth_pct"] <= label_min]
    ann = [(b["trough"][:7], b["depth_pct"], f'{b["peak"][:4]}: {num(b["depth_pct"], "%", digits=0)}') for b in bears]
    last = dd[-1]
    return ts_chart([{"name": "Decline from previous high", "pts": dd, "color": "var(--bad)", "area": True}],
                    y0=-90 if start < "1940" else -60, y1=0, start=start, h=h, shade=c["site"]["charts"]["recession_months"],
                    yfmt="{:.0f}%", ann=ann, label=f"U.S. total stock market: decline from its previous high, month-end, "
                    f"{start[:4]} to {_fmt_month(last[0])}. Largest declines labelled; recessions shaded.",
                    caption=f'Latest: {num(last[1], "%")} from its high ({_fmt_month(last[0])}). U.S. total market, total return, '
                            'month-end (Kenneth R. French data). Shaded: recessions.')



def _utc(ts):
    """'2026-11-18T18:09:32Z' -> 'Nov 18, 2026, 18:09 UTC'."""
    if not ts or len(ts) < 16:
        return ts or "n/a"
    return f"{day(ts[:10])}, {ts[11:16]} UTC"


KIND = {"tested": ("Tested warning", "st-warning"), "monitoring": ("Monitoring", "st-nc")}


def change_rows(items):
    return "".join(
        f'<li><div class="rowstatic"><span class="rname">{esc(c["title"])}</span>'
        f'<span class="st {"st-clear" if c["kind"] == "tested" and c["severity"] == "down" else KIND[c["kind"]][1]}">'
        f'{KIND[c["kind"]][0]}</span><span class="rsub">{esc(c["detail"])} · {esc(day(c["date"]) if c.get("date") else "")}'
        f'</span></div></li>' for c in items)


def changes_card(inp):
    mon = inp.get("monitor")
    if not mon or not mon.get("assessments"):
        return ""
    cur = mon["assessments"][-1]
    prev = mon["assessments"][-2] if len(mon["assessments"]) > 1 else None
    items, events = cur.get("changes", []), cur.get("events", [])
    head = (f'<p class="oneline"><small>Assessed {esc(_utc(cur["assessed_at_utc"]))} · data through '
            f'{esc(day(cur["market_data_through"]))}'
            + (f' (previous: {esc(day(prev["market_data_through"]))})' if prev else "") + "</small></p>")
    stale = f'<p class="note" data-through="{esc(cur["market_data_through"])}" hidden></p>'
    if not prev:
        body = '<p class="oneline">First market assessment. Changes appear after the next trading day.</p>'
    elif not items:
        body = '<p class="oneline">No meaningful changes since the previous assessment.</p>'
    else:
        body = f'<ul class="rows">{change_rows(items[:3])}</ul>' + (
            fold(f"{len(items) - 3} more change{'s' if len(items) > 4 else ''}", f'<ul class="rows">{change_rows(items[3:])}</ul>')
            if len(items) > 3 else "")
    ev = ('<p class="note" role="status"><strong>Event review:</strong> ' + esc("; ".join(events)) +
          '. Every warning sign was rechecked. Not a prediction.</p>') if events else ""
    whys = []
    for c in items:
        if c["why"] not in whys:
            whys.append(c["why"])
    why = fold("Why these changes matter", li_p(whys + [
        "“Tested warning” means a historically tested sign changed state. “Monitoring” means a descriptive threshold, "
        "not a predictor.", "Daily, weekly and monthly data each keep their own observation dates."]))
    return (f'<section class="card" aria-labelledby="chg"><h2 id="chg">What changed since the last market assessment?</h2>'
            f'{head}{stale}{ev}{body}{why}<p class="oneline"><a href="market-risk.html#week">This week’s interpretation →</a></p>'
            '</section>')


def weekly_card(inp):
    mon = inp.get("monitor")
    if not mon or not mon.get("weekly"):
        return ""
    wk = mon["weekly"][-1]
    rows = "".join(f'<li><strong>{esc(l_["topic"])}.</strong> {esc(l_["text"])}</li>' for l_ in wk["lines"])
    log = "".join(f'<li>{esc(_utc(a["assessed_at_utc"]))}: data through {esc(day(a["market_data_through"]))} — '
                  f'{len(a.get("changes", []))} change{"s" if len(a.get("changes", [])) != 1 else ""}'
                  + (" (baseline)" if a.get("baseline") else "") + "</li>" for a in reversed(mon["assessments"][-10:]))
    return (f'<section class="card" id="week" aria-labelledby="wk"><p class="eyebrow">Weekly interpretation</p>'
            f'<h2 id="wk">Week of {esc(day(wk["week"][0]))} to {esc(day(wk["week"][1]))}</h2>'
            f'<p class="oneline"><strong>{esc(wk["summary"])}</strong></p><ul class="clean">{rows}</ul>'
            + fold("Assessment log (latest 10)", f'<ul class="clean">{log}</ul>'
                   '<p class="oneline"><small>A new assessment is made only when new market data arrive; slower '
                   'indicators keep their own observation dates.</small></p>') + "</section>")



def home(inp, matrix):
    c = inp["crash"]
    site_ = c["site"]
    ws, cur, v, a = site_["warnings"], c["current"], inp["view"], inp["assessment"]
    on, near, tested, stale = counts(ws)
    w = {x["key"]: x for x in ws}
    headline = (f"{on} of {tested} tested warning signs {'is' if on == 1 else 'are'} on"
                + (f", and {near} {'is' if near == 1 else 'are'} close to {'its' if near == 1 else 'their'} trigger" if near else ""))
    rows = "".join(
        f'<li><a class="rowlink" href="market-risk.html#w-{x["key"]}"><span class="rname">{esc(x["title"])}</span>'
        f'{status_pill(x["status"])}<span class="rsub">{esc(SHORT[x["key"]](x))} · '
        f'{esc(day(x["date"]) if x.get("date") else "")}</span></a></li>' for x in ws)
    nas = cur.get("NASDAQCOM", {}) if isinstance(cur.get("NASDAQCOM"), dict) else {}
    vix = cur["volatility"].get("VIXCLS", {})
    size = cur.get("size_deciles_French", {})
    eg = w["valuation"].get("context_equity_to_gdp", {})
    concern, reassure = [], []
    if w["trend"]["status"] in ("warning", "near"):
        o = w["trend"].get("others", {}).get("Nasdaq Composite")
        concern.append(f'Trend: S&P 500 only {num(w["trend"]["value"], "%")} above its 10-month average'
                       + (f'; Nasdaq {num(o["gap_pct"], "%")} below' if o and o["gap_pct"] < 0 else "") + '.')
    if nas.get("from_52w_high") is not None and nas["from_52w_high"] <= -10:
        concern.append(f'Nasdaq {num(abs(nas["from_52w_high"]), "%", sign=False)} below its high: a tech-led correction.')
    if w["breadth"]["status"] in ("warning", "near"):
        concern.append(f'Breadth: only {w["breadth"]["value"]:.0f}% of industries above trend (trigger 40%).')
    if size.get("3m_Lo 10") is not None and size["3m_Lo 10"] < size["3m_Hi 10"]:
        concern.append(f'Small companies lagging large ones ({num(size["3m_Lo 10"], "%")} vs {num(size["3m_Hi 10"], "%")}, 3 months).')
    if isinstance(vix, dict) and vix.get("value", 0) >= 20:
        concern.append(f'Volatility (VIX) {vix["value"]:.1f}, up {vix["chg_3m"]:.0f}% in 3 months.')
    if eg.get("value"):
        concern.append(f'Stock value vs GDP highest since {eg["history_from"][:4]} (not yet a tested warning).')
    for k, txt in (("curve", "Yield curve not inverted"), ("credit", "Credit spreads narrow"),
                   ("conditions", "Financial conditions looser than average")):
        if w[k]["status"] == "clear":
            reassure.append(f'{txt} ({warn_value(w[k])}).')
    if v["condition"] == "Expanding":
        reassure.append("Economy expanding; unemployment steady.")
    raise_ = [f'{x["title"]}: {x["trigger"].lower()}.' for x in ws if x["status"] in ("near", "clear") and x.get("trigger")]
    ease = []
    if w["trend"]["status"] != "clear":
        ease.append("The S&P 500 and Nasdaq move clearly back above their 10-month averages.")
    if w["breadth"]["status"] != "clear":
        ease.append("More than 45% of industries rise back above their trend.")
    ease.append("Credit spreads stay narrow and financial conditions stay loose.")
    li = lambda xs: '<ul class="clean">' + "".join(f"<li>{esc(t)}</li>" for t in xs) + "</ul>"
    labor = {r["h"]: r for r in matrix if r["target"] == "labor_deterioration"}[12]
    ipg = c["site"]["charts"]["ip_growth"]
    secs = inp["sectors"]["sectors"]
    picks = sorted((x for x in secs if x["research_priority"] == "Worth researching now"),
                   key=lambda x: -(x["relative_strength_12m_pp"] or 0))
    srows = "".join(
        f'<li><a class="rowlink" href="sector-{x["slug"]}.html"><span class="rname">{esc(x["sector"])}</span>'
        f'<span class="rval">{x["relative_strength_12m_pp"]:+.0f} pts</span>'
        f'<span class="rsub">{esc(x["cycle_class"])} · past 12 months vs market</span></a></li>' for x in picks)
    body = (
        '<div class="stack">'
        '<section class="card hero" aria-labelledby="q"><p class="eyebrow">Stock-market warning check</p>'
        '<h1 id="q" class="hero-q">How vulnerable is the stock market to a major decline?</h1>'
        f'<p class="big" style="font-size:1.35rem;line-height:1.25">{esc(headline)}.</p>'
        f'<p class="oneline">Each sign came before past 20% declines more often than usual, but each also missed many and '
        f'gave false alarms. <strong>Not a crash probability.</strong></p>'
        f'<ul class="rows wgrid">{rows}</ul>'
        + (f'<p class="oneline"><small>{esc(", ".join(x["title"] for x in stale))}: not counted because the tested data are not current.</small></p>' if stale else "")
        + '<p class="oneline"><a href="market-risk.html">See the evidence →</a></p></section>'
        + changes_card(inp) +
        '<section class="card" aria-labelledby="cr"><h2 id="cr" class="sr-only">What concerns us and what reassures us</h2>'
        '<div class="two">'
        f'<div><h3>Concerning</h3>{li(concern)}</div><div><h3>Reassuring</h3>{li(reassure)}</div></div>'
        + fold("What would raise concern", li(raise_)) + fold("What would ease concern", li(ease))
        + fold("What this cannot predict", li([
            "When a decline will start, how deep it will be, or whether one happens at all.",
            "We tested a combined model of these signals: it was overconfident and no better than the long-run average, "
            "so we publish no crash probability or overall risk score.",
            "Sudden shocks (1987, 2020) gave little or no warning in these measures."]))
        + '</section>'
        '<div class="two">'
        f'<section class="card" aria-labelledby="mv"><div class="row-head"><h2 id="mv">Recent market moves</h2>'
        f'<a href="market-risk.html#indexes">More →</a></div>{indexes_table(cur)}</section>'
        '<section class="card" aria-labelledby="hist"><h2 id="hist">How deep past declines went</h2>'
        f'{drawdown_chart(c, "1950-01", h=150)}</section></div>'
        '<div class="two">'
        f'<section class="card" aria-labelledby="eco"><p class="eyebrow">Supporting context</p><div class="row-head">'
        f'<h2 id="eco">The economy: {esc(v["condition"])}</h2><a href="forecast.html">Economy →</a></div>'
        + ts_chart([{"name": "Industrial production, 12-month change", "pts": ipg, "color": "var(--brand2)"}],
                   y0=-20, y1=10, start="2012-01", h=120, yfmt="{:.0f}%", hlines=((0, "No change (0%)"),),
                   label=f"Industrial production, 12-month change, 2012 to {_fmt_month(ipg[-1][0])}.",
                   caption=f"Industrial production, 12-month change (FRED), through {_fmt_month(ipg[-1][0])}.")
        + f'<p class="oneline">Job market weakens within 12 months: <strong>{esc(labor["text"] or "not enough evidence")}</strong>'
          f'{" (" + esc(labor["band"]).lower() + ")" if labor["band"] else ""}. Recession outlooks: not enough evidence yet.</p></section>'
        f'<section class="card" aria-labelledby="sec"><p class="eyebrow">Where to look</p><div class="row-head">'
        f'<h2 id="sec">Sectors worth researching</h2><a href="sectors.html">All 11 →</a></div><ul class="rows">{srows}</ul>'
        '<p class="oneline"><small>Research guidance, not a recommendation.</small></p></section></div>'
        '</div>')
    return page("Market Risk Check", "home", body, "Is the stock market vulnerable to a major decline? Historically tested warning signs, with their records.")


def market_page(inp):
    c = inp["crash"]
    site_, cur = c["site"], c["current"]
    ws, ch = site_["warnings"], site_["charts"]
    w = {x["key"]: x for x in ws}
    signal_charts = {
        "curve": lambda: ts_chart([{"name": "10-year minus 3-month Treasury", "pts": ch["curve"], "color": "var(--brand2)"}],
                                  y0=-4, y1=5, start="1960-01", h=130, yfmt="{:.0f}", hlines=((0, "Inverted when below this line (0)"),),
                                  shade=ch["recession_months"], label="Yield curve, 10-year minus 3-month, 1960 to date.",
                                  caption="Points; monthly averages (FRED GS10 − TB3MS)."),
        "credit": lambda: ts_chart([{"name": "BAA corporate minus 10-year Treasury", "pts": ch["credit"], "color": "var(--warn)"}],
                                   y0=0, y1=6, start="1960-01", h=130, yfmt="{:.0f}", hlines=((2.5, "Stress threshold (2.5 points)"),),
                                   shade=ch["recession_months"], label="Corporate credit spread, BAA minus 10-year Treasury, 1960 to date.",
                                   caption="Points; monthly (FRED BAA − GS10)."),
        "conditions": lambda: ts_chart([{"name": "Chicago Fed NFCI", "pts": ch["nfci"], "color": "var(--brand2)"}],
                                       y0=-1.5, y1=3, start="1971-01", h=130, yfmt="{:.1f}", hlines=((0, "Average (0); above = tighter"),),
                                       shade=ch["recession_months"], label="Chicago Fed National Financial Conditions Index, 1971 to date.",
                                       caption="Monthly average of the weekly index (FRED NFCI)."),
        "breadth": lambda: ts_chart([{"name": "Industries above trend", "pts": [[m, 100 * v] for m, v in ch["breadth"]],
                                      "color": "var(--good)"}], y0=0, y1=100, start="2000-01", h=130, yfmt="{:.0f}%",
                                    hlines=((40, "Weak-breadth threshold (40%)"),), shade=ch["recession_months"],
                                    label="Share of 49 industries above their 10-month average, 2000 to date.",
                                    caption="Kenneth R. French 49 industry portfolios, monthly."),
        "trend": lambda: ts_chart([{"name": n, "pts": [[d, 100 * v / pts[0][1]] for d, v in pts], "color": col}
                                   for (n, pts, col) in (("S&P 500", ch["index_1y"]["SP500"], "var(--brand2)"),
                                                         ("Nasdaq", ch["index_1y"]["NASDAQCOM"], "var(--bad)"),
                                                         ("Dow", ch["index_1y"]["DJIA"], "var(--good)")) if pts],
                                  y0=75, y1=125, start=ch["index_1y"]["SP500"][0][0], h=140, yfmt="{:.0f}",
                                  hlines=((100, "Starting level (100)"),), ticks_every=1,
                                  label=f'S&P 500, Nasdaq and Dow, {day(ch["index_1y"]["SP500"][0][0])} to '
                                        f'{day(ch["index_1y"]["SP500"][-1][0])}, rebased to 100.',
                                  caption=f'Daily closes (FRED), rebased to 100, through {day(ch["index_1y"]["SP500"][-1][0])}.'),
        "valuation": lambda: "",
    }
    cards = []
    for x in ws:
        r = x["record"]
        extra = ""
        if x["key"] == "trend":
            extra = "".join(f'<li>{esc(k)}: {num(o["gap_pct"], "%")} vs its 10-month average ({day(o["date"])})</li>'
                            for k, o in x.get("others", {}).items())
            extra = f'<ul class="clean">{extra}</ul>' if extra else ""
        cards.append(
            f'<section class="card" id="w-{x["key"]}" aria-labelledby="h-{x["key"]}"><div class="row-head">'
            f'<h2 id="h-{x["key"]}">{esc(x["title"])}</h2>{status_pill(x["status"])}</div>'
            f'<p class="oneline"><strong>{esc(warn_value(x))}</strong> {esc(x.get("detail", "").replace(" -", " −"))}'
            + (f' · {esc(day(x["date"]))} ({esc(x["frequency"])})' if x.get("date") else "") + "</p>"
            + extra + signal_charts[x["key"]]()
            + f'<p class="oneline">{esc(WHY[x["key"]])}</p>'
            + fold("Trigger and track record", f'<ul class="clean"><li>Warning when: {esc(x["trigger"])}'
                   + (f' (near: {esc(x["near_rule"])})' if x.get("near_rule") else "") + "</li>"
                   f'<li>{esc(record_text(x))}</li><li>Median lead from first warning to the market peak: '
                   f'{r.get("median_lead_months")} months.</li><li>Source: {esc(x.get("source", ""))}.</li></ul>')
            + "</section>")
    cmp_ = site_["compare_today"]
    t = w
    tr = cur.get("US_total_market_French", {})
    rows = [
        ("Yield curve, lowest in 12 months (points)", num(cmp_["curve_min12"]["median_at_peaks"], digits=2),
         num(t["curve"]["low12"], digits=2), _fmt_month(t["curve"]["date"])),
        ("Credit spread (points)", num(cmp_["credit"]["median_at_peaks"], sign=False, digits=2),
         num(t["credit"]["value"], sign=False, digits=2), _fmt_month(t["credit"]["date"])),
        ("Market vs 10-month average", num(100 * cmp_["trend_gap"]["median_at_peaks"], "%"),
         num(t["trend"]["value"], "%") + " (S&P 500)", day(t["trend"]["date"])),
        ("Industries above trend", f'{100 * cmp_["breadth"]["median_at_peaks"]:.0f}%', f'{t["breadth"]["value"]:.0f}%',
         _fmt_month(t["breadth"]["date"])),
        ("12-month market return", num(cmp_["ret12"]["median_at_peaks"], "%"), num(tr.get("12m"), "%"),
         _fmt_month(tr.get("date", "2026-09")[:7])),
    ]
    compare = ("<div class=\"scroll\" tabindex=\"0\" role=\"region\" aria-label=\"Today versus past peaks\"><table class=\"grid7\"><caption class=\"sr-only\">Today compared with the median of past bear-market peaks"
               "</caption><thead><tr><th scope=\"col\">Measure</th><th scope=\"col\">At past peaks (median)</th>"
               "<th scope=\"col\">Today</th></tr></thead><tbody>"
               + "".join(f'<tr><th scope="row" style="white-space:normal">{esc(a_)}</th><td>{esc(b_)}</td><td>{esc(c_)}'
                         f'<br><small>{esc(d_)}</small></td></tr>' for a_, b_, c_, d_ in rows) + "</tbody></table></div>")
    mat = site_["warning_matrix"]
    cols = [x["title"] for x in ws]
    short = {"Yield curve": "Curve", "Market trend": "Trend", "Market breadth": "Breadth",
             "Financial conditions": "Cond.", "Credit spreads": "Credit", "Valuation": "Value"}
    bears = {b["peak"][:7]: b for b in c["bear_markets"]}
    mrows = []
    for pk in sorted(k for k in mat if k >= "1954"):
        cells = []
        for col in cols:
            v = mat[pk].get(col)
            cells.append('<td><span class="off">–</span><span class="sr-only">no data</span></td>' if v is None else
                         f'<td><span class="{"on" if v else "off"}" aria-hidden="true">{"●" if v else "○"}</span>'
                         f'<span class="sr-only">{"warned" if v else "no warning"}</span></td>')
        b = bears.get(pk, {})
        mrows.append(f'<tr><th scope="row">{pk[:4]}<br><small>{num(b.get("depth_pct"), "%", digits=0)}</small></th>{"".join(cells)}</tr>')
    matrix_html = (f'<div class="scroll" tabindex="0" role="region" aria-label="Warning record before past bear markets">'
                   f'<table class="grid7"><caption class="sr-only">Was each warning on in the 12 months before each bear-market '
                   f'peak?</caption><thead><tr><th scope="col">Peak</th>'
                   + "".join(f'<th scope="col" title="{esc(cn)}">{esc(short[cn])}</th>' for cn in cols)
                   + f'</tr></thead><tbody>{"".join(mrows)}</tbody></table></div>')
    lead = cur.get("industries_French", {})
    lbars = diverging_bars([(INDUSTRY.get(n, n), v) for n, v in lead.get("leaders_12m", []) + lead.get("laggards_12m", [])],
                           unit="%")
    size = cur.get("size_deciles_French", {})
    models = [c[k] for k in ("model_T12_core", "model_T6_core", "model_T12_with_cape", "model_T6_with_cape")]
    mtxt = "; ".join(f'{m["horizon_months"]} months: skill {m["full_sample"]["bss_vs_base_rate"]:+.2f}, '
                     f'ranking {m["full_sample"]["auc"]:.2f}' for m in models)
    body = (
        '<h1>Market risk</h1><p class="lede">Warning signs that came before past major declines, measured today, with their '
        'track records. Market data are daily or weekly; economic conclusions are monthly.</p><div class="stack">'
        + weekly_card(inp)
        + '<div class="two">' + "".join(cards) + "</div>"
        + '<section class="card" aria-labelledby="cmp"><h2 id="cmp">Today versus past market peaks</h2>'
        f'<p class="muted oneline">Median of {cmp_["credit"]["n"]} U.S. bear-market peaks since 1953, compared with the latest data.</p>'
        f'{compare}<p class="oneline"><small>Past peaks use the total U.S. market (monthly); today’s trend uses S&amp;P 500 daily '
        'closes. Breadth today is far weaker than at a typical past peak; credit and the yield curve look calmer.</small></p></section>'
        '<section class="card" aria-labelledby="mx"><h2 id="mx">Which warnings came before past bear markets</h2>'
        '<p class="muted oneline">● = on at some point in the 12 months before the peak. No warning caught every decline.</p>'
        f'{matrix_html}</section>'
        '<section class="card" id="history" aria-labelledby="dd"><h2 id="dd">A century of declines</h2>'
        f'{drawdown_chart(c, "1926-07", h=190)}'
        + fold("All 16 bear markets since 1926", '<ul class="clean">' + "".join(
            f'<li>{_fmt_month(b["peak"][:7])} to {_fmt_month(b["trough"][:7])}: {num(b["depth_pct"], "%", digits=0)} '
            f'over {b["months_peak_to_trough"]} months</li>' for b in c["bear_markets"]) + "</ul>")
        + '</section>'
        '<section class="card" id="indexes" aria-labelledby="ix"><h2 id="ix">Index performance</h2>'
        + indexes_table(cur, (("1m", "1m"), ("3m", "3m"), ("12m", "12m"), ("from_52w_high", "From high")))
        + '<p class="oneline"><small>FRED keeps about one year of S&amp;P 500 history, so its 12-month change is unavailable.</small></p>'
        '<h3>Leaders and laggards, past 12 months</h3>' + lbars
        + f'<p class="oneline"><small>Kenneth R. French industry portfolios through {_fmt_month(lead.get("month", "2026-09"))}. '
          f'Smallest 10% of companies: {num(size.get("3m_Lo 10"), "%")} over 3 months; largest 10%: {num(size.get("3m_Hi 10"), "%")}.</small></p>'
        '</section>'
        '<section class="card" aria-labelledby="dv"><h2 id="dv">When the economy and the market disagree</h2>'
        + ts_chart([{"name": "Industrial production, 12-month change", "pts": ch["ip_growth"], "color": "var(--brand2)"}],
                   y0=-20, y1=10, start="1985-01", h=120, yfmt="{:.0f}%", hlines=((0, "No change (0%)"),), shade=ch["recession_months"],
                   label="Industrial production, 12-month change, 1985 to date.")
        + drawdown_chart(c, "1985-01", h=120, label_min=-30)
        + '<p class="oneline">The market fell 20% or more in 1987, 1998, 2018 and 2022 while production was still growing. '
          'An expanding economy does not rule out a major decline.</p></section>'
        '<section class="card">' + fold("Why we publish no crash probability", li_p([
            f"We tested a combined model of these warnings out of sample, without hindsight: {mtxt}.",
            "Every version was worse than simply using the long-run average and was badly overconfident, so it is not published.",
            "Each warning’s record above is a historical frequency, not today’s odds.",
            "Valuation (Shiller CAPE) is excluded from the count until a current, licensed series is available."]))
        + fold("Data and method", li_p([
            "Declines: U.S. total stock market, daily total return, Kenneth R. French Data Library (1926 onward).",
            "A bear market is a fall of 20% or more from a previous high before that high is regained.",
            "Warnings use fixed thresholds set before testing (docs/V7_PREREGISTRATION_CRASH_RESEARCH.md).",
            "Market and rate data: FRED (S&P 500, Nasdaq, Dow, VIX, Treasury and BAA yields, NFCI).",
            "Daily and weekly observations are shown with their dates; they do not change the monthly economic conclusions."]))
        + '</section></div>')
    return page("Market Risk", "market", body, "Historically tested stock-market warning signs, today’s readings and their records.")


def li_p(items):
    return '<ul class="clean">' + "".join(f"<li>{esc(t)}</li>" for t in items) + "</ul>"


def forecast(inp, matrix):
    pub = next((r for r in matrix if r["published"]), None)
    names = {"term_spread": ("Yield curve", "10-year minus 3-month rate; positive is historically calmer."),
             "term_spread_min12": ("Lowest yield curve, past year", "Below zero (inverted) has preceded downturns."),
             "credit_spread": ("Corporate borrowing premium", "Wider means lenders see more risk."),
             "unemp_rise": ("Unemployment rise from yearly low", "0.5 or more has signalled trouble."),
             "payrolls_6m": ("Job growth, 6 months (%)", "Shrinking payrolls are a warning sign.")}
    detail = ""
    if pub:
        inputs = "".join(f'<li><div class="rowstatic"><span class="rname">{esc(names[k][0])}</span><span class="rval">{v:.2f}</span>'
                         f'<span class="rsub">{esc(names[k][1])}</span></div></li>'
                         for k, v in (pub["inputs"] or {}).items() if k in names)
        detail = (f'<section class="card" aria-labelledby="pub"><p class="eyebrow">Published outlook · data through {esc(pub["origin"])}</p>'
                  f'<h2 id="pub">{esc(TARGET_PLAIN[pub["target"]])} within {pub["h"]} months: {esc(pub["text"])}</h2>'
                  f'{probability_bar(pub["p"], pub["base"], "Job market weakens within 12 months")}'
                  f'<p class="oneline"><strong>{esc(pub["band"])}</strong> compared with the long-run average of {pub["base"]:.0%} (the vertical line).</p>'
                  + fold("What the model is reading", f'<ul class="rows">{inputs}</ul>') + '</section>')
    groups = []
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        rs = [r for r in matrix if r["target"] == target]
        badges = "".join(f'<span class="b ok">{r["h"]} months: {esc(r["text"])}</span>' if r["published"] else
                         f'<span class="b">{r["h"]} months<span class="sr-only">: not enough evidence</span></span>'
                         for r in rs)
        failed = sorted({f for r in rs if not r["published"] for f in r["failed"]})
        why = plain_reason(failed) if failed else "Published: it passed our test."
        if failed and any(r["published"] for r in rs):
            gaps = " and ".join(f'{r["h"]}' for r in rs if not r["published"])
            why = f"{gaps} months — " + why[:1].lower() + why[1:]
        groups.append(f'<li><div class="rowstatic"><span class="rname">{esc(TARGET_LABEL[target])}</span>'
                      f'<span class="rsub">{esc(TARGET_PLAIN[target])} within 3, 6 or 12 months.</span>'
                      f'<span class="badges" style="grid-column:1/-1;justify-content:flex-start">{badges}</span>'
                      f'<span class="rsub">{esc(why)}</span></div></li>')
    v, a = inp["view"], inp["assessment"]
    lst = lambda items: "<ul class=\"clean\">" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"
    ipg = inp["crash"]["site"]["charts"]["ip_growth"]
    hl = v["headline"].replace("Our assessment: ", "")
    cond = (f'<section class="card hero" aria-labelledby="now"><p class="eyebrow">Economic conditions · data through '
            f'{esc(_fmt_month(a["sources"]["UNRATE"]["latest_used_month"]))}</p>'
            f'<h2 id="now" class="big">{esc(v["condition"])}</h2>'
            f'<p class="oneline"><span class="chip">Direction: {esc(v["direction"])}</span><span class="chip">Evidence: {esc(v["evidence_confidence"])}</span></p>'
            f'<p class="oneline">{esc(hl[:1].upper() + hl[1:])}</p>'
            + ts_chart([{"name": "Industrial production, 12-month change", "pts": ipg, "color": "var(--brand2)"}],
                       y0=-20, y1=10, start="2000-01", h=130, yfmt="{:.0f}%", hlines=((0.5, "Expansion threshold (+0.5%)"),),
                       shade=inp["crash"]["site"]["charts"]["recession_months"],
                       label=f"Industrial production, 12-month change, 2000 to {_fmt_month(ipg[-1][0])}.",
                       caption="Industrial production (FRED). Shaded: recessions.")
            + '<p class="oneline"><small>This describes economic activity, not stock-market risk; see '
              '<a href="market-risk.html">Market risk</a>. "Evidence" rates data quality, not the odds of any event.</small></p>'
            + fold("Why we think this", lst(v["drivers"]))
            + fold("What could prove us wrong", lst(v["counterevidence"] + v.get("evidence_gaps", [])))
            + fold("What would change our view", lst(v["reversal_conditions"])) + "</section>")
    body = (
        '<h1>Economy</h1><p class="lede">Where the U.S. economy stands, and outlooks that are tested against history before we '
        'publish them. If an outlook fails, we say so instead of showing a number.</p>'
        f'<div class="stack">{cond}{detail}'
        f'<section class="card" aria-labelledby="all"><div class="row-head"><h2 id="all">All outlooks</h2><a href="track-record.html">Test results →</a></div>'
        f'<ul class="rows">{"".join(groups)}</ul></section></div>')
    return page("Economy", "forecast", body, "Economic conditions and tested 3-, 6- and 12-month economic outlooks.")

def sectors_page(inp):
    order = ("Worth researching now", "Monitor", "Lower priority for now")
    items = inp["sectors"]["sectors"]
    top = max(abs(x["relative_strength_12m_pp"] or 0) for x in items) or 1
    test = inp["sectors"]["relative_strength_test"]
    groups = []
    for pr in order:
        xs = sorted((x for x in items if x["research_priority"] == pr), key=lambda x: -(x["relative_strength_12m_pp"] or 0))
        if not xs:
            continue
        rows = "".join(
            f'<li><a class="rowlink" href="sector-{x["slug"]}.html"><span class="rname">{esc(x["sector"])}</span>'
            f'<span class="rval">{"n/a" if x["relative_strength_12m_pp"] is None else f"{x["relative_strength_12m_pp"]:+.0f} pts"}</span>'
            f'<span class="rsub">{esc(x["cycle_class"])} · backdrop {esc(x["economic_backdrop"]).lower()}</span>'
            f'{mini_rs(x["relative_strength_12m_pp"], top)}</a></li>' for x in xs)
        groups.append(f'<section class="card" aria-labelledby="g-{PRIORITY_CLASS[pr]}"><div class="row-head">'
                      f'<h2 id="g-{PRIORITY_CLASS[pr]}"><span class="pill {PRIORITY_CLASS[pr]}">{esc(pr)}</span></h2>'
                      f'<small>{len(xs)} sector{"s" if len(xs) != 1 else ""}</small></div><ul class="rows">{rows}</ul></section>')
    method = ('<ul class="clean">'
              '<li><strong>Backdrop</strong>: how the sector did versus the market in past recessions and expansions, matched to today\'s economy.</li>'
              f'<li><strong>Recent strength</strong> (bars: past 12 months vs market, skipping the latest month) counts because our pre-registered test found it has persisted: '
              f'{test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months, t={test["t_stat"]}, {test["periods"]} periods since {test["first_period"][:4]}.</li>'
              '<li>"Worth researching now" means the evidence points the same way. It is never a recommendation.</li>'
              '<li>Investment attractiveness needs current, licensed valuation data, which is not yet available, so every sector shows "Insufficient evidence".</li>'
              '<li>Sectors are approximated with Kenneth R. French industry portfolios, not official GICS indices.</li></ul>')
    body = (
        '<h1>Sectors</h1>'
        f'<p class="lede">Which sectors deserve research in today\'s <strong>{esc(inp["view"]["condition"]).lower()}</strong> economy, '
        f'based on cycle behaviour and recent strength (to {esc(inp["sectors"]["as_of_month"])}). Not a buy or sell recommendation.</p>'
        f'<div class="stack">{"".join(groups)}<section class="card">{fold("How sectors are ranked", method)}</section></div>')
    return page("Sectors", "sectors", body, "Evidence-based research guidance for all 11 market sectors.")

def sector_detail(x, inp):
    sens, val = x["sensitivities"], x["valuation_context"]
    bars = diverging_bars([("In recessions", sens["recession_excess_pct_per_year"]),
                           ("In expansions", sens["expansion_excess_pct_per_year"]),
                           ("High inflation", sens["high_inflation_excess_pct_per_year"]),
                           ("Low inflation", sens["low_inflation_excess_pct_per_year"])], unit="%/yr")
    sup = "".join(f"<li>{esc(t)}</li>" for t in x["supports"]) or "<li>No strong supporting evidence right now.</li>"
    ch = "".join(f"<li>{esc(t)}</li>" for t in x["challenges"]) or "<li>No major contrary evidence flagged.</li>"
    wc = "".join(f"<li>{esc(t)}</li>" for t in x["what_would_change"])
    rate = sens["rate_beta_pct_per_pp"]
    vrow = ("not available" if val["forward_pe_median"] is None else
            f'{val["forward_pe_median"]} vs market {val["market_forward_pe"]} ({val["forward_pe_vs_market"]:+.0%})')
    rs = x["relative_strength_12m_pp"]
    behaved = (f'<p class="muted oneline">Average yearly return vs the market, {esc(sens["period"])}.</p>{bars}'
               f'<p>Each 1-point rise in the 10-year yield: {"n/a" if rate is None else f"{rate:+.1f}%"} relative return (monthly).</p>')
    priced = (f'<p><strong>{esc(x["investment_attractiveness"])}.</strong> {esc(x["attractiveness_reason"])}</p>'
              f'<p>Forward P/E: {esc(vrow)}. Expected 5-year earnings growth: '
              f'{"n/a" if val["expected_growth_5y_median_pct"] is None else str(val["expected_growth_5y_median_pct"]) + "%"}.</p>'
              f'<p><small>{esc(val["vintage"])}. Source: Aswath Damodaran, NYU Stern.</small></p>')
    method = (f'<p>Sector proxy: equal-weighted Kenneth R. French industry portfolios ({esc(", ".join(x["proxy_industries"]))}). '
              f'Relative strength as of {esc(x["relative_strength_as_of"])}. Recession months follow NBER dating. Educational research, not investment advice.</p>')
    body = (
        f'<p class="oneline"><a href="sectors.html">← All sectors</a></p><h1>{esc(x["sector"])}</h1>'
        f'<p><span class="pill {PRIORITY_CLASS[x["research_priority"]]}">{esc(x["research_priority"])}</span> '
        f'<span class="chip">{esc(x["cycle_class"])}</span><span class="chip">Backdrop: {esc(x["economic_backdrop"])}</span>'
        f'<span class="chip">12 months: {"n/a" if rs is None else f"{rs:+.1f} pts vs market"}</span></p>'
        '<div class="grid cols-2">'
        f'<section class="card"><h2>Why it may deserve attention</h2><ul class="clean">{sup}</ul></section>'
        f'<section class="card"><h2>What argues against it</h2><ul class="clean">{ch}</ul></section>'
        f'<section class="card"><h2>What would change this view</h2><ul class="clean">{wc}</ul><p class="oneline"><strong>Watch:</strong> {esc(x["watch"])}</p></section>'
        '<section class="card"><h2 class="sr-only">More evidence</h2>'
        + fold("How it has behaved", behaved) + fold("Is it attractively priced?", priced)
        + fold("When the usual pattern failed", f'<p>{esc(x["contrary_case"])}</p>') + fold("Data and method", method)
        + '</section></div>')
    return page(x["sector"], "sectors", body, f"Economic exposure and research evidence for the {x['sector']} sector.")

def track_page(inp, matrix):
    lab = sorted((r for r in inp["archive"] if r["target"] == "labor_deterioration" and r["h"] == 12), key=lambda r: r["origin"])
    ev = next(e for e in inp["forecast"]["evaluations"] if e["target"] == "labor_deterioration" and e["horizon_months"] == 12)
    fr = next(e for e in inp["research"]["first_release_labor_robustness"] if e["horizon_months"] == 12)
    m, f = ev["full_sample"]["model"], fr["full_sample"]["model"]
    rows = []
    for target in ("labor_deterioration", "recession_onset", "recession", "inflation_rising"):
        rs = [r for r in matrix if r["target"] == target and r["eval"]]
        badges = "".join(
            f'<span class="b{" ok" if r["published"] else ""}">{r["h"]}m <span aria-hidden="true">{"✓" if r["published"] else "✗"}</span>'
            f'<span class="sr-only">{" passes" if r["published"] else " fails"}</span></span>' for r in rs)
        detail = "; ".join(
            f'{r["h"]}m: skill {r["eval"]["full_sample"]["model"]["bss_vs_base_rate"]:+.2f}, ranking {r["eval"]["full_sample"]["model"]["auc"]:.2f}'
            + ("" if r["published"] else " — " + ", ".join(CHECK_SHORT.get(k, k) for k in r["failed"])) for r in rs)
        rows.append(f'<li><div class="rowstatic"><span class="rname">{esc(TARGET_LABEL[target])}</span><span class="badges">{badges}</span>'
                    f'<span class="rsub">{esc(detail)}</span></div></li>')
    test = inp["sectors"]["relative_strength_test"]
    notes = ('<ul class="clean">'
             '<li>The recession-start outlook was registered in advance and evaluated once; it ranks risk well but is too confident, so it is not published.</li>'
             '<li>We added one recalibration step after our first test showed overconfidence — a data-snooping risk we disclose.</li>'
             '<li>Only a handful of recessions since 1972, so recession results are uncertain.</li>'
             f'<li>Sector recent-strength signal: {test["mean_spread_pp_per_6m"]:+.1f} pts per 6 months over {test["periods"]} periods '
             f'(t={test["t_stat"]}; weaker in recent decades: {test["first_half_mean"]:+.1f} then {test["second_half_mean"]:+.1f}).</li></ul>')
    body = (
        '<h1>Track Record</h1><p class="lede">How each outlook would have performed in the past, using only information available at the time. Failures included.</p>'
        '<div class="stack">'
        '<section class="card" aria-labelledby="lab"><p class="eyebrow">Our published outlook</p><h2 id="lab">Job market weakens within 12 months</h2>'
        f'{track_timeline(lab)}'
        f'<p class="oneline">Since {esc(ev["evaluation_start"][:4])}: skill <strong>{m["bss_vs_base_rate"]:+.2f}</strong>, ranking <strong>{m["auc"]:.2f}</strong>, '
        f'{m["episodes"]} episodes. On data as first published: {f["bss_vs_base_rate"]:+.2f} / {f["auc"]:.2f} — still passes.</p>'
        + fold("Do our probabilities mean what they say?", calibration_chart(ev["calibration"])
               + '<p class="muted">Dots near the dashed line: forecasts of 40% came true about 40% of the time.</p>')
        + '</section>'
        '<section class="card" aria-labelledby="tests"><h2 id="tests">Every outlook we test</h2>'
        '<p class="muted oneline">Skill above 0 beats the long-run average; ranking runs from 0.5 (coin flip) to 1.0.</p>'
        f'<ul class="rows">{"".join(rows)}</ul></section>'
        f'<section class="card"><h2 class="sr-only">Notes and data</h2>{fold("Honest notes", notes)}'
        '<p class="oneline"><a href="forecast_archive.csv">Download every past forecast (CSV)</a></p></section></div>')
    return page("Track Record", "forecast", body, "Historical performance of every outlook, including failures.")

def research_page(inp):
    body = (
        '<h1>Research &amp; Data</h1><p class="lede">Methods, sources and evidence behind every number on this site.</p>'
        '<section class="card">'
        '<details class="fold" open><summary>How the market warning check works</summary><div><ul class="clean">'
        '<li>Six warning signs were chosen and given fixed thresholds before testing: yield curve, market trend, breadth, financial conditions, credit spreads and valuation.</li>'
        '<li>Each was checked against every U.S. bear market (a fall of 20% or more) since 1926, using only information available at the time. We report how often a decline followed, the bear markets it missed and its false alarms.</li>'
        '<li>A combined model of these warnings failed our out-of-sample test, so no crash probability or overall risk score is published; the homepage counts warnings, nothing more.</li>'
        '<li>Valuation is shown but not counted while the long-history series (Shiller CAPE) is not current.</li></ul></div></details>'
        '<details class="fold"><summary>How the outlooks work</summary><div><ul class="clean">'
        '<li>A small logistic model reads the yield curve, corporate borrowing premium, unemployment trend and job growth.</li>'
        '<li>It is re-fitted once a year using only past data, then tested month by month from 1972 against the long-run average, a yield-curve-only model and our earlier descriptive rules.</li>'
        '<li>Market data are used for the current month; government data only once published (one-month lag). Recession dates are used only to score.</li>'
        '<li>An outlook is published only if it beats the average (skill ≥ 0.05), ranks risk well (≥ 0.70), has at least 3 episodes and is not overconfident.</li></ul></div></details>'
        '<details class="fold"><summary>How sectors are assessed</summary><div><ul class="clean">'
        '<li>Economic sensitivity: each sector\'s return versus the market in recessions, expansions, high-inflation months and when the 10-year yield changes, since 1953.</li>'
        '<li>Recent strength: 12-month return versus the market, skipping the latest month; pre-registered persistence test.</li>'
        '<li>Valuation and earnings: Damodaran annual data shown as dated context. A rating needs current, licensed data, so attractiveness stays "not enough evidence".</li></ul></div></details>'
        '<details class="fold"><summary>Data sources and attribution</summary><div><ul class="clean">'
        '<li>Federal Reserve Bank of St. Louis — FRED and ALFRED (economic data, first releases).</li>'
        '<li>Kenneth R. French Data Library, Tuck School of Business at Dartmouth — industry portfolio and market returns.</li>'
        '<li>Aswath Damodaran, NYU Stern — US industry P/E and expected growth (annual).</li>'
        '<li>NBER — U.S. business-cycle dates (scoring and chart shading only).</li>'
        '<li>Kenneth R. French Data Library — daily U.S. total-market returns since 1926 and size portfolios (market declines, breadth, small vs large).</li>'
        '<li>FRED — S&amp;P 500, Nasdaq, Dow and VIX daily closes; Chicago Fed NFCI; Federal Reserve Z.1 equity values; IMF commodity prices.</li>'
        '<li>Robert Shiller’s stock-market data (public mirror) — CAPE history to 2023-09.</li></ul></div></details>'
        '<details class="fold"><summary>Limitations</summary><div><ul class="clean">'
        '<li>Most history uses today\'s revised data; the job-market outlook was re-checked on data as first published.</li>'
        '<li>Few recessions since 1972; recession outlooks remain unpublished.</li>'
        '<li>Sector figures use industry proxies, not official sector indices.</li>'
        '<li>Educational research, not personalized investment advice.</li></ul></div></details>'
        '<details class="fold"><summary>Pre-registration and evidence files</summary><div><p>Pass B analyses were registered in advance '
        '(<code>docs/V7_PREREGISTRATION_PASS_B.md</code>) and evaluated once. Full evidence: <code>docs/evidence/</code> in the repository.</p></div></details></section>')
    return page("Research & Data", "research", body, "Methodology, data sources, limitations and evidence.")


def build(out_dir: Path, inp: dict) -> list:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix = outlook_matrix(inp)
    pages = {"index.html": home(inp, matrix), "market-risk.html": market_page(inp), "forecast.html": forecast(inp, matrix),
             "sectors.html": sectors_page(inp), "track-record.html": track_page(inp, matrix),
             "research.html": research_page(inp)}
    for x in inp["sectors"]["sectors"]:
        pages[f"sector-{x['slug']}.html"] = sector_detail(x, inp)
    for name, content in pages.items():
        if not content.startswith("<!doctype html>"):
            raise ValueError("Invalid page: " + name)
        (out_dir / name).write_text(content)
    with (out_dir / "forecast_archive.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "horizon_months", "origin", "probability", "outcome"])
        w.writerows((r["target"], r["h"], r["origin"], r["probability"], r["outcome"]) for r in inp["archive"])
    return sorted(pages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", default="docs/evidence/v7_forecast_evaluation_2026-11-17.json")
    ap.add_argument("--research", default="docs/evidence/v7_passb_forecast_research_2026-11-18.json")
    ap.add_argument("--sectors", default="docs/evidence/v7_sectors_2026-11-18.json")
    ap.add_argument("--archive", default="data/v7/forecast_archive.csv")
    ap.add_argument("--fred-dir", default="data/v7")
    ap.add_argument("--crash", default=CRASH_EVIDENCE)
    ap.add_argument("--output", default="audit-output/v7-site")
    a = ap.parse_args()
    print(build(Path(a.output), load_inputs(a.forecast, a.research, a.sectors, a.archive, a.fred_dir, a.crash)))


if __name__ == "__main__":
    main()

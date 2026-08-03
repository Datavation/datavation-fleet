"""Finance-Dashboard.html — self-contained, mobile, read-only.

The review surface Quinn's routines refresh (commission §10.4): lives privately
on OneDrive, never published. Six views: (1) consolidated position with the
net-worth roll-up (liquid / illiquid assets / liabilities / custodial),
(2) cash flow + headline burn, (3) spend by category, (4) recurring
commitments / leak list, (5) business vs personal, (6) open questions. Data is
embedded inline as JSON — no server, no external fetch, no CDN — so it renders
on the phone straight off OneDrive sync. Internal transfers are already netted
out of the totals by analytics.py.
"""

from __future__ import annotations

import json
import os


_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Finance Dashboard</title>
<style>
  :root { --bg:#0f1720; --card:#182430; --ink:#e8eef4; --muted:#93a4b3;
          --pos:#3fb984; --neg:#e0685f; --accent:#5aa9e6; --line:#26333f; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
  header { padding:18px 16px 6px; }
  h1 { font-size:19px; margin:0 0 2px; }
  .sub { color:var(--muted); font-size:12px; }
  main { padding:8px 12px 40px; max-width:820px; margin:0 auto; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px;
          padding:14px 14px 10px; margin:10px 0; }
  .card h2 { font-size:13px; text-transform:uppercase; letter-spacing:.05em;
             color:var(--muted); margin:0 0 10px; }
  .big { font-size:26px; font-weight:700; }
  .row { display:flex; justify-content:space-between; align-items:center;
         padding:6px 0; border-bottom:1px solid var(--line); gap:10px; }
  .row:last-child { border-bottom:0; }
  .row .l { color:var(--ink); }
  .row .m { color:var(--muted); font-size:12px; }
  .num { font-variant-numeric:tabular-nums; white-space:nowrap; }
  .pos { color:var(--pos); } .neg { color:var(--neg); }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
  .bar { height:8px; background:var(--line); border-radius:5px; overflow:hidden; margin-top:4px; }
  .bar > span { display:block; height:100%; background:var(--accent); }
  .pill { display:inline-block; font-size:11px; color:var(--muted);
          border:1px solid var(--line); border-radius:20px; padding:1px 8px; }
  .warn { color:var(--neg); }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  td, th { text-align:left; padding:5px 4px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { color:var(--muted); font-weight:600; }
  td.r, th.r { text-align:right; }
  .muted { color:var(--muted); }
  footer { color:var(--muted); font-size:11px; text-align:center; padding:16px; }
</style>
</head>
<body>
<header>
  <h1>Quinn — Finance Dashboard</h1>
  <div class="sub" id="sub"></div>
</header>
<main id="app"></main>
<footer>Refreshed locally by Quinn's routines (read-only view — Quinn never moves money). Internal transfers netted out. Custodial holdings excluded from net worth. Private: lives on OneDrive, never published.</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const app = document.getElementById('app');
const gbp = v => (v<0?'-':'') + '£' + Math.abs(+v).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const cls = v => (+v<0?'neg':'pos');
function card(title, inner){ const d=document.createElement('div'); d.className='card';
  d.innerHTML='<h2>'+title+'</h2>'+inner; app.appendChild(d); }
function esc(s){ return (s==null?'':String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

document.getElementById('sub').textContent =
  (D.generated_span.from||'?') + ' → ' + (D.generated_span.to||'?') + '  ·  ' + D.txn_count + ' transactions';

// 1. Consolidated position — net worth roll-up
(function(){ const c=D.consolidated; let h='';
  const nw = (c.net_worth!=null ? c.net_worth : c.net_position);
  h += '<div class="grid">';
  h += '<div><div class="m">Net worth</div><div class="big '+cls(nw)+'">'+gbp(nw)+'</div></div>';
  h += '<div><div class="m">Liquid / cash</div><div class="big pos">'+gbp(c.liquid_total)+'</div></div>';
  h += '</div>';
  if(c.asset_total!=null && +c.asset_total!==0)
    h += '<div class="row"><span class="l">Assets <span class="pill">illiquid</span></span><span class="num pos">'+gbp(c.asset_total)+'</span></div>';
  h += '<div class="row"><span class="l">Liabilities</span><span class="num neg">'+gbp(c.liability_total)+'</span></div>';
  h += '<div class="row"><span class="l">Net position <span class="m">liquid + liabilities</span></span><span class="num '+cls(c.net_position)+'">'+gbp(c.net_position)+'</span></div>';
  if(+c.custodial_total!==0)
    h += '<div class="row"><span class="l">Held in safekeeping <span class="pill">custodial</span></span><span class="num muted">'+gbp(c.custodial_total)+'</span></div>';
  h += '<div style="margin-top:8px">';
  c.accounts.forEach(a=>{ h += '<div class="row"><span class="l">'+esc(a.name)+' <span class="m">'+esc(a.world)+' · '+esc(a.type)+'</span></span><span class="num '+cls(a.balance)+'">'+gbp(a.balance)+'</span></div>'; });
  h += '</div>';
  card('Consolidated position', h);
})();

// 2. Cash flow + burn
(function(){ const cf=D.cashflow; let h='';
  h += '<div class="grid">';
  h += '<div><div class="m">Weekly burn</div><div class="big neg">'+gbp(cf.weekly_burn)+'</div></div>';
  h += '<div><div class="m">Daily burn</div><div class="big neg">'+gbp(cf.daily_burn)+'</div></div>';
  h += '</div>';
  h += '<div class="row"><span class="l">Total in</span><span class="num pos">'+gbp(cf.total_in)+'</span></div>';
  h += '<div class="row"><span class="l">Total out</span><span class="num neg">'+gbp(cf.total_out)+'</span></div>';
  h += '<div class="row"><span class="l">Net</span><span class="num '+cls(cf.net)+'">'+gbp(cf.net)+'</span></div>';
  if(cf.monthly.length){ h+='<table><tr><th>Month</th><th class="r">In</th><th class="r">Out</th><th class="r">Net</th></tr>';
    cf.monthly.forEach(m=>{ h+='<tr><td>'+m.month+'</td><td class="r num pos">'+gbp(m.in)+'</td><td class="r num neg">'+gbp(m.out)+'</td><td class="r num '+cls(m.net)+'">'+gbp(m.net)+'</td></tr>'; });
    h+='</table>'; }
  card('Cash flow', h);
})();

// 3. Spend by category
(function(){ const rows=D.spend_by_category; if(!rows.length){card('Spend by category','<div class="muted">No spend.</div>');return;}
  const max=Math.max.apply(null,rows.map(r=>+r.amount))||1; let h='';
  rows.forEach(r=>{ const w=Math.round(+r.amount/max*100);
    h+='<div class="row" style="display:block;border:0;padding:4px 0"><div style="display:flex;justify-content:space-between"><span class="l">'+esc(r.category)+'</span><span class="num">'+gbp(r.amount)+'</span></div><div class="bar"><span style="width:'+w+'%"></span></div></div>'; });
  if(+D.uncategorised_total>0) h+='<div class="m warn" style="margin-top:6px">Uncategorised: '+gbp(D.uncategorised_total)+' — add rules to categories.csv.</div>';
  card('Spend by category', h);
})();

// 4. Recurring / leak list
(function(){ const rows=D.recurring; if(!rows.length){card('Recurring commitments','<div class="muted">No recurring rules matched.</div>');return;}
  let h='<table><tr><th>Commitment</th><th>Cadence</th><th class="r">Hits</th><th class="r">Total</th></tr>';
  rows.forEach(r=>{ h+='<tr><td>'+esc(r.label)+'</td><td class="muted">'+esc(r.cadence)+'</td><td class="r num">'+r.hits+'</td><td class="r num neg">'+gbp(r.total)+'</td></tr>'; });
  h+='</table>'; card('Recurring commitments / leak list', h);
})();

// 5. Business vs personal
(function(){ const bp=D.business_personal; let h='<table><tr><th>Scope</th><th class="r">In</th><th class="r">Out</th></tr>';
  bp.by_scope.forEach(r=>{ h+='<tr><td>'+esc(r.scope)+'</td><td class="r num pos">'+gbp(r.in)+'</td><td class="r num neg">'+gbp(r.out)+'</td></tr>'; });
  h+='</table>';
  if(bp.by_world.length){ h+='<div class="m" style="margin-top:8px">By world (spend)</div>';
    bp.by_world.forEach(r=>{ h+='<div class="row"><span class="l">'+esc(r.world)+'</span><span class="num neg">'+gbp(r.out)+'</span></div>'; }); }
  card('Business vs personal', h);
})();

// 6. Open questions
(function(){ const rows=D.open_questions; if(!rows.length){card('Open questions','<div class="muted">Nothing flagged. ✓</div>');return;}
  let h='<table><tr><th>Type</th><th>Detail</th><th>Answer</th></tr>';
  rows.forEach(q=>{ h+='<tr><td class="muted">'+esc(q.type)+'</td><td>'+esc(q.detail)+'</td><td>'+esc(q.answer)+'</td></tr>'; });
  h+='</table>'; card('Open questions ('+rows.length+')', h);
})();
</script>
</body>
</html>
"""


def write_dashboard(views, workdir: str) -> str:
    data = json.dumps(views, ensure_ascii=False)
    # guard against a stray </script> in data breaking the inline block
    data = data.replace("</", "<\\/")
    html = _TEMPLATE.replace("__DATA__", data)
    path = os.path.join(workdir, "Finance-Dashboard.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path

"""Finance-Insights.html — Quinn's interactive analysis view (client-local).

A richer companion to the engine's Finance-Dashboard.html, driven entirely by
the engine's own transactions.csv + rules/accounts.csv. It adds what a static
roll-up can't give: a month-by-month in/out trend by entity, collapsible
sections, a mortgage paydown panel, a business/entity filter, and a
regular-outgoings view that labels direct debits / standing orders and flags
possible duplicated commitments.

DESIGN BOUNDARIES (deliberate):
  * Reads ONLY the engine's output + the local rules. It never touches the
    shared engine code — this is a prototype view. Proven features get PROPOSED
    back into engine/dashboard.py through Archy's gate, not edited in ad hoc.
  * Self-contained HTML: data embedded as JSON, no CDN, no network, no external
    chart lib (SVG hand-rendered). It renders off local OneDrive like the engine
    dashboard and NEVER leaves the workdir.
  * Never invents a figure. Balances fed from a transaction feed with no seeded
    opening balance are labelled 'net-flow' so they are not mistaken for a real
    balance.

Usage:  python insights.py "<WORKDIR>"
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal
from statistics import mean, pstdev

# Make the engine importable for the rules loader (config only — no engine mutation).
_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE_ROOT = os.path.normpath(os.path.join(_HERE, "..", "consolidate"))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)

from engine.config import load_rules  # noqa: E402

ZERO = Decimal("0.00")
DD_MARKER = re.compile(r"\bDD\b|DIRECT DEBIT|\bDDR\b|STANDING ORDER|\bSTO\b", re.I)

# keyword -> commitment bucket, for the duplicate/overlap flag
_BUCKETS = [
    ("mortgage", ("mtge", "mortgage")),
    ("council tax", ("ctax", "council")),
    ("energy", ("octopus", "british gas", "eon", "e.on", "edf", "ovo", "energy", "electric", "utilita")),
    ("water", ("anglian water", "thames water", "water")),
    ("broadband / TV", ("virgin media", "sky", "bt ", "talktalk", "now tv", "netflix", "disney", "youtube")),
    ("mobile", ("ee ", "vodafone", "o2", "three", "tesco mobile", "giffgaff")),
    ("gym", ("energie", "puregym", "gym", "fitness")),
    ("insurance", ("admiral", "aviva", "insurance", "insur", "hastings", "churchill", "direct line")),
    ("subscriptions", ("apple", "spotify", "amazon prime", "prime", "microsoft", "google", "adobe")),
    ("pension / life", ("pension", "aviva life", "life eu")),
]


def _bucket(payee: str) -> str:
    p = payee.lower()
    for name, keys in _BUCKETS:
        if any(k in p for k in keys):
            return name
    return ""


def _norm_payee(s: str) -> str:
    s = (s or "").upper()
    s = re.sub(r"\b\d[\d/.\-]{2,}\b", " ", s)         # refs, dates, long digit runs
    s = re.sub(r"[^A-Z& ]", " ", s)
    s = re.sub(r"\b(LTD|LIMITED|UK|LONDON|GB|PLC|COM|WWW|FT|BGC|BP|MOBILE|CHANNEL|PYMTS|PYMT|PAYMENT)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return " ".join(s.split()[:3])


def _rate_and_payment(note: str):
    """Pull APR, monthly payment and fixed-until date out of the accounts.csv note."""
    rate = re.search(r"(\d+(?:\.\d+)?)\s*%", note or "")
    pay = re.search(r"monthly\s+£?\s*(\d+(?:\.\d+)?)", note or "", re.I)
    until = re.search(r"(?:fixed|fix)\s+(?:to|until)\s+([0-9A-Za-z\-]+)", note or "", re.I)
    return (
        Decimal(rate.group(1)) if rate else None,
        Decimal(pay.group(1)) if pay else None,
        until.group(1) if until else None,
    )


def build(workdir: str) -> dict:
    rules = load_rules(os.path.join(workdir, "rules"))
    rows = list(csv.DictReader(open(os.path.join(workdir, "transactions.csv"),
                                    encoding="utf-8-sig", newline="")))

    worlds = sorted({r["world"] for r in rows if r["world"]})
    months = sorted({r["date"][:7] for r in rows})

    # ---- monthly in/out by world (transfers excluded from flow) --------------
    by_wm = defaultdict(lambda: {"in": ZERO, "out": ZERO})
    for r in rows:
        if r["is_internal_transfer"] == "Y":
            continue
        a = Decimal(r["amount"])
        cell = by_wm[(r["world"], r["date"][:7])]
        if a >= 0:
            cell["in"] += a
        else:
            cell["out"] += -a
    monthly = [
        {"world": w, "ym": m, "in": f"{by_wm[(w, m)]['in']:.2f}", "out": f"{by_wm[(w, m)]['out']:.2f}"}
        for w in worlds for m in months
        if (by_wm[(w, m)]["in"] or by_wm[(w, m)]["out"])
    ]

    # ---- account balances (with honest 'basis' labels) -----------------------
    flow = defaultdict(lambda: ZERO)
    ntx = defaultdict(int)
    for r in rows:
        flow[r["account_id"]] += Decimal(r["amount"])
        ntx[r["account_id"]] += 1
    accounts = []
    for aid, acc in rules.accounts.items():
        opening = Decimal(acc.opening_balance) if acc.opening_balance else ZERO
        bal = opening + flow.get(aid, ZERO)
        if acc.is_liability:
            cls = "liability"
        elif acc.is_asset:
            cls = "asset"
        else:
            cls = "liquid"
        if ntx.get(aid, 0) == 0:
            basis = "manual"
        elif aid == "rhs_monzo":
            basis = "verified"          # computed == Monzo's own closing balance
        elif acc.type == "credit_card":
            basis = "unreliable"        # transaction-sum excludes interest/fees; sign can flip
        else:
            basis = "net-flow"          # no opening seeded -> flow since first txn, not a real balance
        accounts.append({
            "id": aid, "name": acc.name, "world": acc.world, "type": acc.type,
            "class": cls, "balance": f"{bal:.2f}", "basis": basis,
        })

    # ---- mortgage paydown panel ----------------------------------------------
    mort_actual = defaultdict(lambda: ZERO)   # ym -> observed mortgage DD total
    for r in rows:
        if "MTGE" in (r["raw_description"] or "").upper() or "MORTGAGE" in (r["description"] or "").upper():
            if Decimal(r["amount"]) < 0:
                mort_actual[r["date"][:7]] += -Decimal(r["amount"])
    mortgages = []
    for aid, acc in rules.accounts.items():
        if acc.type != "mortgage":
            continue
        bal = abs(Decimal(acc.opening_balance)) if acc.opening_balance else ZERO
        rate, pay, until = _rate_and_payment(acc.note)
        sched = []
        if rate and pay:
            b = bal
            mr = rate / Decimal(1200)     # monthly rate fraction
            for _ in range(12):
                interest = (b * mr).quantize(Decimal("0.01"))
                principal = (pay - interest).quantize(Decimal("0.01"))
                b = (b - principal).quantize(Decimal("0.01"))
                sched.append({"payment": f"{pay:.2f}", "interest": f"{interest:.2f}",
                              "principal": f"{principal:.2f}", "closing": f"{b:.2f}"})
        mortgages.append({
            "name": acc.name, "balance": f"{bal:.2f}",
            "rate": (f"{rate:.2f}" if rate else None),
            "payment": (f"{pay:.2f}" if pay else None),
            "fixed_until": until, "schedule": sched,
        })
    mort_observed = [{"ym": m, "paid": f"{mort_actual[m]:.2f}"} for m in sorted(mort_actual)]

    # ---- recurring / regular outgoings ---------------------------------------
    grp = defaultdict(lambda: {"months": set(), "amts": [], "worlds": defaultdict(lambda: ZERO),
                               "cats": defaultdict(int), "dd": 0, "ex": ""})
    for r in rows:
        if r["is_internal_transfer"] == "Y" or Decimal(r["amount"]) >= 0:
            continue
        raw = r["raw_description"] or r["description"]
        key = _norm_payee(raw)
        if not key:
            continue
        g = grp[key]
        g["months"].add(r["date"][:7])
        amt = -Decimal(r["amount"])
        g["amts"].append(float(amt))
        g["worlds"][r["world"]] += amt
        g["cats"][r["category"]] += 1
        if DD_MARKER.search(raw):
            g["dd"] += 1
        if not g["ex"]:
            g["ex"] = raw[:44]

    fixed, variable = [], []
    for payee, g in grp.items():
        nmonths = len(g["months"])
        if nmonths < 3:
            continue
        count = len(g["amts"])
        total = sum(g["amts"])
        monthly_avg = total / nmonths
        freq = count / nmonths
        m = mean(g["amts"])
        cov = (pstdev(g["amts"]) / m) if (len(g["amts"]) > 1 and m) else 0.0
        is_dd = g["dd"] > 0
        top_world = max(g["worlds"].items(), key=lambda kv: kv[1])[0]
        top_cat = max(g["cats"].items(), key=lambda kv: kv[1])[0]
        item = {
            "payee": payee, "example": g["ex"], "worlds": sorted(g["worlds"]),
            "world": top_world, "category": top_cat, "bucket": _bucket(payee + " " + g["ex"]),
            "months": nmonths, "count": count,
            "monthly_avg": round(monthly_avg, 2), "annualised": round(monthly_avg * 12, 2),
            "is_dd": is_dd,
            "repay": bool(re.search(r"B ?CARD|BARCLAYCARD|CREDIT CARD", payee, re.I)),
        }
        # a fixed commitment: a DD/SO, or ~monthly with steady amount
        if is_dd or (freq <= 1.6 and cov < 0.30):
            fixed.append(item)
        else:
            variable.append(item)
    fixed.sort(key=lambda x: x["annualised"], reverse=True)
    variable.sort(key=lambda x: x["annualised"], reverse=True)

    # ---- possible duplicate / overlapping commitments ------------------------
    bucket_map = defaultdict(list)
    for it in fixed:
        if it["bucket"]:
            bucket_map[it["bucket"]].append(it)
    duplicates = []
    for b, items in bucket_map.items():
        distinct = {i["payee"] for i in items}
        if len(distinct) >= 2:
            duplicates.append({
                "bucket": b,
                "payees": [{"payee": i["payee"], "annualised": i["annualised"]} for i in items],
                "annual_total": round(sum(i["annualised"] for i in items), 2),
            })
    duplicates.sort(key=lambda d: d["annual_total"], reverse=True)

    # ---- cash-flow summary + uncategorised -----------------------------------
    cf_in = defaultdict(lambda: ZERO)
    cf_out = defaultdict(lambda: ZERO)
    uncat = ZERO
    for r in rows:
        if r["is_internal_transfer"] == "Y":
            continue
        a = Decimal(r["amount"])
        ym = r["date"][:7]
        if a >= 0:
            cf_in[ym] += a
        else:
            cf_out[ym] += -a
            if r["category"] == "uncategorised":
                uncat += -a
    cf_monthly = [{"ym": m, "in": f"{cf_in[m]:.2f}", "out": f"{cf_out[m]:.2f}",
                   "net": f"{cf_in[m] - cf_out[m]:.2f}"} for m in months]
    total_in = sum(cf_in.values(), ZERO)
    total_out = sum(cf_out.values(), ZERO)

    return {
        "span": {"from": months[0] if months else None, "to": months[-1] if months else None},
        "txn_count": len(rows),
        "worlds": worlds,
        "months": months,
        "monthly": monthly,
        "accounts": accounts,
        "mortgages": mortgages,
        "mortgage_observed": mort_observed,
        "recurring_fixed": fixed,
        "recurring_variable": variable[:40],
        "duplicates": duplicates,
        "cashflow": {"monthly": cf_monthly, "total_in": f"{total_in:.2f}",
                     "total_out": f"{total_out:.2f}", "net": f"{total_in - total_out:.2f}"},
        "uncategorised": f"{uncat:.2f}",
    }


# --------------------------------------------------------------------------- #
#  Presentation
# --------------------------------------------------------------------------- #

_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quinn — Finance Insights</title>
<style>
  :root { --bg:#0f1720; --card:#182430; --ink:#e8eef4; --muted:#93a4b3;
          --pos:#3fb984; --neg:#e0685f; --accent:#5aa9e6; --line:#26333f;
          --w-Personal:#5aa9e6; --w-Joint:#b98bd6; --w-RexHomeServices:#3fb984; --w-Datavation:#e0a355; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
  header { padding:18px 16px 6px; }
  h1 { font-size:19px; margin:0 0 2px; }
  .sub { color:var(--muted); font-size:12px; }
  main { padding:8px 12px 40px; max-width:920px; margin:0 auto; }
  details.card { background:var(--card); border:1px solid var(--line); border-radius:12px;
          padding:0; margin:10px 0; overflow:hidden; }
  details.card > summary { list-style:none; cursor:pointer; padding:13px 14px;
          font-size:13px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted);
          display:flex; justify-content:space-between; align-items:center; }
  details.card > summary::-webkit-details-marker { display:none; }
  details.card > summary::after { content:"▸"; color:var(--muted); transition:transform .15s; }
  details.card[open] > summary::after { transform:rotate(90deg); }
  details.card > summary:hover { color:var(--ink); }
  .body { padding:0 14px 12px; }
  .big { font-size:24px; font-weight:700; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
  .row { display:flex; justify-content:space-between; align-items:center;
         padding:6px 0; border-bottom:1px solid var(--line); gap:10px; }
  .row:last-child { border-bottom:0; }
  .m, .muted { color:var(--muted); font-size:12px; }
  .num { font-variant-numeric:tabular-nums; white-space:nowrap; }
  .pos { color:var(--pos); } .neg { color:var(--neg); }
  .pill { display:inline-block; font-size:10px; color:var(--muted);
          border:1px solid var(--line); border-radius:20px; padding:1px 7px; margin-left:5px; }
  .pill.dd { color:var(--accent); border-color:var(--accent); }
  .pill.warn { color:var(--neg); border-color:var(--neg); }
  .pill.ok { color:var(--pos); border-color:var(--pos); }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  td, th { text-align:left; padding:5px 4px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { color:var(--muted); font-weight:600; }
  td.r, th.r { text-align:right; }
  .filters { display:flex; flex-wrap:wrap; gap:6px; padding:6px 2px 2px; }
  .filters button { background:var(--card); color:var(--muted); border:1px solid var(--line);
          border-radius:20px; padding:4px 11px; font-size:12px; cursor:pointer; }
  .filters button.on { color:var(--ink); border-color:var(--accent); background:#1d2f3f; }
  .legend { display:flex; flex-wrap:wrap; gap:12px; font-size:11px; color:var(--muted); margin:2px 0 8px; }
  .legend span::before { content:"■ "; }
  .chartwrap { overflow-x:auto; }
  .callout { background:#20161a; border:1px solid var(--neg); border-radius:9px; padding:9px 11px; margin:8px 0; font-size:13px; }
  .callout b { color:var(--neg); }
  footer { color:var(--muted); font-size:11px; text-align:center; padding:16px; }
</style>
</head>
<body>
<header>
  <h1>Quinn — Finance Insights</h1>
  <div class="sub" id="sub"></div>
  <div class="filters" id="filters"></div>
</header>
<main id="app"></main>
<footer>Quinn's analysis view — read-only, built from the local ledger. Private: lives on OneDrive, never published. Internal transfers netted from flows.</footer>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const gbp = v => (v<0?'-':'') + '£' + Math.abs(+v).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const gbp0 = v => (v<0?'-':'') + '£' + Math.abs(+v).toLocaleString('en-GB',{maximumFractionDigits:0});
const esc = s => (s==null?'':String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const wcol = w => getComputedStyle(document.documentElement).getPropertyValue('--w-'+w).trim() || '#7f8c99';
const shortW = w => ({RexHomeServices:'Rex HS', Datavation:'Datavation', Personal:'Personal', Joint:'Joint'}[w]||w);

let active = new Set(D.worlds);   // entity filter state

document.getElementById('sub').textContent =
  (D.span.from||'?') + ' → ' + (D.span.to||'?') + '  ·  ' + D.txn_count + ' transactions';

// ---- entity filter bar ----
(function(){ const f=document.getElementById('filters');
  const mk=(label,fn,test)=>{ const b=document.createElement('button'); b.textContent=label;
    b.onclick=()=>{fn(); render(); paint();}; b.dataset.test=test; f.appendChild(b); return b; };
  mk('All',()=>{active=new Set(D.worlds);},'all');
  mk('Business only',()=>{active=new Set(D.worlds.filter(w=>w==='RexHomeServices'||w==='Datavation'));},'biz');
  D.worlds.forEach(w=> mk(shortW(w),()=>{ if(active.has(w)) active.delete(w); else active.add(w);
      if(active.size===0) active=new Set(D.worlds); },'w:'+w));
  paint();
  function _p(){}
})();
function paint(){ document.querySelectorAll('#filters button').forEach(b=>{
  const t=b.dataset.test; let on=false;
  if(t==='all') on = active.size===D.worlds.length;
  else if(t==='biz') on = active.size===2 && active.has('RexHomeServices') && active.has('Datavation');
  else if(t.startsWith('w:')) on = active.has(t.slice(2));
  b.classList.toggle('on', on); }); }

// ---- section builders ----
function section(title, id, inner, open){
  return '<details class="card" '+(open?'open':'')+'><summary>'+title+'</summary><div class="body" id="'+id+'">'+inner+'</div></details>';
}

function trendChart(){
  const ms=D.months; const W=Math.max(520, ms.length*46), H=210, pad=28, base=H-18, top=12;
  // aggregate in/out over active worlds
  const agg=ms.map(m=>{ let mo={}, io=0, oo=0;
    D.worlds.forEach(w=>{ mo[w]={in:0,out:0}; });
    D.monthly.forEach(r=>{ if(r.ym===m && active.has(r.world)){ mo[r.world].in+=+r.in; mo[r.world].out+=+r.out; io+=+r.in; oo+=+r.out; } });
    return {m, mo, io, oo}; });
  const max=Math.max(1, ...agg.map(a=>Math.max(a.io,a.oo)));
  const bw=14, gap=6, slot=46;
  let svg='<svg width="'+W+'" height="'+H+'" role="img">';
  // gridlines
  for(let g=0; g<=2; g++){ const y=top+(base-top)*g/2; const val=max*(1-g/2);
    svg+='<line x1="'+pad+'" y1="'+y+'" x2="'+W+'" y2="'+y+'" stroke="#26333f"/>';
    svg+='<text x="2" y="'+(y+3)+'" fill="#93a4b3" font-size="9">'+gbp0(val)+'</text>'; }
  agg.forEach((a,i)=>{ const x0=pad+i*slot+6;
    // stacked IN
    let y=base; ['Personal','Joint','RexHomeServices','Datavation'].forEach(w=>{ if(!active.has(w))return;
      const h=(a.mo[w]?a.mo[w].in:0)/max*(base-top); if(h<=0)return; y-=h;
      svg+='<rect x="'+x0+'" y="'+y+'" width="'+bw+'" height="'+h+'" fill="'+wcol(w)+'"><title>'+w+' in '+a.m+': '+gbp(a.mo[w].in)+'</title></rect>'; });
    // stacked OUT
    let y2=base; const x1=x0+bw+gap; ['Personal','Joint','RexHomeServices','Datavation'].forEach(w=>{ if(!active.has(w))return;
      const h=(a.mo[w]?a.mo[w].out:0)/max*(base-top); if(h<=0)return; y2-=h;
      svg+='<rect x="'+x1+'" y="'+y2+'" width="'+bw+'" height="'+h+'" fill="'+wcol(w)+'" opacity="0.55"><title>'+w+' out '+a.m+': '+gbp(a.mo[w].out)+'</title></rect>'; });
    svg+='<text x="'+(x0+bw)+'" y="'+(H-4)+'" fill="#93a4b3" font-size="8.5" text-anchor="middle">'+a.m.slice(2)+'</text>';
  });
  svg+='</svg>';
  const legend='<div class="legend">'+D.worlds.filter(w=>active.has(w)).map(w=>'<span style="color:'+wcol(w)+'">'+shortW(w)+'</span>').join('')
    +'<span style="color:var(--muted)">solid = in · faded = out</span></div>';
  const totIn=agg.reduce((s,a)=>s+a.io,0), totOut=agg.reduce((s,a)=>s+a.oo,0);
  const head='<div class="grid"><div><div class="m">In (filtered)</div><div class="big pos">'+gbp(totIn)+'</div></div>'
    +'<div><div class="m">Out (filtered)</div><div class="big neg">'+gbp(totOut)+'</div></div></div>';
  return head+legend+'<div class="chartwrap">'+svg+'</div>';
}

function balancesView(){
  let h='<div class="muted" style="margin-bottom:6px">Basis is labelled honestly — only <b>manual</b> and <b>verified</b> lines are real balances; <b>net-flow</b> lines are flow since Jan-2025 (no opening seeded), and the card is <b>unreliable</b> until anchored to its statement.</div>';
  h+='<table><tr><th>Account</th><th>Basis</th><th class="r">Balance</th></tr>';
  D.accounts.forEach(a=>{ const p = a.basis==='verified'?'<span class="pill ok">verified</span>'
      : a.basis==='manual'?'<span class="pill ok">manual</span>'
      : a.basis==='unreliable'?'<span class="pill warn">unreliable</span>'
      : '<span class="pill warn">net-flow</span>';
    h+='<tr><td>'+esc(a.name)+' <span class="m">'+shortW(a.world)+' · '+a.type+'</span></td><td>'+p+'</td><td class="r num '+(+a.balance<0?'neg':'pos')+'">'+gbp(a.balance)+'</td></tr>'; });
  h+='</table>';
  return h;
}

function mortgageView(){
  let h='';
  D.mortgages.forEach(mo=>{
    h+='<div style="margin:10px 0 4px"><b>'+esc(mo.name)+'</b> '
      +(mo.rate?'<span class="pill">'+mo.rate+'% fixed'+(mo.fixed_until?' → '+mo.fixed_until:'')+'</span>':'')
      +(mo.payment?'<span class="pill">£'+mo.payment+'/mo</span>':'')+'</div>';
    h+='<div class="row"><span class="l">Current balance</span><span class="num neg">'+gbp(-Math.abs(+mo.balance))+'</span></div>';
    if(mo.schedule.length){
      h+='<div class="m" style="margin-top:6px">Projected paydown at current rate (next 12 months)</div>';
      h+='<table><tr><th>#</th><th class="r">Payment</th><th class="r">Interest</th><th class="r">Principal</th><th class="r">Closing</th></tr>';
      mo.schedule.forEach((s,i)=>{ h+='<tr><td class="muted">'+(i+1)+'</td><td class="r num">'+gbp(s.payment)+'</td><td class="r num neg">'+gbp(s.interest)+'</td><td class="r num pos">'+gbp(s.principal)+'</td><td class="r num">'+gbp(s.closing)+'</td></tr>'; });
      h+='</table>';
    }
  });
  if(D.mortgage_observed.length){
    h+='<div class="m" style="margin-top:10px">Actual mortgage direct debits observed in the ledger</div>';
    h+='<table><tr><th>Month</th><th class="r">Paid</th></tr>';
    D.mortgage_observed.slice(-8).forEach(o=>{ h+='<tr><td>'+o.ym+'</td><td class="r num neg">'+gbp(o.paid)+'</td></tr>'; });
    h+='</table>';
  }
  return h;
}

function recurringView(){
  const inActive = it => it.worlds.some(w=>active.has(w));
  const fx=D.recurring_fixed.filter(inActive), va=D.recurring_variable.filter(inActive);
  const monTot=fx.reduce((s,i)=>s+(i.repay?0:+i.monthly_avg),0), annTot=fx.reduce((s,i)=>s+(i.repay?0:+i.annualised),0);
  let h='<div class="grid"><div><div class="m">Fixed commitments / month</div><div class="big neg">'+gbp(monTot)+'</div></div>'
    +'<div><div class="m">Annualised</div><div class="big neg">'+gbp(annTot)+'</div></div></div>';
  if(D.duplicates.length){
    h+='<div class="callout"><b>Possible overlaps</b> — more than one commitment in the same bucket:<br>'
      + D.duplicates.map(d=>'· <b>'+esc(d.bucket)+'</b>: '+d.payees.map(p=>esc(p.payee)).join(', ')+' <span class="muted">('+gbp0(d.annual_total)+'/yr)</span>').join('<br>')
      + '</div>';
  }
  h+='<div class="m" style="margin-top:8px">Fixed monthly commitments — standing orders & direct debits</div>';
  h+='<table><tr><th>Payee</th><th></th><th class="r">~/mo</th><th class="r">/yr</th><th class="r">mths</th></tr>';
  fx.forEach(i=>{ h+='<tr><td>'+esc(i.payee)+' <span class="m">'+shortW(i.world)+'</span></td>'
    +'<td>'+(i.is_dd?'<span class="pill dd">DD</span>':'')+(i.repay?'<span class="pill warn">repayment</span>':'')+(i.bucket?'<span class="pill">'+esc(i.bucket)+'</span>':'')+'</td>'
    +'<td class="r num neg">'+gbp(i.monthly_avg)+'</td><td class="r num">'+gbp0(i.annualised)+'</td><td class="r num muted">'+i.months+'</td></tr>'; });
  h+='</table>';
  h+='<div class="m" style="margin-top:10px">Frequent variable spend (not fixed — groceries, fuel, shopping)</div>';
  h+='<table><tr><th>Payee</th><th class="r">~/mo</th><th class="r">/yr</th><th class="r">#</th></tr>';
  va.slice(0,15).forEach(i=>{ h+='<tr><td>'+esc(i.payee)+' <span class="m">'+shortW(i.world)+'</span></td>'
    +'<td class="r num neg">'+gbp(i.monthly_avg)+'</td><td class="r num">'+gbp0(i.annualised)+'</td><td class="r num muted">'+i.count+'</td></tr>'; });
  h+='</table>';
  return h;
}

function cashflowView(){
  let h='<div class="grid"><div><div class="m">Total in</div><div class="big pos">'+gbp(D.cashflow.total_in)+'</div></div>'
    +'<div><div class="m">Total out</div><div class="big neg">'+gbp(D.cashflow.total_out)+'</div></div></div>';
  h+='<table><tr><th>Month</th><th class="r">In</th><th class="r">Out</th><th class="r">Net</th></tr>';
  D.cashflow.monthly.forEach(m=>{ h+='<tr><td>'+m.ym+'</td><td class="r num pos">'+gbp(m.in)+'</td><td class="r num neg">'+gbp(m.out)+'</td><td class="r num '+(+m.net<0?'neg':'pos')+'">'+gbp(m.net)+'</td></tr>'; });
  h+='</table>';
  if(+D.uncategorised>0) h+='<div class="m" style="margin-top:6px" ><span class="pill warn">heads-up</span> '+gbp(D.uncategorised)+' of outgoings still uncategorised — category rules pending.</div>';
  return h;
}

function render(){
  const app=document.getElementById('app');
  app.innerHTML =
    section('Monthly in / out trend', 'sec-trend', trendChart(), true)
  + section('Regular outgoings — direct debits & standing orders', 'sec-rec', recurringView(), true)
  + section('Mortgages — balance & paydown', 'sec-mort', mortgageView(), false)
  + section('Account balances & net worth', 'sec-bal', balancesView(), false)
  + section('Cash flow by month', 'sec-cf', cashflowView(), false);
}
render();
</script>
</body>
</html>
"""


def write_html(data: dict, workdir: str) -> str:
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = _TEMPLATE.replace("__DATA__", js)
    path = os.path.join(workdir, "Finance-Insights.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python insights.py <WORKDIR>", file=sys.stderr)
        return 2
    workdir = argv[0]
    data = build(workdir)
    path = write_html(data, workdir)
    print("wrote", path)
    # reconciliation echo (no figures beyond top-level totals)
    print("months:", len(data["months"]), "| fixed commitments:", len(data["recurring_fixed"]),
          "| variable payees:", len(data["recurring_variable"]), "| overlap buckets:", len(data["duplicates"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

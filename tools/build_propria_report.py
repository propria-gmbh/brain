#!/usr/bin/env python3
"""Build Propria GmbH Q1/Q2 2026 accounting report as self-contained HTML."""

import csv
import json
import os
from collections import defaultdict

BASE = (
    "/Users/dister/Library/CloudStorage/"
    "GoogleDrive-ilja.disterheft@gmail.com/Shared drives/Propria/"
    "Propria GmbH/10. Accounting/60. Shopify/10. Orders"
)
REVOLUT_JSON = "/private/tmp/revolut_clean.json"
OUT = "/Users/dister/Projects/brain/07_OUTPUT/q1q2-2026-propria-report-v5.html"

STORES = {
    "mf": {
        "name": "Marc&François",
        "folder": "Marc&François",
        "currency": "CHF",
        "payouts_file": "payouts_export_1 (1).csv",
        "tx_file": "payment_transactions_export_1.csv",
        "orders_file": "orders_export_1 (1).csv",
    },
    "oa": {
        "name": "Oliver & Alder",
        "folder": "Oliver and Alder",
        "currency": "GBP",
        "payouts_file": "payouts_export_1.csv",
        "tx_file": "payment_transactions_export_1.csv",
        "orders_file": "orders_export_1 (1).csv",
        "has_pdfs": True,
    },
    "ct": {
        "name": "Charlie & Ted",
        "folder": "Charlie & Ted",
        "currency": "USD",
        "payouts_file": "payouts_export_1 (1).csv",
        "tx_file": "payment_transactions_export_1 (1).csv",
        "orders_file": "orders_export_1.csv",
    },
    "cg": {
        "name": "Casa Giannini",
        "folder": "Casa Giannini",
        "currency": "EUR",
        "payouts_file": "payouts_export_1.csv",
        "tx_file": "payment_transactions_export_1 (1).csv",
        "orders_file": "orders_export_1.csv",
    },
}

SUPPLIER_PARTIES = {"HST Electronics technology Co., Limited", "EAST BAITE LIMITED"}


def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def famt(v):
    try:
        return round(float(v or 0), 2)
    except (ValueError, TypeError):
        return 0.0


def load_revolut():
    with open(REVOLUT_JSON) as f:
        return json.load(f)


def load_store(sid, cfg):
    folder = os.path.join(BASE, cfg["folder"])

    payouts = []
    for r in read_csv(os.path.join(folder, cfg["payouts_file"])):
        d = r.get("Payout Date", "")
        if not ("2026-01" <= d <= "2026-06-30"):
            continue
        total = famt(r.get("Total"))
        if total == 0:
            continue
        pkey = f"{sid}_{d}_{abs(total):.2f}"
        q = "Q1" if d <= "2026-03-31" else "Q2"
        payouts.append({
            "key": pkey,
            "sid": sid,
            "date": d,
            "q": q,
            "total": total,
            "charges": famt(r.get("Charges")),
            "refunds": famt(r.get("Refunds")),
            "fees": -famt(r.get("Fees")),  # Shopify stores fees as positive; negate for display
            "bank_ref": r.get("Bank Reference", ""),
            "currency": r.get("Currency", "EUR"),
        })

    payout_by_date = {p["date"]: p for p in payouts}

    tx_by_payout_id = defaultdict(list)
    payout_id_to_date = {}
    for r in read_csv(os.path.join(folder, cfg["tx_file"])):
        d = r.get("Transaction Date", "")[:10]
        if d[:4] != "2026":
            continue
        pid = r.get("Payout ID", "")
        pdate = r.get("Payout Date", "")
        if pid:
            tx_by_payout_id[pid].append({
                "order": r.get("Order", ""),
                "type": r.get("Type", ""),
                "date": d,
                "payout_date": pdate,
                "amount_eur": famt(r.get("Amount")),
                "fee": famt(r.get("Fee")),
                "net": famt(r.get("Net")),
                "pres_amount": r.get("Presentment Amount", ""),
                "pres_currency": r.get("Presentment Currency", ""),
                "payout_id": pid,
            })
            if pdate and pid not in payout_id_to_date:
                payout_id_to_date[pid] = pdate

    for pid, txs in tx_by_payout_id.items():
        pdate = payout_id_to_date.get(pid, "")
        p = payout_by_date.get(pdate)
        if p:
            p.setdefault("payout_id", pid)
            p.setdefault("transactions", [])
            p["transactions"].extend(txs)

    orders_by_name = defaultdict(list)
    for r in read_csv(os.path.join(folder, cfg["orders_file"])):
        name = r.get("Name", "")
        if name:
            orders_by_name[name].append(r)

    orders = {}
    for name, rows in orders_by_name.items():
        first = rows[0]
        items = []
        for r in rows:
            item_name = r.get("Lineitem name", "").strip()
            if item_name:
                items.append({
                    "name": item_name,
                    "qty": r.get("Lineitem quantity", "1"),
                    "price": r.get("Lineitem price", ""),
                    "sku": r.get("Lineitem sku", ""),
                })
        orders[name] = {
            "order_num": name,
            "sid": sid,
            "date": (first.get("Paid at") or first.get("Created at", ""))[:10],
            "total": famt(first.get("Total")),
            "currency": first.get("Currency", cfg["currency"]),
            "customer": first.get("Billing Name") or first.get("Shipping Name", ""),
            "email": first.get("Email", ""),
            "financial_status": first.get("Financial Status", ""),
            "items": items,
        }

    pdf_by_payout_id = {}
    if cfg.get("has_pdfs"):
        for fn in os.listdir(folder):
            if fn.endswith(".pdf") and fn[:-4].isdigit():
                pdf_by_payout_id[fn[:-4]] = os.path.join(folder, fn)

    for p in payouts:
        pid = p.get("payout_id", "")
        if pid and pid in pdf_by_payout_id:
            p["pdf_path"] = pdf_by_payout_id[pid]

    return payouts, orders


def build_data(revolut, store_data):
    all_payouts = {}
    for sid, (payouts, orders) in store_data.items():
        for p in payouts:
            all_payouts[p["key"]] = p

    for sid, (payouts, orders) in store_data.items():
        for p in payouts:
            for tx in p.get("transactions", []):
                onum = tx.get("order", "")
                if onum in orders:
                    tx["order_data"] = orders[onum]

    payout_by_date_amt = defaultdict(list)
    for pkey, p in all_payouts.items():
        k = (p["date"], round(abs(p["total"]), 2))
        payout_by_date_amt[k].append(pkey)

    rev_to_pay = {}
    pay_to_rev = {}
    for r in revolut:
        is_topup = r["type"] == "TOPUP"
        is_shopify_transfer = r["type"] == "TRANSFER" and r.get("party") == "Shopify"
        if is_topup or is_shopify_transfer:
            k = (r["date"], round(abs(r["amount"]), 2))
            matched_pkeys = payout_by_date_amt.get(k, [])
            rev_to_pay[r["id"]] = matched_pkeys
            for pkey in matched_pkeys:
                pay_to_rev[pkey] = r["id"]

    invoices = []
    for r in revolut:
        if r["type"] == "TRANSFER" and r.get("party") in SUPPLIER_PARTIES:
            invoices.append({
                "rev_id": r["id"],
                "date": r["date"],
                "amount": r["amount"],
                "party": r["party"],
                "desc": r.get("desc", ""),
                "doc_url": r.get("doc_url", ""),
                "doc_label": r.get("doc_label", ""),
                "q": r.get("q", ""),
                "kfb_bills": r.get("kfb_bills", []),
                "kfb_bill_data": r.get("kfb_bill_data", []),
                "kfb_auto_links": r.get("kfb_auto_links", {}),
            })

    return {
        "rev": revolut,
        "payouts": all_payouts,
        "stores": {
            sid: {"name": cfg["name"], "currency": cfg["currency"]}
            for sid, cfg in STORES.items()
        },
        "invoices": invoices,
        "rev_to_pay": rev_to_pay,
        "pay_to_rev": pay_to_rev,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Propria GmbH Q1/Q2 2026 Buchhaltung</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;background:#f0f2f5;color:#1a1a1a}
.app{display:flex;flex-direction:column;height:100vh}
.header{background:#1e3a5f;color:white;padding:12px 20px;display:flex;align-items:center;gap:16px;flex-shrink:0}
.header h1{font-size:15px;font-weight:600;letter-spacing:0.02em}
.subtitle{font-size:11px;opacity:0.7}
.tabs{background:#fff;border-bottom:1px solid #dde1e7;display:flex;padding:0 20px;flex-shrink:0}
.tab{padding:10px 16px;cursor:pointer;font-size:12px;font-weight:500;color:#666;border-bottom:2px solid transparent;white-space:nowrap;transition:color 0.15s}
.tab:hover{color:#1e3a5f}
.tab.active{color:#1e3a5f;border-bottom-color:#1e3a5f}
.main{display:flex;flex:1;overflow:hidden}
.list-area{flex:1;overflow-y:auto;padding:0}
.panel{width:500px;flex-shrink:0;background:#fff;border-left:1px solid #dde1e7;overflow-y:auto;display:none;flex-direction:column}
.panel.open{display:flex}
.panel-header{padding:12px 16px;border-bottom:1px solid #eee;background:#fafbfc;display:flex;align-items:center;gap:8px;flex-shrink:0}
.back-btn{background:none;border:none;cursor:pointer;color:#1e3a5f;font-size:13px;padding:4px 8px;border-radius:4px;display:flex;align-items:center;gap:4px}
.back-btn:hover{background:#e8edf3}
.breadcrumb{font-size:11px;color:#888;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.doc-btn{background:#1e3a5f;color:white;border:none;cursor:pointer;font-size:13px;font-weight:600;padding:7px 14px;border-radius:4px;white-space:nowrap;flex-shrink:0}
.doc-btn:hover{background:#16305a}
.panel-body{padding:16px;flex:1}
table{width:100%;border-collapse:collapse;background:#fff}
th{background:#f5f7fa;font-size:11px;font-weight:600;color:#555;text-align:left;padding:8px 12px;border-bottom:2px solid #dde1e7;position:sticky;top:0;z-index:1}
td{padding:7px 12px;border-bottom:1px solid #f0f2f5;vertical-align:middle}
tr:hover td{background:#f8faff;cursor:pointer}
.amt-pos{color:#0a7c3c;font-weight:500;font-variant-numeric:tabular-nums}
.amt-neg{color:#c0392b;font-weight:500;font-variant-numeric:tabular-nums}
.amt-neu{color:#555;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:600;text-transform:uppercase}
.badge-topup{background:#d4edda;color:#0a7c3c}
.badge-transfer{background:#fde8e8;color:#c0392b}
.badge-fee{background:#f0f0f0;color:#777}
.badge-reward{background:#fff3cd;color:#856404}
.badge-card{background:#e8e8fd;color:#3a3a9e}
.badge-refund{background:#fde8e8;color:#c0392b}
.badge-charge{background:#d4edda;color:#0a7c3c}
.badge-mf{background:#e8f4fd;color:#1565c0}
.badge-oa{background:#fce4ec;color:#880e4f}
.badge-ct{background:#e8f5e9;color:#1b5e20}
.badge-cg{background:#fff3e0;color:#e65100}
.tag-q1{background:#e3f2fd;color:#1565c0;padding:1px 6px;border-radius:3px;font-size:10px}
.tag-q2{background:#f3e5f5;color:#6a1b9a;padding:1px 6px;border-radius:3px;font-size:10px}
.card-section{margin-bottom:14px}
.card-label{font-size:10px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px}
.card-value{font-size:13px;color:#1a1a1a}
.card-value.big{font-size:20px;font-weight:700}
.card-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
.link-list{list-style:none}
.link-list li{padding:7px 0;border-bottom:1px solid #f0f2f5;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.link-list li:hover{color:#1e3a5f}
.link-list li:last-child{border-bottom:none}
.chevron{color:#ccc;font-size:11px}
.section-title{font-size:11px;font-weight:700;color:#1e3a5f;text-transform:uppercase;letter-spacing:0.06em;margin:16px 0 8px;padding-top:14px;border-top:1px solid #eef}
.section-title:first-of-type{margin-top:0;padding-top:0;border-top:none}
.order-item{padding:5px 0;border-bottom:1px solid #f5f5f5;display:flex;justify-content:space-between;align-items:center}
.order-item:last-child{border-bottom:none}
.empty-state{text-align:center;color:#999;padding:30px;font-size:13px}
.filter-bar{padding:9px 16px;background:#fff;border-bottom:1px solid #eee;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.filter-btn{padding:3px 10px;border-radius:12px;border:1px solid #dde1e7;background:#fff;cursor:pointer;font-size:11px;color:#555;transition:all 0.15s}
.filter-btn.active{background:#1e3a5f;color:#fff;border-color:#1e3a5f}
.print-all-btn{margin-left:auto;padding:4px 12px;border-radius:4px;border:1px solid #1e3a5f;background:#fff;cursor:pointer;font-size:11px;color:#1e3a5f;font-weight:600}
.print-all-btn:hover{background:#1e3a5f;color:#fff}
.summary-bar{padding:8px 16px;background:#1e3a5f;color:white;font-size:11px;display:flex;gap:20px;flex-wrap:wrap}
.summary-item{display:flex;flex-direction:column;gap:2px}
.summary-item .s-label{opacity:0.6;font-size:10px}
.summary-item .s-val{font-weight:600}
.pdf-link{color:#1e3a5f;text-decoration:none;font-size:11px;display:inline-flex;align-items:center;gap:4px}
.pdf-link:hover{text-decoration:underline}
.unmatched{color:#999;font-style:italic}
.row-doc-btn{background:none;border:none;cursor:pointer;color:#1e3a5f;font-size:13px;padding:2px 4px;opacity:0.5;line-height:1}
.row-doc-btn:hover{opacity:1}
/* P&L tab */
.pl-section{background:#fff;margin:16px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.pl-section-title{background:#1e3a5f;color:white;padding:10px 16px;font-size:12px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase}
.pl-table{width:100%;border-collapse:collapse}
.pl-table th{background:#f5f7fa;font-size:11px;font-weight:600;color:#555;text-align:right;padding:8px 12px;border-bottom:1px solid #dde1e7}
.pl-table th:first-child{text-align:left}
.pl-table td{padding:8px 12px;border-bottom:1px solid #f0f2f5;text-align:right;font-variant-numeric:tabular-nums}
.pl-table td:first-child{text-align:left;font-weight:500}
.pl-table tr.total-row td{font-weight:700;background:#f9fafb;border-top:2px solid #dde1e7;border-bottom:2px solid #dde1e7}
.pl-table tr.margin-row td{font-weight:700;font-size:15px;background:#e8f4e8;color:#0a5c2a;border-top:2px solid #0a7c3c}
.pl-table tr.margin-neg td{background:#fde8e8;color:#c0392b;border-top:2px solid #c0392b}
.pl-q-col{color:#888;font-size:11px}
.tx-sale{background:#f6fff8;border-left:3px solid #0a7c3c;padding:8px 10px;margin:4px 0;border-radius:3px}
.tx-refund{background:#fff5f5;border-left:3px solid #c0392b;padding:8px 10px;margin:4px 0;border-radius:3px}
.tx-net-total{background:#f5f7fa;padding:8px 10px;margin-top:6px;border-radius:3px;font-weight:700;display:flex;justify-content:space-between}
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div>
      <div class="header h1">Propria GmbH &mdash; Buchhaltung</div>
      <div class="subtitle">Q1+Q2 2026 &mdash; Januar bis Juni</div>
    </div>
  </div>
  <div class="tabs" id="tabs">
    <div class="tab active" onclick="switchTab(0)">Revolut EUR</div>
    <div class="tab" onclick="switchTab(1)">Payouts</div>
    <div class="tab" onclick="switchTab(2)">Orders</div>
    <div class="tab" onclick="switchTab(3)">Transactions</div>
    <div class="tab" onclick="switchTab(4)">Lieferanten</div>
    <div class="tab" onclick="switchTab(5)">P&amp;L</div>
  </div>
  <div class="main">
    <div class="list-area" id="listArea">
      <div id="summaryBar" class="summary-bar"></div>
      <div id="filterBar" class="filter-bar"></div>
      <div id="tableContainer"></div>
    </div>
    <div class="panel" id="panel">
      <div class="panel-header">
        <button class="back-btn" onclick="panelBack()">&#8592; Zurück</button>
        <div class="breadcrumb" id="breadcrumb"></div>
        <button class="doc-btn" id="panelDocBtn" onclick="panelOpenDoc()" style="display:none">&#128196; Dokument anzeigen ↗</button>
      </div>
      <div class="panel-body" id="panelBody"></div>
    </div>
  </div>
</div>
<script>
const D = __DATA__;

let activeTab = 0;
let panelStack = [];
let filterType = '';
let filterStore = '';
let currentDocFn = null;

function switchTab(i) {
  activeTab = i;
  panelStack = [];
  closePanel();
  document.querySelectorAll('.tab').forEach((t,j) => t.classList.toggle('active', j===i));
  render();
}

function render() {
  renderSummary();
  renderFilters();
  renderTable();
}

function eur(v) { return (v >= 0 ? '+' : '') + v.toFixed(2) + ' EUR'; }
function eurN(v) { return v.toFixed(2) + ' EUR'; }
function amtCls(v) { return v > 0 ? 'amt-pos' : v < 0 ? 'amt-neg' : 'amt-neu'; }
function fmtDate(d) { return (d||'').slice(0,10); }

function badge(type, sid) {
  const map = {
    TOPUP:['topup','TOPUP'], TRANSFER:['transfer','TRANSFER'],
    CARD_PAYMENT:['card','CARD'], FEE:['fee','FEE'],
    REWARD:['reward','REWARD'], REFUND:['refund','REFUND'],
    charge:['charge','CHARGE'], refund:['refund','REFUND'], sale:['charge','SALE'],
  };
  const sm = {mf:['mf','Marc&F'], oa:['oa','Oliver&A'], ct:['ct','Charlie&T'], cg:['cg','Casa G']};
  if (sid && sm[sid]) return `<span class="badge badge-${sm[sid][0]}">${sm[sid][1]}</span>`;
  const m = map[type] || map[(type||'').toLowerCase()];
  if (m) return `<span class="badge badge-${m[0]}">${m[1]}</span>`;
  return `<span class="badge badge-fee">${type||''}</span>`;
}
function qTag(q) { return q ? `<span class="tag-${q.toLowerCase()}">${q}</span>` : ''; }

// ---- Document generation ----
const DOC_STYLE = `
  body{font-family:Arial,sans-serif;padding:40px;max-width:720px;margin:0 auto;color:#1a1a1a;font-size:13px}
  .no-print{margin-bottom:20px;display:flex;gap:10px}
  .btn{padding:8px 18px;background:#1e3a5f;color:white;border:none;border-radius:4px;cursor:pointer;font-size:13px}
  .doc-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;padding-bottom:14px;border-bottom:3px solid #1e3a5f}
  .co h1{font-size:17px;color:#1e3a5f;margin:0} .co p{font-size:11px;color:#888;margin:3px 0 0}
  .dt{text-align:right} .dt h2{font-size:48px;font-weight:900;color:#1e3a5f;margin:0;text-transform:uppercase;letter-spacing:0.04em;line-height:1}
  .dt .ref{font-size:13px;color:#555;margin-top:6px;font-weight:500}
  table{width:100%;border-collapse:collapse;margin:14px 0}
  th{font-size:11px;font-weight:600;color:#555;text-align:left;padding:6px 8px;border-bottom:2px solid #dde1e7;background:#f5f7fa}
  td{padding:7px 8px;border-bottom:1px solid #f0f2f5}
  tr.total-row td{font-weight:700;border-top:2px solid #ddd;border-bottom:2px solid #ddd;background:#f9fafb}
  .pos{color:#0a7c3c;font-weight:500} .neg{color:#c0392b;font-weight:500}
  .section{font-size:12px;font-weight:700;color:#1e3a5f;text-transform:uppercase;margin:20px 0 8px;letter-spacing:0.05em}
  .info-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
  .info-cell .lbl{font-size:10px;color:#888;text-transform:uppercase;font-weight:600;margin-bottom:2px}
  .info-cell .val{font-size:13px} .info-cell .val.big{font-size:18px;font-weight:700}
  .page-break{page-break-after:always;border-top:1px dashed #ccc;margin:40px 0}
  @media print{.no-print{display:none!important} body{padding:20px}}
`;

function docWrap(titleType, titleRef, date, content) {
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Propria - ${titleType}</title>
  <style>${DOC_STYLE}</style></head><body>
  <div class="no-print">
    <button class="btn" onclick="window.print()">&#128424; Drucken / Als PDF speichern</button>
    <button class="btn" style="background:#666" onclick="window.close()">Schliessen</button>
  </div>
  <div class="doc-head">
    <div class="co"><h1>Propria GmbH</h1><p>Q1/Q2 2026 Buchungsnachweis</p></div>
    <div class="dt"><h2>${titleType}</h2><div class="ref">${titleRef}</div><div class="ref">${date}</div></div>
  </div>
  ${content}
  </body></html>`;
}

function infoGrid(cells) {
  return `<div class="info-grid">${cells.map(([l,v,big])=>
    `<div class="info-cell"><div class="lbl">${l}</div><div class="val${big?' big':''}">${v}</div></div>`
  ).join('')}</div>`;
}

function buildOrderDocContent(orderNum) {
  const allTx = gatherOrderTx(orderNum);
  if (!allTx.length) return `<p>Keine Daten f&uuml;r ${orderNum}</p>`;
  const {tx: ftx, p: fp} = allTx[0];
  const od = ftx.order_data;
  const sid = fp.sid;
  const storeName = D.stores[sid]?.name || sid;

  let out = infoGrid([
    ['Shop', storeName, false],
    ['Order', orderNum, true],
    ['Datum', fmtDate(ftx.date), false],
    ['Kunde', od ? (od.customer||'—') : '—', false],
    ['E-Mail', od ? (od.email||'—') : '—', false],
    ['Status', od ? (od.financial_status||'—') : '—', false],
  ]);

  if (od && od.items && od.items.length) {
    out += `<div class="section">Artikel</div><table>
      <tr><th>Pos.</th><th>Artikel</th><th>SKU</th><th style="text-align:right">Menge</th><th style="text-align:right">Preis</th></tr>`;
    od.items.forEach((item, i) => {
      out += `<tr><td>${i+1}</td><td>${item.name}</td><td style="color:#888">${item.sku||''}</td>
        <td style="text-align:right">${item.qty}</td><td style="text-align:right">${item.price} ${od.currency}</td></tr>`;
    });
    out += `<tr class="total-row"><td colspan="4">Gesamt (Shopify)</td>
      <td style="text-align:right">${od.total.toFixed(2)} ${od.currency}</td></tr></table>`;
  }

  out += `<div class="section">Transaktionen</div>
    <table><tr><th>Datum</th><th>Typ</th><th>Betrag (Lokal)</th><th style="text-align:right">Betrag EUR</th>
      <th style="text-align:right">Shopify Fee</th><th style="text-align:right">Net EUR</th></tr>`;
  let totalNet = 0;
  for (const {tx} of allTx) {
    const cls = tx.type === 'refund' ? 'neg' : 'pos';
    totalNet += tx.net;
    out += `<tr><td>${fmtDate(tx.date)}</td><td>${tx.type||''}</td>
      <td>${tx.pres_amount||''} ${tx.pres_currency||''}</td>
      <td style="text-align:right" class="${cls}">${tx.amount_eur.toFixed(2)}</td>
      <td style="text-align:right;color:#888">${tx.fee.toFixed(2)}</td>
      <td style="text-align:right" class="${cls}">${tx.net.toFixed(2)}</td></tr>`;
  }
  out += `<tr class="total-row"><td colspan="5">Netto (nach Shopify-Geb&uuml;hren)</td>
    <td style="text-align:right" class="${totalNet>=0?'pos':'neg'}">${totalNet.toFixed(2)}&nbsp;EUR</td></tr></table>`;

  // Zahlungseingang: Payouts
  const seenPkDoc = new Set();
  const payoutRows = allTx.map(({pk: txPk, p}) => { if (seenPkDoc.has(txPk)) return ''; seenPkDoc.add(txPk);
    const revId = D.pay_to_rev[txPk];
    const rev = revId ? D.rev.find(x=>x.id===revId) : null;
    return `<tr><td>${fmtDate(p.date)}</td><td>${p.bank_ref||'—'}</td><td>${D.stores[p.sid]?.name||p.sid}</td>
      <td style="text-align:right" class="${p.total>=0?'pos':'neg'}">${p.total.toFixed(2)}&nbsp;EUR</td>
      <td>${rev ? '&#10003; Revolut '+fmtDate(rev.date)+' / '+rev.amount.toFixed(2)+' EUR' : '—'}</td></tr>`;
  }).join('');
  out += `<div class="section">Zahlungseingang (Payout)</div>
    <table><tr><th>Datum</th><th>Bank Reference</th><th>Shop</th><th style="text-align:right">Betrag EUR</th><th>Revolut</th></tr>
    ${payoutRows}</table>`;

  // Warenkosten aus verknüpften Lieferantenrechnungen (nur wenn vorhanden)
  const linksNow = loadLinks();
  const linkedInvs = D.invoices.filter(inv => linksNow[inv.rev_id] && (orderNum in linksNow[inv.rev_id]));
  if (linkedInvs.length > 0) {
    let totalCost = 0;
    out += `<div class="section">Warenkosten (Lieferantenrechnungen)</div>
      <table><tr><th>Lieferant</th><th>Rechnungsdatum</th><th style="text-align:right">Betrag EUR</th></tr>`;
    for (const inv of linkedInvs) {
      const amt = linksNow[inv.rev_id][orderNum] || 0;
      totalCost += amt;
      out += `<tr><td>${inv.party}</td><td>${fmtDate(inv.date)}</td>
        <td style="text-align:right" class="neg">-${amt.toFixed(2)}</td></tr>`;
    }
    out += `<tr class="total-row"><td colspan="2">Warenkosten gesamt</td>
      <td style="text-align:right" class="neg">-${totalCost.toFixed(2)}&nbsp;EUR</td></tr></table>`;
  }

  return out;
}

function openOrderDoc(orderNum) {
  const allTx = gatherOrderTx(orderNum);
  const date = allTx.length ? fmtDate(allTx[0].tx.date) : '';
  const sid = allTx.length ? allTx[0].p.sid : '';
  const storeName = D.stores[sid]?.name || sid;
  const win = window.open('', '_blank');
  win.document.write(docWrap('ORDER', `${storeName} / ${orderNum}`, date, buildOrderDocContent(orderNum)));
  win.document.close();
}

function buildPayDocContent(pk) {
  const p = D.payouts[pk];
  if (!p) return '';
  const storeName = D.stores[p.sid]?.name || p.sid;
  const revId = D.pay_to_rev[pk];
  const txs = p.transactions || [];

  let out = infoGrid([
    ['Shop', storeName, false],
    ['Datum', fmtDate(p.date), false],
    ['Quartal', p.q||'', false],
    ['Bank Reference', p.bank_ref||'—', false],
    ['Revolut Eingang', revId ? 'Verknüpft ✓' : '—', false],
    ['Total EUR', `<span class="${p.total>=0?'pos':'neg'}">${eur(p.total)}</span>`, true],
  ]);

  out += `<div class="section">Zusammenfassung</div>
    <table><tr><th>Position</th><th style="text-align:right">EUR</th></tr>
    <tr><td>Charges (Umsatz)</td><td style="text-align:right" class="pos">+${p.charges.toFixed(2)}</td></tr>
    <tr><td>Refunds (Rückerstattungen)</td><td style="text-align:right" class="neg">${p.refunds.toFixed(2)}</td></tr>
    <tr><td>Shopify Fees</td><td style="text-align:right" class="neg">${p.fees.toFixed(2)}</td></tr>
    <tr class="total-row"><td>Total Payout</td><td style="text-align:right" class="${p.total>=0?'pos':'neg'}">${eur(p.total)}</td></tr>
    </table>`;

  // Revolut Eingang
  const rev = revId ? D.rev.find(x=>x.id===revId) : null;
  out += `<div class="section">Revolut Eingang</div>`;
  if (rev) {
    out += infoGrid([
      ['Datum', fmtDate(rev.date), false],
      ['Betrag EUR', `<span class="${rev.amount>=0?'pos':'neg'}">${rev.amount.toFixed(2)} EUR</span>`, true],
      ['Beschreibung', rev.desc||'—', false],
      ['Referenz', rev.ref||'—', false],
    ]);
  } else {
    out += `<p style="color:#999">Kein Revolut-Eingang verknüpft.</p>`;
  }

  if (txs.length) {
    out += `<div class="section">Einzeltransaktionen / Orders (${txs.length})</div>
      <table><tr><th>Datum</th><th>Order</th><th>Typ</th><th style="text-align:right">Betrag EUR</th>
        <th style="text-align:right">Fee</th><th style="text-align:right">Net EUR</th></tr>`;
    for (const tx of txs) {
      const cls = tx.type === 'refund' ? 'neg' : 'pos';
      out += `<tr><td>${fmtDate(tx.date)}</td><td>${tx.order||''}</td><td>${tx.type||''}</td>
        <td style="text-align:right" class="${cls}">${tx.amount_eur.toFixed(2)}</td>
        <td style="text-align:right;color:#888">${tx.fee.toFixed(2)}</td>
        <td style="text-align:right" class="${cls}">${tx.net.toFixed(2)}</td></tr>`;
    }
    out += '</table>';
  }
  return out;
}

function openPayDoc(pk) {
  const p = D.payouts[pk];
  if (!p) return;
  const storeName = D.stores[p.sid]?.name || p.sid;
  const win = window.open('', '_blank');
  win.document.write(docWrap('PAYOUT STATEMENT', `${storeName} / ${p.bank_ref||pk}`, fmtDate(p.date), buildPayDocContent(pk)));
  win.document.close();
}

function buildInvDocContent(revId) {
  const inv = D.invoices.find(i => i.rev_id === revId);
  if (!inv) return '';
  let out = infoGrid([
    ['Lieferant', inv.party, true],
    ['Datum', fmtDate(inv.date), false],
    ['Quartal', inv.q||'', false],
    ['Betrag', `<span class="neg">${inv.amount.toFixed(2)}&nbsp;EUR</span>`, true],
  ]);
  if (inv.doc_url) {
    out += `<div class="section">Dokument</div><p><a href="${inv.doc_url}" target="_blank">${inv.doc_label||'Öffnen'}</a></p>`;
  } else {
    out += `<div class="section">Dokument</div><p style="color:#999">Kein Dokument verknüpft. Bitte manuell dem Auftrag zuordnen.</p>`;
  }
  out += `<div class="section">Revolut Buchung</div>`;
  const r = D.rev.find(x => x.id === revId);
  if (r) {
    out += infoGrid([
      ['Typ', 'TRANSFER', false], ['Datum', fmtDate(r.date), false],
      ['Beschreibung', r.desc||'', false], ['Ref', r.ref||'', false],
    ]);
  }

  // Verknüpfte Aufträge (aus localStorage)
  const linksNow = loadLinks();
  const allocMap = linksNow[revId] || {};
  const linkedOrders = Object.keys(allocMap);
  if (linkedOrders.length > 0) {
    const orderIdx = buildOrderIndex();
    let totalAlloc = 0;
    out += `<div class="section">Verknüpfte Aufträge (${linkedOrders.length})</div>
      <table><tr><th>Order</th><th>Shop</th><th>Datum</th><th>Kunde</th><th style="text-align:right">Warenwert EUR</th></tr>`;
    for (const onum of linkedOrders) {
      const o = orderIdx[onum];
      const amt = allocMap[onum] || 0;
      totalAlloc += amt;
      out += `<tr><td>${onum}</td><td>${o ? (D.stores[o.sid]?.name||o.sid) : '—'}</td>
        <td>${o ? fmtDate(o.date) : '—'}</td>
        <td>${o?.order_data?.customer||'—'}</td>
        <td style="text-align:right" class="neg">-${amt.toFixed(2)}</td></tr>`;
    }
    out += `<tr class="total-row"><td colspan="4">Zugeordnet gesamt</td>
      <td style="text-align:right" class="neg">-${totalAlloc.toFixed(2)}&nbsp;EUR</td></tr></table>`;
    const diff = Math.abs(inv.amount) - totalAlloc;
    if (Math.abs(diff) > 0.01) {
      out += `<p style="color:#e67e22;font-size:12px">&#9888; Restbetrag nicht zugeordnet: ${diff.toFixed(2)} EUR</p>`;
    }
  } else {
    out += `<div class="section">Verknüpfte Aufträge</div><p style="color:#999">Noch keine Aufträge zugeordnet.</p>`;
  }

  return out;
}

function openInvDoc(revId) {
  const inv = D.invoices.find(i => i.rev_id === revId);
  if (!inv) return;
  const win = window.open('', '_blank');
  win.document.write(docWrap('LIEFERANTENRECHNUNG', inv.party, fmtDate(inv.date), buildInvDocContent(revId)));
  win.document.close();
}

// Print ALL documents for current tab
function printAll() {
  let combined = '';
  let title = '';
  const parts = [];

  if (activeTab === 1) {
    title = 'ALLE PAYOUTS Q1/Q2 2026';
    const pkeys = Object.keys(D.payouts)
      .filter(pk => !filterStore || D.payouts[pk].sid === filterStore)
      .sort((a,b) => D.payouts[b].date.localeCompare(D.payouts[a].date));
    pkeys.forEach((pk, i) => {
      parts.push(`<div class="section" style="font-size:16px;color:#1e3a5f">${D.stores[D.payouts[pk].sid]?.name} &mdash; Payout ${fmtDate(D.payouts[pk].date)}</div>` + buildPayDocContent(pk));
      if (i < pkeys.length - 1) parts.push('<div class="page-break"></div>');
    });
  } else if (activeTab === 2) {
    title = 'ALLE ORDERS Q1/Q2 2026';
    const seen = new Set();
    const orderList = [];
    for (const pk of Object.keys(D.payouts)) {
      const p = D.payouts[pk];
      if (filterStore && p.sid !== filterStore) continue;
      for (const tx of (p.transactions||[])) {
        if (tx.order && !seen.has(tx.order)) { seen.add(tx.order); orderList.push(tx.order); }
      }
    }
    orderList.sort().forEach((onum, i) => {
      const allTx = gatherOrderTx(onum);
      if (!allTx.length) return;
      const sid = allTx[0].p.sid;
      parts.push(`<div class="section" style="font-size:16px;color:#1e3a5f">${D.stores[sid]?.name} &mdash; Order ${onum}</div>` + buildOrderDocContent(onum));
      if (i < orderList.length - 1) parts.push('<div class="page-break"></div>');
    });
  } else if (activeTab === 4) {
    title = 'LIEFERANTENRECHNUNGEN Q1/Q2 2026';
    D.invoices.forEach((inv, i) => {
      parts.push(`<div class="section" style="font-size:16px;color:#1e3a5f">${inv.party} &mdash; ${fmtDate(inv.date)}</div>` + buildInvDocContent(inv.rev_id));
      if (i < D.invoices.length - 1) parts.push('<div class="page-break"></div>');
    });
  }

  if (!parts.length) return;
  const win = window.open('', '_blank');
  win.document.write(docWrap(title, 'Sammelausdruck', 'Q1+Q2 2026', parts.join('')));
  win.document.close();
}

// ---- Panel state ----
let panelDocAction = null;

function openPanel(title, html, docFn) {
  document.getElementById('breadcrumb').textContent = title;
  document.getElementById('panelBody').innerHTML = html;
  const docBtn = document.getElementById('panelDocBtn');
  if (docFn) { docBtn.style.display = ''; panelDocAction = docFn; }
  else { docBtn.style.display = 'none'; panelDocAction = null; }
  document.getElementById('panel').classList.add('open');
}

function panelOpenDoc() { if (panelDocAction) panelDocAction(); }

function closePanel() {
  document.getElementById('panel').classList.remove('open');
  panelStack = [];
}

function panelBack() {
  panelStack.pop();
  if (!panelStack.length) { closePanel(); return; }
  const {fn, args} = panelStack[panelStack.length-1];
  fn(...args);
}

function pushOrReplace(fn, args) {
  const top = panelStack[panelStack.length-1];
  if (!top || top.fn !== fn || JSON.stringify(top.args) !== JSON.stringify(args)) {
    panelStack.push({fn, args});
  }
}

// ---- Gather all transactions for an order number ----
function gatherOrderTx(orderNum) {
  const result = [];
  for (const pk of Object.keys(D.payouts)) {
    for (const tx of (D.payouts[pk].transactions||[])) {
      if (tx.order === orderNum) result.push({pk, p: D.payouts[pk], tx});
    }
  }
  result.sort((a,b) => a.tx.date.localeCompare(b.tx.date));
  return result;
}

// ---- Card renderers ----
function openRevCard(revId) {
  const r = D.rev.find(x => x.id === revId);
  if (!r) return;
  const pkeys = D.rev_to_pay[revId] || [];
  let html = `<div class="card-grid">
    <div><div class="card-label">Datum</div><div class="card-value">${fmtDate(r.date)}</div></div>
    <div><div class="card-label">Quartal</div><div class="card-value">${r.q||''}</div></div>
    <div><div class="card-label">Typ</div><div class="card-value">${badge(r.type)}</div></div>
    <div><div class="card-label">Betrag</div><div class="card-value big ${amtCls(r.amount)}">${eur(r.amount)}</div></div>
  </div>
  <div class="card-section"><div class="card-label">Beschreibung</div><div class="card-value">${r.desc||'—'}</div></div>
  <div class="card-section"><div class="card-label">Referenz</div><div class="card-value">${r.ref||'—'}</div></div>`;
  if (r.doc_url) html += `<div class="card-section"><div class="card-label">Dokument</div>
    <a href="${r.doc_url}" target="_blank" class="pdf-link">&#128196; ${r.doc_label||'Öffnen'}</a></div>`;
  if (pkeys.length) {
    html += `<div class="section-title">Verknüpfte Payouts (${pkeys.length})</div><ul class="link-list">`;
    for (const pk of pkeys) {
      const p = D.payouts[pk];
      if (!p) continue;
      html += `<li onclick="openPayCard('${pk}')">
        <span>${badge(null,p.sid)} ${fmtDate(p.date)} &mdash; ${(p.transactions||[]).length} Tx</span>
        <span class="${amtCls(p.total)}">${eur(p.total)} <span class="chevron">›</span></span></li>`;
    }
    html += '</ul>';
  }
  if (D.invoices.find(i=>i.rev_id===revId)) {
    const inv = D.invoices.find(i=>i.rev_id===revId);
    html += `<div class="section-title">Lieferantenrechnung</div>
      <div class="card-section"><div class="card-label">Lieferant</div><div class="card-value">${inv.party}</div></div>
      <div class="card-section"><div class="card-label">Betrag</div><div class="card-value amt-neg">${inv.amount.toFixed(2)} EUR</div></div>`;
    if (inv.doc_url) html += `<a href="${inv.doc_url}" target="_blank" class="pdf-link">&#128196; ${inv.doc_label||'Rechnung'}</a>`;
  }
  pushOrReplace(openRevCard, [revId]);
  openPanel(`${r.type} ${fmtDate(r.date)}`, html, null);
}

function openPayCard(pk) {
  const p = D.payouts[pk];
  if (!p) return;
  const storeName = D.stores[p.sid]?.name || p.sid;
  const revId = D.pay_to_rev[pk];
  const txList = p.transactions || [];
  const orders = [...new Set(txList.map(t=>t.order).filter(Boolean))];
  let html = `<div class="card-grid">
    <div><div class="card-label">Datum</div><div class="card-value">${fmtDate(p.date)}</div></div>
    <div><div class="card-label">Shop</div><div class="card-value">${badge(null,p.sid)}</div></div>
    <div><div class="card-label">Charges</div><div class="card-value amt-pos">+${p.charges.toFixed(2)}</div></div>
    <div><div class="card-label">Refunds</div><div class="card-value ${amtCls(p.refunds)}">${p.refunds.toFixed(2)}</div></div>
    <div><div class="card-label">Fees</div><div class="card-value ${amtCls(p.fees)}">${p.fees.toFixed(2)}</div></div>
    <div><div class="card-label">Total EUR</div><div class="card-value big ${amtCls(p.total)}">${eur(p.total)}</div></div>
  </div>`;
  if (p.bank_ref) html += `<div class="card-section"><div class="card-label">Bank Reference</div>
    <div class="card-value" style="font-size:11px;color:#888">${p.bank_ref}</div></div>`;
  if (p.pdf_path) html += `<div class="card-section"><div class="card-label">PDF</div>
    <a href="file://${p.pdf_path}" target="_blank" class="pdf-link">&#128196; Payout PDF</a></div>`;
  if (revId) {
    const rv = D.rev.find(r=>r.id===revId);
    html += `<div class="section-title">Revolut Buchung</div><ul class="link-list">
      <li onclick="openRevCard('${revId}')">
        <span>${badge(rv?.type||'TOPUP')} ${fmtDate(rv?.date||'')} &mdash; ${rv?.ref||rv?.desc||''}</span>
        <span class="${amtCls(rv?.amount||0)}">${(rv?.amount||0).toFixed(2)} EUR <span class="chevron">›</span></span>
      </li></ul>`;
  }
  if (orders.length) {
    html += `<div class="section-title">Orders (${orders.length})</div><ul class="link-list">`;
    for (const onum of orders) {
      const tx = txList.find(t=>t.order===onum);
      const od = tx?.order_data;
      html += `<li onclick="openOrderCard('${pk}','${onum.replace(/'/g,"\\'")}')">
        <span><strong>${onum}</strong>${od?' &mdash; '+(od.customer||''):''}
          ${tx?.type==='refund'?'<span class="badge badge-refund" style="margin-left:6px">REFUND</span>':''}</span>
        <span class="${amtCls(tx?.net||0)}">${(tx?.net||0).toFixed(2)} EUR <span class="chevron">›</span></span>
      </li>`;
    }
    html += '</ul>';
  } else {
    html += `<div class="section-title">Orders</div><div class="empty-state">Keine Transaktionen</div>`;
  }
  pushOrReplace(openPayCard, [pk]);
  openPanel(`Payout ${storeName} ${fmtDate(p.date)}`, html, () => openPayDoc(pk));
}

function openOrderCard(pk, orderNum) {
  const allTx = gatherOrderTx(orderNum);
  if (!allTx.length) return;
  const {p: primaryP, tx: firstTx} = allTx[0];
  const od = firstTx.order_data;
  const storeName = D.stores[primaryP.sid]?.name || primaryP.sid;

  const sales = allTx.filter(x => x.tx.type !== 'refund');
  const refunds = allTx.filter(x => x.tx.type === 'refund');
  const totalNet = allTx.reduce((a,x)=>a+x.tx.net, 0);
  const totalSaleEur = sales.reduce((a,x)=>a+x.tx.amount_eur, 0);
  const totalRefundEur = refunds.reduce((a,x)=>a+x.tx.amount_eur, 0);

  let html = `<div class="card-grid">
    <div><div class="card-label">Order</div><div class="card-value big">${orderNum}</div></div>
    <div><div class="card-label">Shop</div><div class="card-value">${badge(null,primaryP.sid)}</div></div>
  </div>`;
  if (od) {
    html += `<div class="card-grid">
      <div><div class="card-label">Kunde</div><div class="card-value">${od.customer||'—'}</div></div>
      <div><div class="card-label">E-Mail</div><div class="card-value" style="font-size:11px;color:#555">${od.email||'—'}</div></div>
    </div>`;
  }

  // Charge transactions
  if (sales.length) {
    html += `<div class="section-title">Verkauf${sales.length>1?' ('+sales.length+')':''}</div>`;
    for (const {tx, p} of sales) {
      html += `<div class="tx-sale">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span style="font-weight:600">${fmtDate(tx.date)}</span>
          <span class="amt-pos">+${tx.net.toFixed(2)} EUR net</span>
        </div>
        <div style="font-size:11px;color:#555;display:flex;gap:12px">
          <span>${tx.pres_amount||''} ${tx.pres_currency||''}</span>
          <span>= ${tx.amount_eur.toFixed(2)} EUR</span>
          <span>Fee: ${tx.fee.toFixed(2)} EUR</span>
          <span style="color:#888">Payout: ${fmtDate(p.date)}</span>
        </div>
      </div>`;
    }
  }

  // Refund transactions
  if (refunds.length) {
    html += `<div class="section-title">Rückerstattung${refunds.length>1?' ('+refunds.length+')':''}</div>`;
    for (const {tx, p} of refunds) {
      html += `<div class="tx-refund">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span style="font-weight:600">${fmtDate(tx.date)} &mdash; REFUND</span>
          <span class="amt-neg">${tx.net.toFixed(2)} EUR net</span>
        </div>
        <div style="font-size:11px;color:#555;display:flex;gap:12px">
          <span>${tx.pres_amount||''} ${tx.pres_currency||''}</span>
          <span>= ${tx.amount_eur.toFixed(2)} EUR</span>
          <span style="color:#888">Payout: ${fmtDate(p.date)}</span>
        </div>
      </div>`;
    }
  }

  // Net total
  html += `<div class="tx-net-total" style="margin-top:10px">
    <span>Netto gesamt (nach Shopify-Gebühren)</span>
    <span class="${amtCls(totalNet)}">${totalNet.toFixed(2)} EUR</span>
  </div>`;

  // Items
  if (od && od.items && od.items.length) {
    html += `<div class="section-title">Artikel</div>`;
    for (const item of od.items) {
      html += `<div class="order-item">
        <span>${item.qty}x ${item.name}</span>
        <span style="color:#555">${item.price} ${od.currency}</span>
      </div>`;
    }
  }

  // Payouts link
  html += `<div class="section-title">Payout${allTx.length>1?'s':''}</div><ul class="link-list">`;
  const seenPk = new Set();
  for (const {pk: txPk, p} of allTx) {
    if (seenPk.has(txPk)) continue;
    seenPk.add(txPk);
    html += `<li onclick="openPayCard('${txPk}')">
      <span>Payout ${fmtDate(p.date)} &mdash; ${D.stores[p.sid]?.name}</span>
      <span class="${amtCls(p.total)}">${p.total.toFixed(2)} EUR <span class="chevron">›</span></span>
    </li>`;
  }
  html += '</ul>';

  // Warenkosten (linked supplier invoices, with per-order manual allocation)
  const linkedInvs = getLinkedInvoices(orderNum);
  const linksNow = loadLinks();
  html += `<div class="section-title">Warenkosten (${linkedInvs.length > 0 ? linkedInvs.length + ' Rechnung' + (linkedInvs.length > 1 ? 'en' : '') : 'nicht zugeordnet'})</div>`;
  if (linkedInvs.length > 0) {
    let totalCost = 0;
    html += '<ul class="link-list">';
    for (const inv of linkedInvs) {
      const allocated = linksNow[inv.rev_id]?.[orderNum] || 0; // amount from supplier price list
      totalCost += allocated;
      html += `<li onclick="openInvCard('${inv.rev_id}')">
        <span>${inv.party.split(' ')[0]} ${fmtDate(inv.date)}</span>
        <span class="amt-neg">-${allocated.toFixed(2)} EUR <span class="chevron">›</span></span>
      </li>`;
    }
    html += '</ul>';
    html += `<div class="tx-net-total">
      <span>Warenkosten gesamt</span>
      <span class="amt-neg">-${totalCost.toFixed(2)} EUR</span>
    </div>`;
  } else {
    html += `<div style="color:#999;font-size:12px;padding:8px 0">Noch keine Rechnungen verknüpft.</div>`;
  }

  pushOrReplace(openOrderCard, [pk, orderNum]);
  openPanel(`Order ${orderNum}`, html, () => openOrderDoc(orderNum));
}

// ---- Invoice-Order linking (localStorage) ----
// Format: { revId: { orderNum: eurAmount, ... } }
// Each order gets its own allocated amount (from supplier price list), NOT equal split.
const LINKS_KEY = 'propria_inv_alloc_v2_q1q2_2026';

function loadLinks() {
  try { return JSON.parse(localStorage.getItem(LINKS_KEY) || '{}'); }
  catch(e) { return {}; }
}
function saveLinks(links) {
  localStorage.setItem(LINKS_KEY, JSON.stringify(links));
}

// Link invoice to order with initial amount = full invoice (user adjusts if multiple orders)
function linkInvToOrder(revId, orderNum) {
  const links = loadLinks();
  const inv = D.invoices.find(i=>i.rev_id===revId);
  if (!links[revId]) links[revId] = {};
  if (!(orderNum in links[revId])) {
    // Default: full invoice amount (user will edit when linking multiple orders)
    links[revId][orderNum] = inv ? Math.abs(inv.amount) : 0;
  }
  saveLinks(links);
}

function unlinkInvOrder(revId, orderNum) {
  const links = loadLinks();
  if (links[revId]) {
    delete links[revId][orderNum];
    if (!Object.keys(links[revId]).length) delete links[revId];
  }
  saveLinks(links);
}

// Save manually edited allocation amount for one order
function saveAllocation(revId, orderNum, value) {
  const links = loadLinks();
  if (!links[revId]) links[revId] = {};
  const num = parseFloat(value);
  links[revId][orderNum] = isNaN(num) ? 0 : Math.abs(num);
  saveLinks(links);
}

function getLinkedInvoices(orderNum) {
  const links = loadLinks();
  return D.invoices.filter(inv => links[inv.rev_id] && (orderNum in links[inv.rev_id]));
}

function getAllocatedCost(revId, orderNum) {
  const links = loadLinks();
  return -(links[revId]?.[orderNum] || 0); // negative = expense
}

function applyKfbAutoLinks(revId) {
  const inv = D.invoices.find(i=>i.rev_id===revId);
  if (!inv || !inv.kfb_auto_links) return;
  const links = loadLinks();
  links[revId] = Object.assign({}, inv.kfb_auto_links);
  saveLinks(links);
  openInvCard(revId);
}

function exportLinks() {
  const links = loadLinks();
  const blob = new Blob([JSON.stringify(links, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'invoice_order_links_q1q2_2026.json';
  a.click();
}

function importLinks(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      if (typeof data !== 'object' || Array.isArray(data)) throw new Error('Invalid format');
      saveLinks(data);
      input.value = '';
      render();
      alert('Links importiert: ' + Object.keys(data).length + ' Rechnungen verknüpft.');
    } catch(err) { alert('Fehler beim Import: ' + err.message); }
  };
  reader.readAsText(file);
}

function buildOrderIndex() {
  const idx = {};
  for (const pk of Object.keys(D.payouts)) {
    const p = D.payouts[pk];
    for (const tx of (p.transactions||[])) {
      if (tx.order && !idx[tx.order]) {
        idx[tx.order] = {order_num: tx.order, sid: p.sid, date: tx.date, amount_eur: tx.amount_eur, order_data: tx.order_data};
      }
    }
  }
  return idx;
}

function openInvCard(revId) {
  const inv = D.invoices.find(i=>i.rev_id===revId);
  if (!inv) { openRevCard(revId); return; }
  const links = loadLinks();

  // Auto-populate from KFB data if no manual links exist yet
  if (!links[revId] && inv.kfb_auto_links && Object.keys(inv.kfb_auto_links).length > 0) {
    links[revId] = Object.assign({}, inv.kfb_auto_links);
    saveLinks(links);
  }

  const allocMap = links[revId] || {};   // { orderNum: amount }
  const linkedOrders = Object.keys(allocMap);
  const orderIdx = buildOrderIndex();
  const invAbs = Math.abs(inv.amount);
  const totalAllocated = Object.values(allocMap).reduce((a,v)=>a+v, 0);
  const diff = +(invAbs - totalAllocated).toFixed(2);
  const balanced = Math.abs(diff) < 0.01;

  // Candidate orders: ±45 days, not yet linked
  const invMs = new Date(inv.date).getTime();
  const candidates = Object.values(orderIdx)
    .filter(o => Math.abs(new Date(o.date).getTime() - invMs) <= 45*86400000 && !(o.order_num in allocMap))
    .sort((a,b) => Math.abs(new Date(a.date)-invMs) - Math.abs(new Date(b.date)-invMs))
    .slice(0, 25);

  let html = `<div class="card-grid">
    <div><div class="card-label">Lieferant</div><div class="card-value" style="font-weight:700">${inv.party}</div></div>
    <div><div class="card-label">Datum</div><div class="card-value">${fmtDate(inv.date)} ${qTag(inv.q)}</div></div>
    <div><div class="card-label">Rechnungsbetrag</div><div class="card-value big amt-neg">-${invAbs.toFixed(2)} EUR</div></div>
    <div><div class="card-label">Zugeordnet</div><div class="card-value ${balanced?'amt-neg':''}">
      ${totalAllocated > 0 ? `-${totalAllocated.toFixed(2)} EUR` : '—'}
      ${!balanced && linkedOrders.length > 0 ? `<span style="color:#e67e22;font-size:10px;display:block">Restbetrag: ${diff > 0 ? '-' : '+'}${Math.abs(diff).toFixed(2)} EUR</span>` : ''}
    </div></div>
  </div>`;

  if (inv.doc_url) html += `<div class="card-section"><div class="card-label">Dokument</div>
    <a href="${inv.doc_url}" target="_blank" class="pdf-link">&#128196; ${inv.doc_label||'Öffnen'}</a></div>`;

  // KFB bill details (for East Baite invoices)
  if (inv.kfb_bill_data && inv.kfb_bill_data.length > 0) {
    html += `<div class="section-title">Kungfu Buy Rechnungen (${inv.kfb_bills.length})</div>
      <div style="font-size:12px">`;
    for (const bill of inv.kfb_bill_data) {
      html += `<div style="background:#f8f9fa;border:1px solid #e8ecf0;border-radius:6px;padding:8px 10px;margin-bottom:6px">
        <div style="font-weight:600;color:#1e3a5f">Bill ${bill.bill_no} &mdash; ${bill.bill_time} &mdash; <span class="neg">-${bill.amount_eur.toFixed(2)} EUR</span></div>`;
      for (const o of bill.orders || []) {
        html += `<div style="color:#555;margin-top:4px;padding-left:8px">
          <strong>${o.shopify_name}</strong> &mdash; ${o.product} &mdash; ${o.buyer} (${o.country})
          <span class="neg" style="float:right">-${o.amount.toFixed(2)} EUR</span>
        </div>`;
      }
      html += `</div>`;
    }
    html += `</div>`;
    if (!links[revId] || Object.keys(links[revId]).length === 0) {
      html += `<button onclick="applyKfbAutoLinks('${revId}')" style="margin-bottom:10px;background:#e8f4fd;color:#1565c0;border:1px solid #90caf9;border-radius:4px;padding:4px 10px;cursor:pointer;font-size:11px">&#128279; KFB-Zuordnung anwenden</button>`;
    }
  }

  // Linked orders with editable amounts
  html += `<div class="section-title">Verknüpfte Aufträge (${linkedOrders.length})`;
  if (!balanced && linkedOrders.length > 0) html += ` <span style="color:#e67e22;font-size:11px;font-weight:400">&#9888; Summe stimmt nicht überein</span>`;
  html += '</div>';

  if (linkedOrders.length) {
    html += '<ul class="link-list">';
    for (const onum of linkedOrders) {
      const o = orderIdx[onum];
      const amt = allocMap[onum];
      const safeOnum = onum.replace(/'/g,"\\'").replace(/"/g,'&quot;');
      html += `<li style="justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
        <span onclick="openOrderCard('','${safeOnum}')" style="flex:1;min-width:120px;cursor:pointer">
          <strong>${onum}</strong>${o?' &mdash; '+fmtDate(o.date)+' &mdash; '+(o.order_data?.customer||''):''}
        </span>
        <span style="display:flex;gap:6px;align-items:center">
          <input type="number" step="0.01" min="0" value="${amt.toFixed(2)}"
            style="width:80px;border:1px solid #ccc;border-radius:4px;padding:3px 6px;font-size:12px;text-align:right"
            onchange="saveAllocation('${revId}','${safeOnum}',this.value);openInvCard('${revId}')"
            onclick="event.stopPropagation()" title="Warenwert laut Lieferanten-Preisliste">
          <span style="font-size:11px;color:#888">EUR</span>
          <button onclick="event.stopPropagation();unlinkInvOrder('${revId}','${safeOnum}');openInvCard('${revId}')"
            style="background:#fde8e8;color:#c0392b;border:none;border-radius:4px;padding:2px 8px;cursor:pointer;font-size:11px">&#10005;</button>
        </span>
      </li>`;
    }
    html += '</ul>';
    if (!balanced && linkedOrders.length > 0) {
      html += `<div style="font-size:11px;color:#e67e22;padding:4px 0 8px">
        Tipp: Summe aller Aufträge soll ${invAbs.toFixed(2)} EUR ergeben (laut Lieferantenrechnung).
      </div>`;
    }
  } else {
    html += `<div style="color:#999;font-size:12px;padding:8px 0">Noch keine Aufträge zugeordnet.</div>`;
  }

  // Candidate orders
  html += `<div class="section-title">Kandidaten (±45 Tage, ${candidates.length})</div>`;
  if (candidates.length) {
    html += '<ul class="link-list">';
    for (const o of candidates) {
      const diffDays = Math.round(Math.abs(new Date(o.date).getTime()-invMs)/86400000);
      const safeOnum = o.order_num.replace(/'/g,"\\'");
      html += `<li onclick="event.stopPropagation();linkInvToOrder('${revId}','${safeOnum}');openInvCard('${revId}')">
        <span><strong>${o.order_num}</strong> ${badge(null,o.sid)} ${fmtDate(o.date)}
          ${o.order_data?.customer?' &mdash; '+o.order_data.customer:''}
          <span style="color:#aaa;font-size:10px;margin-left:4px">±${diffDays}d</span>
        </span>
        <span style="display:flex;gap:6px;align-items:center">
          <span style="color:#888;font-size:11px">${o.amount_eur.toFixed(2)} EUR</span>
          <span style="background:#e8f4fd;color:#1565c0;border-radius:4px;padding:2px 8px;font-size:11px;cursor:pointer">+ Zuordnen</span>
        </span>
      </li>`;
    }
    html += '</ul>';
  } else {
    html += `<div style="color:#999;font-size:12px;padding:8px 0">Keine Kandidaten im Zeitraum ±45 Tage.</div>`;
  }

  html += `<div style="margin-top:16px;padding-top:12px;border-top:1px solid #eee;display:flex;gap:8px">
    <button onclick="exportLinks()" style="background:none;border:1px solid #1e3a5f;color:#1e3a5f;border-radius:4px;padding:5px 12px;cursor:pointer;font-size:11px">&#8595; Links exportieren</button>
  </div>`;

  pushOrReplace(openInvCard, [revId]);
  openPanel(`Rechnung ${inv.party.split(' ')[0]} ${fmtDate(inv.date)}`, html, () => openInvDoc(revId));
}

// ---- Table renderers ----
function docIconBtn(fn, arg1, arg2) {
  const args = arg2 !== undefined ? `'${fn}','${arg1}','${arg2}'` : `'${fn}','${arg1}'`;
  return `<button class="row-doc-btn" onclick="event.stopPropagation();docDispatch(${args})" title="Dokument öffnen">&#128196;</button>`;
}
function docDispatch(fn, a1, a2) {
  if (fn==='order') openOrderDoc(a1);
  else if (fn==='pay') openPayDoc(a1);
  else if (fn==='inv') openInvDoc(a1);
}

function renderRevolutTable() {
  let rows = D.rev.filter(r => !filterType || r.type === filterType);
  let html = `<table><thead><tr>
    <th>Datum</th><th>Q</th><th>Typ</th><th>Beschreibung</th><th>Ref</th>
    <th style="text-align:right">Betrag</th><th style="text-align:right">Saldo</th>
  </tr></thead><tbody>`;
  for (const r of rows) {
    html += `<tr onclick="openRevCard('${r.id}')">
      <td>${fmtDate(r.date)}</td><td>${qTag(r.q)}</td><td>${badge(r.type)}</td>
      <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${r.desc||''}</td>
      <td style="max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#888;font-size:11px">${r.ref||''}</td>
      <td style="text-align:right" class="${amtCls(r.amount)}">${eur(r.amount)}</td>
      <td style="text-align:right;color:#555">${r.balance?r.balance.toFixed(2):''}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}

function renderPayoutsTable() {
  const pkeys = Object.keys(D.payouts)
    .filter(pk => !filterStore || D.payouts[pk].sid === filterStore)
    .sort((a,b) => D.payouts[b].date.localeCompare(D.payouts[a].date));
  let html = `<table><thead><tr>
    <th>Datum</th><th>Q</th><th>Shop</th><th>Charges</th><th>Refunds</th><th>Fees</th>
    <th style="text-align:right">Total EUR</th><th>Rev.</th><th></th>
  </tr></thead><tbody>`;
  for (const pk of pkeys) {
    const p = D.payouts[pk];
    const rev = D.pay_to_rev[pk] ? '&#10003;' : '<span class="unmatched">?</span>';
    html += `<tr onclick="openPayCard('${pk}')">
      <td>${fmtDate(p.date)}</td><td>${qTag(p.q)}</td><td>${badge(null,p.sid)}</td>
      <td class="amt-pos">${p.charges>0?'+'+p.charges.toFixed(2):''}</td>
      <td class="${amtCls(p.refunds)}">${p.refunds!==0?p.refunds.toFixed(2):''}</td>
      <td class="${amtCls(p.fees)}">${p.fees!==0?p.fees.toFixed(2):''}</td>
      <td style="text-align:right" class="${amtCls(p.total)}">${eur(p.total)}</td>
      <td style="text-align:center">${rev}</td>
      <td>${docIconBtn('pay',pk)}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}

function renderOrdersTable() {
  const seen = new Set();
  const orderList = [];
  for (const pk of Object.keys(D.payouts)) {
    const p = D.payouts[pk];
    if (filterStore && p.sid !== filterStore) continue;
    for (const tx of (p.transactions||[])) {
      if (tx.order && !seen.has(tx.order)) {
        seen.add(tx.order);
        orderList.push({pk, p, tx});
      }
    }
  }
  orderList.sort((a,b) => b.tx.date.localeCompare(a.tx.date));

  let html = `<table><thead><tr>
    <th>Datum</th><th>Shop</th><th>Order</th><th>Kunde</th>
    <th style="text-align:right">Betrag (Lokal)</th><th style="text-align:right">Net EUR</th><th></th>
  </tr></thead><tbody>`;
  for (const {pk, p, tx} of orderList) {
    // Check for refunds
    const allTx = gatherOrderTx(tx.order);
    const hasRefund = allTx.some(x=>x.tx.type==='refund');
    const totalNet = allTx.reduce((a,x)=>a+x.tx.net,0);
    const od = tx.order_data;
    const customer = od ? (od.customer||od.email||'') : '';
    const pres = tx.pres_amount ? `${tx.pres_amount} ${tx.pres_currency}` : '';
    html += `<tr onclick="openOrderCard('${pk}','${tx.order.replace(/'/g,"\\'")}')">
      <td>${fmtDate(tx.date)}</td><td>${badge(null,p.sid)}</td>
      <td style="font-weight:500">${tx.order}${hasRefund?' <span class="badge badge-refund" style="font-size:9px">R</span>':''}</td>
      <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#555">${customer}</td>
      <td style="text-align:right;color:#888">${pres}</td>
      <td style="text-align:right" class="${amtCls(totalNet)}">${totalNet.toFixed(2)}</td>
      <td>${docIconBtn('order',tx.order)}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}

function renderTransactionsTable() {
  const allTx = [];
  for (const pk of Object.keys(D.payouts)) {
    const p = D.payouts[pk];
    if (filterStore && p.sid !== filterStore) continue;
    for (const tx of (p.transactions||[])) allTx.push({pk, p, tx});
  }
  allTx.sort((a,b) => b.tx.date.localeCompare(a.tx.date));
  let html = `<table><thead><tr>
    <th>Datum</th><th>Shop</th><th>Order</th><th>Typ</th>
    <th style="text-align:right">Presentment</th><th style="text-align:right">Betrag EUR</th>
    <th style="text-align:right">Fee</th><th style="text-align:right">Net EUR</th>
  </tr></thead><tbody>`;
  for (const {pk, p, tx} of allTx) {
    html += `<tr onclick="openPayCard('${pk}')">
      <td>${fmtDate(tx.date)}</td><td>${badge(null,p.sid)}</td>
      <td style="font-weight:500">${tx.order||''}</td>
      <td>${badge(tx.type)}</td>
      <td style="text-align:right;color:#888">${tx.pres_amount||''} ${tx.pres_currency||''}</td>
      <td style="text-align:right" class="${amtCls(tx.amount_eur)}">${tx.amount_eur.toFixed(2)}</td>
      <td style="text-align:right;color:#888">${tx.fee?tx.fee.toFixed(2):''}</td>
      <td style="text-align:right" class="${amtCls(tx.net)}">${tx.net.toFixed(2)}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}

function renderInvoicesTable() {
  let html = `<table><thead><tr>
    <th>Datum</th><th>Q</th><th>Lieferant</th><th style="text-align:right">Betrag EUR</th><th>Dokument</th><th></th>
  </tr></thead><tbody>`;
  for (const inv of D.invoices) {
    const docLink = inv.doc_url
      ? `<a href="${inv.doc_url}" target="_blank" class="pdf-link">&#128196; ${inv.doc_label||'Dok.'}</a>`
      : '<span style="color:#ccc">—</span>';
    const links = loadLinks();
    const linkedCount = (links[inv.rev_id]||[]).length;
    const linkBadge = linkedCount > 0
      ? `<span style="background:#d4edda;color:#0a7c3c;border-radius:10px;font-size:10px;font-weight:600;padding:1px 7px;margin-left:6px">${linkedCount} Order${linkedCount>1?'s':''}</span>`
      : `<span style="color:#ccc;font-size:10px;margin-left:6px">nicht zugeordnet</span>`;
    html += `<tr onclick="openInvCard('${inv.rev_id}')">
      <td>${fmtDate(inv.date)}</td><td>${qTag(inv.q)}</td>
      <td style="font-weight:500">${inv.party||''}${linkBadge}</td>
      <td style="text-align:right" class="amt-neg">${inv.amount.toFixed(2)}&nbsp;EUR</td>
      <td>${docLink}</td>
      <td>${docIconBtn('inv',inv.rev_id)}</td>
    </tr>`;
  }
  return html + '</tbody></table>';
}

// ---- P&L tab ----
function renderPLTable() {
  const storeIds = ['mf','oa','ct','cg'];
  const storeNames = {mf:'Marc&François', oa:'Oliver & Alder', ct:'Charlie & Ted', cg:'Casa Giannini'};

  // Per-store aggregation, also split Q1/Q2
  const storeData = {};
  for (const sid of storeIds) {
    storeData[sid] = {q1:{charges:0,refunds:0,fees:0,net:0}, q2:{charges:0,refunds:0,fees:0,net:0}};
  }
  for (const p of Object.values(D.payouts)) {
    const sd = storeData[p.sid];
    if (!sd) continue;
    const q = p.q === 'Q1' ? 'q1' : 'q2';
    sd[q].charges += p.charges;
    sd[q].refunds += p.refunds;
    sd[q].fees += p.fees;
    sd[q].net += p.total;
  }

  function col(v, cls) {
    const c = cls || amtCls(v);
    return `<td class="${c}">${v===0?'—':v.toFixed(2)}</td>`;
  }

  let html = `<div class="pl-section">
    <div class="pl-section-title">Umsatz nach Shop &mdash; Q1/Q2 2026</div>
    <table class="pl-table">
      <tr><th>Shop</th>
        <th>Q1 Umsatz</th><th>Q1 Refunds</th><th>Q1 Fees</th><th>Q1 Net</th>
        <th style="border-left:2px solid #dde1e7">Q2 Umsatz</th><th>Q2 Refunds</th><th>Q2 Fees</th><th>Q2 Net</th>
        <th style="border-left:2px solid #dde1e7">Total Net</th>
      </tr>`;

  let totQ1 = {charges:0,refunds:0,fees:0,net:0}, totQ2 = {charges:0,refunds:0,fees:0,net:0};
  for (const sid of storeIds) {
    const {q1,q2} = storeData[sid];
    const totalNet = q1.net + q2.net;
    for (const k of ['charges','refunds','fees','net']) { totQ1[k]+=q1[k]; totQ2[k]+=q2[k]; }
    html += `<tr>
      <td style="font-weight:600;text-align:left">${badge(null,sid)} ${storeNames[sid]}</td>
      ${col(q1.charges,'amt-pos')}${col(q1.refunds)}${col(q1.fees)}${col(q1.net)}
      <td style="border-left:2px solid #f0f2f5">${q2.charges?'<span class="amt-pos">+'+q2.charges.toFixed(2)+'</span>':'—'}</td>
      ${col(q2.refunds)}${col(q2.fees)}${col(q2.net)}
      <td style="border-left:2px solid #dde1e7;font-weight:700" class="${amtCls(totalNet)}">${totalNet.toFixed(2)}</td>
    </tr>`;
  }

  const grandNet = totQ1.net + totQ2.net;
  html += `<tr class="total-row">
    <td>Gesamt</td>
    ${col(totQ1.charges,'amt-pos')}${col(totQ1.refunds)}${col(totQ1.fees)}<td class="${amtCls(totQ1.net)}" style="font-weight:700">${totQ1.net.toFixed(2)}</td>
    <td style="border-left:2px solid #dde1e7;font-weight:700" class="amt-pos">+${totQ2.charges.toFixed(2)}</td>
    ${col(totQ2.refunds)}${col(totQ2.fees)}<td class="${amtCls(totQ2.net)}" style="font-weight:700">${totQ2.net.toFixed(2)}</td>
    <td style="border-left:2px solid #dde1e7;font-weight:700;font-size:15px" class="${amtCls(grandNet)}">${grandNet.toFixed(2)}</td>
  </tr></table></div>`;

  // Supplier costs
  const suppTotal = D.invoices.reduce((a,i)=>a+i.amount, 0);
  const suppQ1 = D.invoices.filter(i=>i.q==='Q1').reduce((a,i)=>a+i.amount,0);
  const suppQ2 = D.invoices.filter(i=>i.q==='Q2').reduce((a,i)=>a+i.amount,0);
  function suppByQ(party) {
    return {
      q1: D.invoices.filter(i=>i.party.includes(party)&&i.q==='Q1').reduce((a,i)=>a+i.amount,0),
      q2: D.invoices.filter(i=>i.party.includes(party)&&i.q==='Q2').reduce((a,i)=>a+i.amount,0),
      tot: D.invoices.filter(i=>i.party.includes(party)).reduce((a,i)=>a+i.amount,0),
    };
  }
  const hst = suppByQ('HST'), eb = suppByQ('EAST');
  function negCell(v) { return v!==0?`<td class="amt-neg">${v.toFixed(2)}</td>`:`<td style="color:#ccc">—</td>`; }

  html += `<div class="pl-section">
    <div class="pl-section-title">Warenkosten (Lieferanten)</div>
    <table class="pl-table">
      <tr><th>Lieferant</th><th>Q1</th><th>Q2</th><th>Total</th></tr>
      <tr><td>HST Electronics</td>${negCell(hst.q1)}${negCell(hst.q2)}<td class="amt-neg">${hst.tot.toFixed(2)}</td></tr>
      <tr><td>East Baite Limited</td>${negCell(eb.q1)}${negCell(eb.q2)}<td class="amt-neg">${eb.tot.toFixed(2)}</td></tr>
      <tr class="total-row"><td>Total Warenkosten</td>
        <td class="amt-neg">${suppQ1.toFixed(2)}</td>
        <td class="amt-neg">${suppQ2.toFixed(2)}</td>
        <td class="amt-neg">${suppTotal.toFixed(2)}</td>
      </tr>
    </table>
    <p style="padding:8px 12px;font-size:11px;color:#888;border-top:1px solid #f0f2f5">
      Hinweis: Warenkosten noch nicht einzelnen Auftr&auml;gen zugeordnet. N&auml;chster Schritt: manuelle Zuordnung Rechnung &rarr; Order.
    </p>
  </div>`;

  // Margin summary
  const margin = grandNet + suppTotal;
  html += `<div class="pl-section">
    <div class="pl-section-title">Marge</div>
    <table class="pl-table">
      <tr><th>Position</th><th>Q1</th><th>Q2</th><th>Total</th></tr>
      <tr><td>Netto Payout (nach Shopify-Geb.)</td>
        <td class="${amtCls(totQ1.net)}">${totQ1.net.toFixed(2)}</td>
        <td class="${amtCls(totQ2.net)}">${totQ2.net.toFixed(2)}</td>
        <td class="${amtCls(grandNet)}" style="font-weight:700">${grandNet.toFixed(2)}</td>
      </tr>
      <tr><td>Warenkosten</td>
        <td class="amt-neg">${suppQ1.toFixed(2)}</td>
        <td class="amt-neg">${suppQ2.toFixed(2)}</td>
        <td class="amt-neg">${suppTotal.toFixed(2)}</td>
      </tr>
      <tr class="${margin>=0?'margin-row':'margin-neg'}">
        <td>Brutto-Marge</td>
        <td class="${amtCls(totQ1.net+suppQ1)}">${(totQ1.net+suppQ1).toFixed(2)}</td>
        <td class="${amtCls(totQ2.net+suppQ2)}">${(totQ2.net+suppQ2).toFixed(2)}</td>
        <td>${margin.toFixed(2)}&nbsp;EUR</td>
      </tr>
    </table>
  </div>`;

  return html;
}

// ---- Summary bar ----
function renderSummary() {
  const sb = document.getElementById('summaryBar');
  if (activeTab === 0) {
    const rev = D.rev;
    const totalIn = rev.filter(r=>r.amount>0).reduce((a,r)=>a+r.amount,0);
    const totalOut = rev.filter(r=>r.amount<0).reduce((a,r)=>a+r.amount,0);
    const topups = rev.filter(r=>r.type==='TOPUP').reduce((a,r)=>a+r.amount,0);
    sb.innerHTML = `
      <div class="summary-item"><span class="s-label">Eingang</span><span class="s-val">+${totalIn.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Ausgang</span><span class="s-val">${totalOut.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Shopify Payouts</span><span class="s-val">+${topups.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Einträge</span><span class="s-val">${rev.length}</span></div>`;
  } else if (activeTab === 1) {
    const pays = Object.values(D.payouts);
    const pos = pays.filter(p=>p.total>0).reduce((a,p)=>a+p.total,0);
    const neg = pays.filter(p=>p.total<0).reduce((a,p)=>a+p.total,0);
    sb.innerHTML = `
      <div class="summary-item"><span class="s-label">Positive Payouts</span><span class="s-val">+${pos.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Negative Payouts</span><span class="s-val">${neg.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Anzahl</span><span class="s-val">${pays.length}</span></div>`;
  } else if (activeTab === 4) {
    const total = D.invoices.reduce((a,i)=>a+i.amount,0);
    const hst = D.invoices.filter(i=>i.party.includes('HST')).reduce((a,i)=>a+i.amount,0);
    const eb = D.invoices.filter(i=>i.party.includes('EAST')).reduce((a,i)=>a+i.amount,0);
    sb.innerHTML = `
      <div class="summary-item"><span class="s-label">Gesamt</span><span class="s-val">${total.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">HST Electronics</span><span class="s-val">${hst.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">East Baite</span><span class="s-val">${eb.toFixed(2)} EUR</span></div>
      <div class="summary-item"><span class="s-label">Rechnungen</span><span class="s-val">${D.invoices.length}</span></div>`;
  } else {
    sb.innerHTML = '';
  }
}

// ---- Filter bar ----
function renderFilters() {
  const fb = document.getElementById('filterBar');
  const stores = [['','Alle Shops'],['mf','Marc&François'],['oa','Oliver & Alder'],['ct','Charlie & Ted'],['cg','Casa Giannini']];
  let html = '';
  if (activeTab === 0) {
    const types = [['','Alle'],['TOPUP','Payouts'],['TRANSFER','Transfer'],['CARD_PAYMENT','Karte'],['FEE','Gebühr'],['REWARD','Reward']];
    html = types.map(([v,l])=>`<button class="filter-btn ${filterType===v?'active':''}" onclick="setFilter('type','${v}')">${l}</button>`).join('');
  } else if ([1,2,3].includes(activeTab)) {
    html = stores.map(([v,l])=>`<button class="filter-btn ${filterStore===v?'active':''}" onclick="setFilter('store','${v}')">${l}</button>`).join('');
    if ([1,2,4].includes(activeTab)) {
      html += `<button class="print-all-btn" onclick="printAll()">&#128424; Alle drucken / PDF</button>`;
    }
  } else if (activeTab === 4) {
    const totalLinked = (() => { const l = loadLinks(); return Object.values(l).reduce((a,v)=>a+v.length,0); })();
    html = `<button class="print-all-btn" onclick="printAll()">&#128424; Alle Rechnungen drucken / PDF</button>
      <button class="filter-btn" onclick="exportLinks()" style="margin-left:8px">&#8595; Links exportieren${totalLinked>0?' ('+totalLinked+')':''}</button>
      <label class="filter-btn" style="cursor:pointer;margin-left:4px">&#8593; Links importieren
        <input type="file" accept=".json" style="display:none" onchange="importLinks(this)">
      </label>`;
  } else if (activeTab === 5) {
    html = '';
  }
  fb.innerHTML = html;
}

function setFilter(kind, val) {
  if (kind==='type') filterType=val;
  else if (kind==='store') filterStore=val;
  render();
}

function renderTable() {
  const tc = document.getElementById('tableContainer');
  if (activeTab===0) tc.innerHTML = renderRevolutTable();
  else if (activeTab===1) tc.innerHTML = renderPayoutsTable();
  else if (activeTab===2) tc.innerHTML = renderOrdersTable();
  else if (activeTab===3) tc.innerHTML = renderTransactionsTable();
  else if (activeTab===4) tc.innerHTML = renderInvoicesTable();
  else if (activeTab===5) tc.innerHTML = renderPLTable();
}

render();
</script>
</body>
</html>
"""


def main():
    print("Loading Revolut data...")
    revolut = load_revolut()
    print(f"  {len(revolut)} transactions")

    print("Loading store data...")
    store_data = {}
    for sid, cfg in STORES.items():
        payouts, orders = load_store(sid, cfg)
        store_data[sid] = (payouts, orders)
        print(f"  {cfg['name']}: {len(payouts)} payouts, {len(orders)} orders")

    print("Building data model...")
    D = build_data(revolut, store_data)
    matched = sum(1 for pk in D["payouts"] if D["pay_to_rev"].get(pk))
    print(f"  {len(D['payouts'])} payouts, {matched} matched to Revolut")
    print(f"  {len(D['invoices'])} supplier invoices")

    print("Generating HTML...")
    data_js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__DATA__", data_js)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT) / 1024
    print(f"Done: {OUT} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()

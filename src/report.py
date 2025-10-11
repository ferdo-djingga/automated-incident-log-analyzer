import csv, os, html
from collections import Counter
from datetime import datetime

SUGGESTED = {
    "HTTP_5xx": "Check upstream health, review app errors, adjust timeouts",
    "TIMEOUT": "Inspect network latency and upstream service health, tune timeouts",
    "NETWORK": "Verify connectivity, DNS, firewall; check packet loss",
    "AUTH": "Validate credentials flow, identity provider status, lockouts",
    "DISK": "Check disk space/IO, rotate logs, restart impacted service",
    "DB": "Check DB connectivity, pool size, slow queries",
    "DEFAULT": "Review logs, escalate with context, attach HTML report"
}

def write_csv(rows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "report.csv")
    header = ["summary","severity","category","count","first_seen","last_seen","suggested_action"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(k,"") for k in header])
    return csv_path

def write_html(summary, rows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    html_path = os.path.join(out_dir, "report.html")
    # Escaping
    def esc(x): return html.escape(str(x))
    # Simple table rows
    trs = "\n".join([
        f"<tr><td>{esc(r['summary'])}</td><td>{esc(r['severity'])}</td><td>{esc(r['category'])}</td>"
        f"<td>{r['count']}</td><td>{esc(r['first_seen'])}</td><td>{esc(r['last_seen'])}</td><td>{esc(r['suggested_action'])}</td></tr>"
        for r in rows
    ])
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Log Analyzer Report</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:24px;}}
h1{{margin:0 0 8px 0}} h2{{margin-top:24px}}
table{{border-collapse:collapse;width:100%;}}
th,td{{border:1px solid #ddd;padding:8px;font-size:14px;}}
th{{background:#f4f4f4;text-align:left;}}
.badge{{display:inline-block;padding:2px 8px;border-radius:6px;background:#eee;margin-right:6px;}}
</style></head>
<body>
<h1>Log Analyzer Report</h1>
<div>
  <span class="badge">Total lines: {summary['total_lines']}</span>
  <span class="badge">Errors: {summary['err_count']}</span>
  <span class="badge">Warnings: {summary['warn_count']}</span>
  <span class="badge">Critical: {summary['crit_count']}</span>
</div>
<h2>Top Incidents</h2>
<table>
  <thead><tr><th>Summary</th><th>Severity</th><th>Category</th><th>Count</th><th>First Seen</th><th>Last Seen</th><th>Suggested Action</th></tr></thead>
  <tbody>
    {trs}
  </tbody>
</table>
</body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return html_path

def aggregate(records):
    # records: list of dicts with timestamp(str), level, source, message, category
    counts = {}
    total = len(records)
    err = sum(1 for r in records if r.get("level") in ("ERROR","ERR","CRITICAL"))
    warn = sum(1 for r in records if r.get("level") == "WARN")
    crit = sum(1 for r in records if r.get("level") == "CRITICAL")
    # group by (category, level, summary_key)
    def summary_key(r):
        cat = r.get("category") or "UNCATEGORIZED"
        lvl = r.get("level") or "INFO"
        msg = r.get("message","")
        short = (msg[:70] + "...") if len(msg) > 70 else msg
        return (cat, lvl, short)
    for r in records:
        k = summary_key(r)
        d = counts.setdefault(k, {"count":0, "first_seen":None, "last_seen":None})
        d["count"] += 1
        ts = r.get("timestamp")
        if ts:
            if d["first_seen"] is None or ts < d["first_seen"]:
                d["first_seen"] = ts
            if d["last_seen"] is None or ts > d["last_seen"]:
                d["last_seen"] = ts
    # Convert to rows for CSV/HTML
    rows = []
    for (cat, lvl, short), d in sorted(counts.items(), key=lambda x: -x[1]["count"])[:50]:
        action = SUGGESTED.get(cat, SUGGESTED["DEFAULT"])
        rows.append({
            "summary": short,
            "severity": lvl,
            "category": cat,
            "count": d["count"],
            "first_seen": d["first_seen"] or "",
            "last_seen": d["last_seen"] or "",
            "suggested_action": action
        })
    summary = {"total_lines": total, "err_count": err, "warn_count": warn, "crit_count": crit}
    return summary, rows
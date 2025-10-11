import argparse
import time

from parsers import apache, nginx, syslog, jsonapp
from report import aggregate, write_csv, write_html

# All parsers we support
PARSERS = {
    "apache": apache,
    "nginx": nginx,
    "syslog": syslog,
    "app": jsonapp,
}

def auto_detect(path: str) -> str:
    """
    Read the first ~50 non-empty lines, score how many lines each parser can handle,
    and pick the parser with the highest score. On ties, use a safe priority.
    This avoids overly-permissive patterns from winning accidentally.
    """
    lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for _ in range(120):  # sample enough lines to be robust
            ln = f.readline()
            if not ln:
                break
            ln = ln.rstrip("\n")
            if ln.strip():
                lines.append(ln)
            if len(lines) >= 50:
                break

    if not lines:
        return "syslog"

    # Score each parser by how many lines it can parse
    scores = {name: 0 for name in PARSERS}
    for ln in lines:
        for name, mod in PARSERS.items():
            try:
                if mod.can_parse(ln):
                    scores[name] += 1
            except Exception:
                pass

    # Tie-breaker priority: JSON (distinct) > Apache > Nginx > Syslog
    priority = ["app", "apache", "nginx", "syslog"]

    # Choose best by (score desc, priority index asc)
    best = max(scores.items(), key=lambda kv: (kv[1], -priority.index(kv[0])))
    return best[0] if best[1] > 0 else "syslog"

def main():
    ap = argparse.ArgumentParser(description="Simple Log Analyzer")
    ap.add_argument("--input", required=True, help="Path to log file")
    ap.add_argument("--type", default="auto", choices=["auto", "apache", "nginx", "syslog", "app"])
    ap.add_argument("--out", default="output", help="Output directory")
    args = ap.parse_args()

    # Decide log type
    log_type = args.type if args.type != "auto" else auto_detect(args.input)
    parser = PARSERS[log_type]

    # Parse and report
    t0 = time.time()
    records = parser.parse(args.input)
    summary, rows = aggregate(records)
    csv_path = write_csv(rows, args.out)
    html_path = write_html(summary, rows, args.out)
    dt = time.time() - t0

    print(f"[OK] Parsed as: {log_type}")
    print(f"[OK] Total lines: {summary['total_lines']}, errors: {summary['err_count']}, warnings: {summary['warn_count']}, critical: {summary['crit_count']}")
    print(f"[OK] Wrote: {csv_path}")
    print(f"[OK] Wrote: {html_path}")
    print(f"[OK] Elapsed: {dt:.3f}s")

if __name__ == "__main__":
    main()
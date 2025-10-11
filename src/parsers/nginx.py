import re

# Nginx error log example (both shapes should be supported):
# 2025/06/01 12:30:01 [error] 1204#0: *12 connect() failed (111: Connection refused) while connecting to upstream, ...
# 2025/06/01 12:30:05 [warn] an upstream response is buffered to a temporary file ...

NGINX_ERR = re.compile(
    r"^(?P<ts>\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})\s"        # timestamp
    r"\[(?P<level>error|crit|warn|notice|info|debug)\]\s"     # [level]
    r"(?!\[client\s)"                                         # NOT Apache's [client ...]
    r"(?:\d+#\d+:\s\*\d+\s)?"                                 # optional 'PID#worker: *req '
    r"(?P<msg>.+)$",                                          # message
    re.IGNORECASE
)

# Simple keyword heuristics for severity/category
KEYWORDS = {
    "CRITICAL": ["fatal", "kernel oops", "panic"],
    "ERROR": ["error", "exception", "timeout", "upstream timed out", "bad gateway", "refused", "connect() failed"],
    "WARN": ["warn", "deprecated", "retry", "slow", "buffered to a temporary file"],
}

CATEGORIES = {
    "HTTP_5xx": ["500", "502", "503", "504", "upstream", "bad gateway"],
    "TIMEOUT": ["timeout", "timed out", "upstream timed out"],
    "NETWORK": ["connection refused", "refused", "dns", "unreachable", "connect() failed"],
    "AUTH": ["unauthorized", "forbidden", "invalid credentials", "auth_fail"],
    "DISK": ["no space left", "disk full", "io error"],
    "DB": ["database", "db", "query failed", "deadlock"],
}

def can_parse(line: str) -> bool:
    """
    True only if the line looks like an Nginx error entry.
    We accept one of:
      - explicit Nginx worker/request block: "1204#0: *12 "
      - OR nginx-ish tokens like 'upstream', 'request:', 'server:', 'host:', ' while '
    And we reject Apache's '[client ...]' marker.
    """
    line = (line or "")
    m = NGINX_ERR.match(line)
    if not m:
        return False

    # Reject Apache-style "[client ...]"
    if "[client " in line:
        return False

    # Accept immediately if PID/worker/request fragment is present
    if re.search(r"\d+#\d+:\s\*\d+\s", line):
        return True

    # Otherwise require nginx-ish keywords in the message portion
    msg = (m.group("msg") or "").lower()
    nginx_like = ("upstream", "request:", "server:", "host:", " while ")
    return any(t in msg for t in nginx_like)

def classify(msg: str):
    m = (msg or "").lower()

    # severity
    sev = "INFO"
    for s, keys in KEYWORDS.items():
        if any(k in m for k in keys):
            sev = s if s in ("CRITICAL", "WARN") else "ERROR"
            break

    # category
    cat = "UNCATEGORIZED"
    for c, keys in CATEGORIES.items():
        if any(k in m for k in keys):
            cat = c
            break

    return sev, cat

def parse(file_path: str):
    """Parse a whole Nginx error log file into normalized records."""
    recs = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = NGINX_ERR.match(line)
            if m:
                ts = m.group("ts")
                level = (m.group("level") or "INFO").upper()
                msg = m.group("msg").strip()
            else:
                ts, level, msg = "", "INFO", line.strip()

            sev, cat = classify(msg)
            level_map = {"CRITICAL": "CRITICAL", "WARN": "WARN", "ERROR": "ERROR"}
            level = level_map.get(sev, level)

            recs.append({
                "timestamp": ts,
                "level": level,
                "source": "nginx",
                "message": msg,
                "category": cat,
            })
    return recs
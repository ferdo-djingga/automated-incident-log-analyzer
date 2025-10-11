import re

# Apache error log example:
# 2025/06/01 12:00:01 [error] [client 192.168.1.10] File does not exist: /var/www/html/favicon.ico

APACHE_ERR = re.compile(
    r"^(?P<ts>\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})\s"     # timestamp
    r"\[(?P<level>error|crit|warn|notice)\]\s"             # [level]
    r"(?!\d+#\d+:\s\*\d+\s)"                               # not nginx 'PID#worker: *req' block
    r"(?:\[client\s[^\]]+\]\s)?"                           # optional [client ...]
    r"(?P<msg>.+)$",                                       # message
    re.IGNORECASE
)

KEYWORDS = {
    "CRITICAL": ["fatal", "panic"],
    "ERROR": ["error", "exception", "timeout", "500", "502", "503", "connection refused", "failed", "bad gateway"],
    "WARN": ["warn", "deprecated", "retry", "slow"],
}

CATEGORIES = {
    "HTTP_5xx": ["500", "502", "503", "504", "upstream", "bad gateway"],
    "TIMEOUT": ["timeout", "timed out"],
    "NETWORK": ["connection refused", "dns", "unreachable"],
    "AUTH": ["unauthorized", "forbidden", "invalid credentials", "auth_fail"],
    "DISK": ["no space left", "disk full", "io error"],
    "DB": ["database", "db", "query failed", "deadlock"],
}

def can_parse(line: str) -> bool:
    """Return True if a single line looks like an Apache error entry."""
    return bool(APACHE_ERR.match(line or ""))

def classify(msg: str):
    """Return (severity, category) inferred from the message text."""
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
    """Parse a whole Apache error log file into normalized records."""
    records = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = APACHE_ERR.match(line)
            if m:
                ts = m.group("ts")
                level = (m.group("level") or "INFO").upper()
                msg = m.group("msg").strip()
            else:
                ts, level, msg = "", "INFO", line.strip()

            sev, cat = classify(msg)
            # overwrite level if severity signals higher priority
            level_map = {"CRITICAL": "CRITICAL", "WARN": "WARN", "ERROR": "ERROR"}
            level = level_map.get(sev, level)

            records.append({
                "timestamp": ts,
                "level": level,
                "source": "apache",
                "message": msg,
                "category": cat,
            })
    return records
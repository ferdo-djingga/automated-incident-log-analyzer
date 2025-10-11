import re

# Syslog example:
# Jun  5 12:01:03 server1 kernel: [12345.678901] eth0: link is down

SYSLOG = re.compile(
    r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})\s+"  # timestamp (e.g., Jun  5 12:01:01)
    r"\S+\s+"                                                  # hostname
    r"\S+(?:\[\d+\])?:\s"                                      # program[pid]:
    r"(?P<msg>.+)$"                                            # message
)

KEYWORDS = {
    "CRITICAL": ["kernel panic", "oops", "fatal"],
    "ERROR": ["error", "exception", "refused", "failed", "timeout"],
    "WARN": ["warn", "deprecated", "link is down", "retry", "slow"],
}

CATEGORIES = {
    "NETWORK": ["link is down", "dns", "unreachable", "refused", "connection reset"],
    "TIMEOUT": ["timeout", "timed out"],
    "DISK": ["no space left", "disk full", "io error"],
    "DB": ["database", "db", "query failed", "deadlock"],
}

def can_parse(line: str) -> bool:
    """Return True if a single line looks like classic syslog."""
    return bool(SYSLOG.match(line or ""))

def classify(msg: str):
    m = (msg or "").lower()

    sev = "INFO"
    for s, keys in KEYWORDS.items():
        if any(k in m for k in keys):
            sev = s if s in ("CRITICAL", "WARN") else "ERROR"
            break

    cat = "UNCATEGORIZED"
    for c, keys in CATEGORIES.items():
        if any(k in m for k in keys):
            cat = c
            break

    return sev, cat

def parse(file_path: str):
    """Parse a whole syslog file into normalized records."""
    recs = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = SYSLOG.match(line)
            if m:
                ts = m.group("ts")
                msg = m.group("msg").strip()
            else:
                ts, msg = "", line.strip()

            sev, cat = classify(msg)
            level_map = {"CRITICAL": "CRITICAL", "WARN": "WARN", "ERROR": "ERROR"}
            level = level_map.get(sev, "INFO")

            recs.append({
                "timestamp": ts,
                "level": level,
                "source": "syslog",
                "message": msg,
                "category": cat,
            })
    return recs
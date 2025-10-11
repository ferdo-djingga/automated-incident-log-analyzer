import json

def can_parse(line: str) -> bool:
    """
    Return True if the line looks like JSON (JSON Lines format).
    We try a quick json.loads on a non-empty line.
    """
    line = (line or "").strip()
    if not line:
        return False
    try:
        obj = json.loads(line)
        return isinstance(obj, dict)
    except Exception:
        return False

def classify(msg: str):
    m = (msg or "").lower()
    if "fatal" in m or "panic" in m:
        return "CRITICAL", "DEFAULT"
    if "error" in m or "exception" in m or "500" in m:
        return "ERROR", "HTTP_5xx" if "500" in m else "DEFAULT"
    if "warn" in m or "deprecated" in m:
        return "WARN", "DEFAULT"
    return "INFO", "DEFAULT"

def parse(file_path: str):
    """Parse JSON Lines application logs into normalized records."""
    recs = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                obj = {"level": "INFO", "msg": line}

            level = (obj.get("level", "INFO") or "INFO").upper()
            msg = obj.get("msg", "")
            sev, cat = classify(msg)
            level_map = {"CRITICAL": "CRITICAL", "WARN": "WARN", "ERROR": "ERROR"}
            level = level_map.get(sev, level)

            recs.append({
                "timestamp": obj.get("ts", ""),
                "level": level,
                "source": "app",
                "message": msg,
                "category": cat,
            })
    return recs
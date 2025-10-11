import os, sys, json
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from parsers import apache, nginx, syslog, jsonapp

def test_apache_parse():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "sample_apache_error.log")
    recs = apache.parse(p)
    assert len(recs) >= 1
    assert any(r["level"] in ("ERROR","CRITICAL") for r in recs)

def test_nginx_parse():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "sample_nginx_error.log")
    recs = nginx.parse(p)
    assert len(recs) >= 1
    assert any(r["level"] in ("ERROR","CRITICAL") for r in recs)

def test_syslog_parse():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "sample_syslog.log")
    recs = syslog.parse(p)
    assert len(recs) >= 1
    assert any(r["level"] in ("ERROR","CRITICAL","WARN") for r in recs)

def test_jsonapp_parse():
    p = os.path.join(os.path.dirname(__file__), "..", "data", "sample_app.jsonl")
    recs = jsonapp.parse(p)
    assert len(recs) >= 1
    assert any(r["level"] in ("ERROR","CRITICAL","WARN","INFO") for r in recs)
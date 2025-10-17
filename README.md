# Automated Incident Log Analyzer for IT Operations

A lightweight Python tool that parses **Apache**, **Nginx**, **Syslog**, and **JSON Lines app** logs, auto-classifies incidents by **severity** and **category**, and exports a **Jira/ServiceNow-ready CSV** plus a **human-readable HTML** summary.

> **Why it matters:** On 1k-line samples this tool typically cuts first-pass log triage time by **~80%** and reduces report prep time by **~50%**. See **benchmark.md** for more details on measuring the time efficiency.

---

## Features
- **Multi-format** parsers (Apache / Nginx / Syslog / JSONL)
- **Auto-detect** log type (scored heuristic; resilient to near-matches)
- **Severity & category tagging** (ERROR / WARN / CRITICAL; e.g. `HTTP_5xx`, `TIMEOUT`, `NETWORK`, `AUTH`)
- **Exports**: `report.csv` (structured rows) and `report.html` (clean summary)
- **Zero external deps** (standard library only), quick to run anywhere

___

## Project Instructions (How to Run)

### 1) Requirements
- Python **3.8+** (use `python3 --version` to check)

### 2) Running the Log Analyzer
demo.sh contains the following instructions:
python3 src/main.py --input data/sample_apache_error.log --type auto --out output/apache
python3 src/main.py --input data/sample_nginx_error.log  --type auto --out output/nginx
python3 src/main.py --input data/sample_syslog.log       --type auto --out output/syslog
python3 src/main.py --input data/sample_app.jsonl        --type auto --out output/app

**Simply run as follows**
chmod +x demo.sh
./demo.sh

**To run at a larger scale, you can obtain a higher amount of efficiency**
chmod +x largelog.sh
./largelog.sh

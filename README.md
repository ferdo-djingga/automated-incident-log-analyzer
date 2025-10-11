# Automated Incident Log Analyzer for IT Operations

A lightweight Python tool that parses **Apache**, **Nginx**, **Syslog**, and **JSON Lines app** logs, auto-classifies incidents by **severity** and **category**, and exports a **Jira/ServiceNow-ready CSV** plus a **human-readable HTML** summary.

> **Why it matters:** On 1k-line samples this tool typically cuts first-pass log triage time by **~80%** and reduces report prep time by **~50%**. See **benchmark.md** for more details on measuring the time efficiency.

---

## ✨ Features
- **Multi-format** parsers (Apache / Nginx / Syslog / JSONL)
- **Auto-detect** log type (scored heuristic; resilient to near-matches)
- **Severity & category tagging** (ERROR / WARN / CRITICAL; e.g. `HTTP_5xx`, `TIMEOUT`, `NETWORK`, `AUTH`)
- **Exports**: `report.csv` (structured rows) and `report.html` (clean summary)
- **Zero external deps** (standard library only), quick to run anywhere

---
## Project Structure
Automated-Incident-Log-Analyzer-for-IT-Operations/
  ├─ src/                        # main source code
  │   ├─ main.py                 # CLI entry point (parse args, run analyzer)
  │   ├─ report.py               # report generator (CSV + HTML)
  │   └─ parsers/                # log parsers (modular)
  │       ├─ apache.py           # Apache error log parser
  │       ├─ nginx.py            # Nginx error log parser
  │       ├─ syslog.py           # Syslog parser
  │       └─ jsonapp.py          # JSON-based application log parser
  │
  ├─ data/                       # sample input logs
  │   ├─ sample_apache_error.log
  │   ├─ sample_nginx_error.log
  │   ├─ sample_syslog.log
  │   └─ sample_app.jsonl
  │
  ├─ output/                     # generated outputs (example runs)
  │   ├─ report.csv
  │   ├─ report.html
  │   └─ demo_console.txt        # example console run output
  │
  ├─ tests/                      # light validation tests
  │   └─ test_parsers.py
  │
  ├─ demo.sh
  ├─ largelog.sh
  ├─ README.md                   # overview + instructions
  ├─ benchmark.md                # guide for measuring time saved / accuracy

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
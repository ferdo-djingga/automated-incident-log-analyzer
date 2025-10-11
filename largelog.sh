#!/bin/bash
echo "=== Generating 1000-line logs for benchmarks ==="

# Apache
: > data/apache_1000.log
for i in {1..200}; do cat data/sample_apache_error.log >> data/apache_1000.log; done
wc -l data/apache_1000.log

# Nginx
: > data/nginx_1000.log
for i in {1..334}; do cat data/sample_nginx_error.log >> data/nginx_1000.log; done
wc -l data/nginx_1000.log

# Syslog
: > data/syslog_1000.log
for i in {1..250}; do cat data/sample_syslog.log >> data/syslog_1000.log; done
wc -l data/syslog_1000.log

# App JSON
: > data/app_1000.jsonl
for i in {1..250}; do cat data/sample_app.jsonl >> data/app_1000.jsonl; done
wc -l data/app_1000.jsonl

echo "=== Running analyzer on 1000-line logs ==="

python3 src/main.py --input data/apache_1000.log --type auto --out output/apache_1000
python3 src/main.py --input data/nginx_1000.log  --type auto --out output/nginx_1000
python3 src/main.py --input data/syslog_1000.log --type auto --out output/syslog_1000
python3 src/main.py --input data/app_1000.jsonl  --type auto --out output/app_1000

echo "=== Done. Reports saved in output/*_1000/ ==="
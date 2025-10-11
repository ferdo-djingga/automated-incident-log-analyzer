#!/bin/bash

echo "=== Running Apache log analysis ==="
python3 src/main.py --input data/sample_apache_error.log --type auto --out output
echo "Apache report generated in output/"

echo "=== Running Nginx log analysis ==="
python3 src/main.py --input data/sample_nginx_error.log --type auto --out output
echo "Nginx report generated in output/"

echo "=== Running Syslog analysis ==="
python3 src/main.py --input data/sample_syslog.log --type auto --out output
echo "Syslog report generated in output/"

echo "=== Running App JSON log analysis ==="
python3 src/main.py --input data/sample_app.jsonl --type auto --out output
echo "App JSON report generated in output/"

echo "=== All reports completed ==="
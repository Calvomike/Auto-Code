#!/bin/bash

export PATH=/usr/local/bin:/usr/bin:/bin

PROJECT_DIR="/home/calvomike/GitHub Repositories/Auto-Code/AutomaticScheduleDownloader"
cd "$PROJECT_DIR" || exit 1

LOG_FILE="$PROJECT_DIR/cron.log"

{
echo "-----------------------------"
echo "Inicio: $(date)"

/myenv/bin/python3 script.py

if [ $? -eq 0 ]; then
    git add .
    git commit -m "Auto commit $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nada para commitear"
    git push
    echo "Push realizado"
else
    echo "Error ejecutando script"
fi

echo "Fin: $(date)"
} >> "$LOG_FILE" 2>&1

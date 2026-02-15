#!/bin/bash

export PATH=/usr/local/bin:/usr/bin:/bin

PROJECT_DIR="/home/calvomike/github_repos/Auto-Code/AutomaticScheduleDownloader"
cd "$PROJECT_DIR" || exit 1

echo "-----------------------------"
echo "Inicio: $(date)"

# activar entorno virtual
source /home/calvomike/myenv/bin/activate

python3 pdf_horario_downloader.py

if [ $? -eq 0 ]; then
    git add .
    git commit -m "Auto commit $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nada para commitear"
    git push
    echo "Push realizado"
else
    echo "Error ejecutando script"
fi

echo "Fin: $(date)"


#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Ejecuta la simulación completa (caso de la evaluación + laboratorio de 50 tareas + Excel).
set -euo pipefail
cd "$(dirname "$0")"
python3 -c "import matplotlib, openpyxl" 2>/dev/null || pip3 install -q --user -r requirements.txt
mkdir -p resultados
python3 -m scheduler.caso
python3 -m scheduler.laboratorio
python3 -m scheduler.excel

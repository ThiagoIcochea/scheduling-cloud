#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Compila y ejecuta el laboratorio en CloudSim Plus (Java 17+ y Maven; disponibles en Cloud Shell).
set -euo pipefail
cd "$(dirname "$0")"
[ -f ../resultados/dataset_50_tareas.csv ] || (cd .. && python3 -m scheduler.laboratorio >/dev/null)
mvn -q compile exec:java

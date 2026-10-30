#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Recorre las partes de la práctica con una pausa entre cada una (para tomar capturas). Uso: bash capturas.sh [pausa_s] [desde]
P=${1:-40}; D=${2:-1}
cd "$(dirname "$0")"
(cd cloudsim && mvn -q -DskipTests dependency:resolve compile >/tmp/mvn.log 2>&1 &)
for i in $(seq "$D" 6); do bash ver.sh "$i"; echo; echo "[parte $i de 6 · $(date '+%d/%m/%Y %H:%M') · $(gcloud config get-value account 2>/dev/null)]"; sleep "$P"; done

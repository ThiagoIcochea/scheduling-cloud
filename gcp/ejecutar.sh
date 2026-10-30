#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Ejecuta el caso en Google Cloud: cada estrategia es un Cloud Run Job con 3 tareas en paralelo
# (VM1, VM2, VM3), cada una con 4 vCPU y 8 GB, como en el enunciado. 1 minuto = ESCALA segundos.
#   bash gcp/ejecutar.sh                 # rr, sjf y propuesta
#   ESTRATEGIAS="rr fcfs sjf lpt optimo" ESCALA=3 bash gcp/ejecutar.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
ESCALA="${ESCALA:-3}"
ESTRATEGIAS="${ESTRATEGIAS:-rr sjf propuesta}"
[[ -z "${PROJECT_ID}" ]] && { echo "Configura el proyecto: gcloud config set project <ID>"; exit 1; }
gcloud services enable run.googleapis.com logging.googleapis.com --project "${PROJECT_ID}" >/dev/null
CODE=$(base64 -w0 gcp/worker.py)
for e in ${ESTRATEGIAS}; do
  PLAN=$(python3 -m scheduler.plan "$e")
  echo "== Estrategia ${e}: ${PLAN}"
  JOB="sched-${e}"
  gcloud run jobs deploy "${JOB}" --project "${PROJECT_ID}" --region "${REGION}" \
    --image=python:3.12-slim --tasks=3 --parallelism=3 --cpu=4 --memory=8Gi --max-retries=0 --task-timeout=15m \
    --command=sh --args="-c,echo \$CODE_B64 | base64 -d > /w.py && python3 /w.py" \
    --set-env-vars="CODE_B64=${CODE},PLAN_B64=$(echo -n "${PLAN}" | base64 -w0),ESCALA=${ESCALA},ESTRATEGIA=${e}" \
    --labels=curso=servicios-cloud-45104,autor=thiago-icochea --quiet
  gcloud run jobs execute "${JOB}" --project "${PROJECT_ID}" --region "${REGION}" --wait
done
echo "Recolectando resultados de Cloud Logging (puede tardar ~30 s en aparecer)…"
sleep 30
# shellcheck disable=SC2086
python3 gcp/resultados_gcp.py "${PROJECT_ID}" "${ESCALA}" ${ESTRATEGIAS}

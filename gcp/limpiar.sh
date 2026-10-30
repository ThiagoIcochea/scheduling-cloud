#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Elimina los Cloud Run Jobs creados (no generan costo si no se ejecutan, pero se dejan limpios).
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"; REGION="${REGION:-us-central1}"
for j in $(gcloud run jobs list --project "$PROJECT_ID" --region "$REGION" --format="value(metadata.name)" | grep '^sched-'); do
  gcloud run jobs delete "$j" --project "$PROJECT_ID" --region "$REGION" --quiet
done

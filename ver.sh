#!/usr/bin/env bash
# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Muestra por partes la salida de la práctica (para las capturas del informe). Uso: bash ver.sh 1..6
cd "$(dirname "$0")"
[ -f /tmp/caso.txt ] || python3 -m scheduler.caso > /tmp/caso.txt
bloque() { awk -v t="$1" -v n="${2:-1}" 'index($0,"=== " t)==1{f++} f==n && !/^$/{print} f==n && /^$/{exit}' /tmp/caso.txt; echo; }
clear
case "${1:-1}" in
 1) echo "### Datos del caso y ACTIVIDAD 1: Round Robin"; head -4 /tmp/caso.txt; echo; bloque "Round Robin" ;;
 2) echo "### ACTIVIDAD 2: SJF (VM que queda libre primero)"; sed -n 4p /tmp/caso.txt; echo; bloque "SJF"; bloque "FCFS" ;;
 3) echo "### ACTIVIDAD 3: Propuesta de optimización vs óptimo"; sed -n 3p /tmp/caso.txt; echo; bloque "Propuesta"; bloque "Óptima" ;;
 7) echo "### ACTIVIDAD 3 (complemento): asignación basada en carga (LPT)"; bloque "Basada en carga" ;;
 4) echo "### PREGUNTA 3: VM heterogéneas (VM1 8 vCPU = 2x, VM2/VM3 2 vCPU = 0,5x)"; bloque "Round Robin" 2; bloque "Basada en carga" 2; grep "Cota inferior hetero" /tmp/caso.txt ;;
 5) echo "### LABORATORIO (Python): 50 tareas, 5 VM heterogéneas, FCFS vs Min-Min"; python3 -m scheduler.laboratorio ;;
 6) echo "### LABORATORIO (CloudSim Plus, Java): 50 cloudlets, 5 VM, FCFS vs Min-Min"; bash cloudsim/ejecutar.sh ;;
esac

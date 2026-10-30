# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
"""Imprime en JSON el plan de una estrategia (vm -> [[job, duración], ...]) para ejecutarlo en GCP.
Uso: python3 -m scheduler.plan rr|fcfs|sjf|lpt|optimo|propuesta"""
import json, sys
from . import algoritmos as A
from .caso import JOBS, VMS, PROPUESTA

FN = {"rr": A.round_robin, "fcfs": A.fcfs, "sjf": A.sjf, "lpt": A.lpt, "optimo": A.optimo}
a = A.desde_plan("Propuesta", JOBS, PROPUESTA) if sys.argv[1] == "propuesta" else FN[sys.argv[1]](JOBS, VMS)
print(json.dumps({vm: [[j, JOBS[j]] for j, _, _ in a.plan[vm]] for vm in VMS}))

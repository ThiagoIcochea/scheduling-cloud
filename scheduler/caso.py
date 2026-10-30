# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
"""Caso de la evaluación: 8 trabajos sobre 3 VM homogéneas (4 vCPU, 8 GB).
Uso: python3 -m scheduler.caso   → imprime tablas y genera resultados/ (JSON, PNG)."""
import json, math, os
from . import algoritmos as A
from .graficos import gantt, barras

JOBS = {"J1": 12, "J2": 4, "J3": 8, "J4": 3, "J5": 10, "J6": 6, "J7": 2, "J8": 7}
VMS = ["VM1", "VM2", "VM3"]
# Actividad 3: propuesta equilibrada (largos primero en VM distintas y se completa cada VM hasta ~17-18 min).
PROPUESTA = {"VM1": ["J1", "J6"], "VM2": ["J5", "J4", "J2"], "VM3": ["J3", "J8", "J7"]}
OUT = os.environ.get("OUT", "resultados")


def tabla(a, jobs=JOBS):
    print(f"\n=== {a.nombre} ===")
    print(f"{'VM':<5}{'Trabajos (inicio→fin)':<52}{'Carga':>7}")
    for vm in a.vms:
        t = ", ".join(f"{j}({i:g}→{f:g})" for j, i, f in a.plan[vm])
        print(f"{vm:<5}{t:<52}{a.cargas[vm]:>7g}")
    m = a.metricas(sum(jobs.values()))
    print("Cmax = max(" + ", ".join(f"{a.cargas[v]:g}" for v in a.vms) + f") = {m['makespan']:g} min")
    print("Métricas:", m)
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    total = sum(JOBS.values())
    print(f"Trabajos: {JOBS}\nTiempo total = {' + '.join(map(str, JOBS.values()))} = {total} min")
    print(f"Carga media teórica = {total}/3 = {total/3:.2f} min → cota inferior entera ⌈52/3⌉ = {math.ceil(total/3)} min")
    print("Orden SJF:", " → ".join(f"{j}({JOBS[j]})" for j in sorted(JOBS, key=lambda j: (JOBS[j], j))))

    res = {}
    for fn in (A.round_robin, A.fcfs, A.sjf, A.lpt, A.optimo):
        a = fn(JOBS, VMS)
        res[a.nombre] = {"plan": a.plan, "cargas": a.cargas, "metricas": tabla(a)}
        gantt(a, f"{OUT}/gantt_{fn.__name__}.png", cota=total / 3)
    p = A.desde_plan("Propuesta equilibrada", JOBS, PROPUESTA)
    res[p.nombre] = {"plan": p.plan, "cargas": p.cargas, "metricas": tabla(p)}
    gantt(p, f"{OUT}/gantt_propuesta.png", cota=total / 3)
    barras(res, f"{OUT}/comparacion_metricas.png")

    # Pregunta 3: VM heterogéneas (VM1 8 vCPU = 2x, VM2/VM3 2 vCPU = 0,5x respecto a 4 vCPU).
    vel = {"VM1": 2.0, "VM2": 0.5, "VM3": 0.5}
    print("\n##### Escenario heterogéneo (VM1 = 8 vCPU, VM2 = VM3 = 2 vCPU) #####")
    het = {}
    for fn in (A.round_robin, A.lpt, A.optimo):
        a = fn(JOBS, VMS, vel)
        het[a.nombre] = {"plan": a.plan, "cargas": a.cargas, "metricas": tabla(a)}
        gantt(a, f"{OUT}/gantt_hetero_{fn.__name__}.png", titulo_extra=" · VM1 8 vCPU, VM2/VM3 2 vCPU")
    capacidad = sum(vel.values())
    print(f"Cota inferior heterogénea = 52 / (2 + 0,5 + 0,5) = {total/capacidad:.2f} min")

    json.dump({"jobs": JOBS, "total": total, "homogeneo": res, "heterogeneo": het},
              open(f"{OUT}/resultados_caso.json", "w"), ensure_ascii=False, indent=1)
    print(f"\nArchivos generados en {OUT}/")


if __name__ == "__main__":
    main()

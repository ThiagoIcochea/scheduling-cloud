# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
"""Práctica de laboratorio: 50 tareas de distinto tamaño sobre 5 VM heterogéneas.
Compara FCFS vs Min-Min (y Max-Min como referencia) midiendo makespan, espera y utilización.
Uso: python3 -m scheduler.laboratorio [semilla]"""
import csv, json, os, random, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from . import algoritmos as A
from .graficos import COLORES

OUT = os.environ.get("OUT", "resultados")
SEMILLA = int(sys.argv[1]) if len(sys.argv) > 1 else 45104
VMS = ["VM1", "VM2", "VM3", "VM4", "VM5"]
MIPS = {"VM1": 500, "VM2": 750, "VM3": 1000, "VM4": 1500, "VM5": 2000}   # capacidad (millones de instrucciones/s)


def dataset(n=50, semilla=SEMILLA):
    rnd = random.Random(semilla)
    # 70 % tareas pequeñas, 20 % medianas, 10 % grandes (longitud en MI)
    t = {}
    for i in range(1, n + 1):
        r = rnd.random()
        mi = rnd.randint(1_000, 10_000) if r < 0.7 else rnd.randint(10_000, 40_000) if r < 0.9 else rnd.randint(40_000, 100_000)
        t[f"T{i:02d}"] = mi
    return t


def resumen(a, tareas):
    cargas = {vm: (a.plan[vm][-1][2] if a.plan[vm] else 0) for vm in VMS}
    cmax = max(cargas.values())
    inicios = [i for vm in VMS for _, i, _ in a.plan[vm]]
    fines = [f for vm in VMS for _, _, f in a.plan[vm]]
    return {"makespan_s": round(cmax, 2), "espera_media_s": round(sum(inicios) / len(inicios), 2),
            "respuesta_media_s": round(sum(fines) / len(fines), 2),
            "utilizacion_pct": round(sum(cargas.values()) / (cmax * len(VMS)) * 100, 1),
            "tareas_por_vm": {vm: len(a.plan[vm]) for vm in VMS},
            "ocupacion_s": {vm: round(cargas[vm], 2) for vm in VMS}}


def main():
    os.makedirs(OUT, exist_ok=True)
    tareas = dataset()
    with open(f"{OUT}/dataset_50_tareas.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["tarea", "longitud_MI"]); w.writerows(tareas.items())
    print(f"Dataset: 50 tareas (semilla {SEMILLA}), total {sum(tareas.values()):,} MI · VM (MIPS): {MIPS}")
    res = {}
    for fn in (A.fcfs_hetero, A.min_min, A.max_min):
        a = fn(tareas, VMS, MIPS)
        r = resumen(a, tareas); res[a.nombre] = r
        print(f"\n{a.nombre:8} makespan={r['makespan_s']:>7} s  espera media={r['espera_media_s']:>7} s  "
              f"utilización={r['utilizacion_pct']:>5} %  tareas/VM={r['tareas_por_vm']}")
        fig, ax = plt.subplots(figsize=(10, 2.8))
        for y, vm in enumerate(VMS):
            for k, (t, i, fin) in enumerate(a.plan[vm]):
                ax.barh(y, fin - i, left=i, color=COLORES[k % len(COLORES)], edgecolor="white", height=0.6)
        ax.axvline(r["makespan_s"], color="black", ls="--", lw=1)
        ax.set_yticks(range(len(VMS)), [f"{v} ({MIPS[v]} MIPS)" for v in VMS]); ax.invert_yaxis()
        ax.set_xlabel("Tiempo (s)"); ax.set_title(f"{a.nombre} · makespan {r['makespan_s']} s", loc="left", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False); fig.tight_layout()
        fig.savefig(f"{OUT}/lab_gantt_{fn.__name__}.png", dpi=150); plt.close(fig)
    nombres = list(res)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, (k, t) in zip(axs, [("makespan_s", "Makespan (s)"), ("espera_media_s", "Espera media (s)"), ("utilizacion_pct", "Utilización de CPU (%)")]):
        b = ax.bar(nombres, [res[n][k] for n in nombres], color=COLORES[:3]); ax.bar_label(b, fmt="%g", fontsize=8)
        ax.set_title(t, fontsize=10); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(f"{OUT}/lab_comparacion.png", dpi=150); plt.close(fig)
    json.dump({"semilla": SEMILLA, "mips": MIPS, "resultados": res}, open(f"{OUT}/resultados_laboratorio.json", "w"), ensure_ascii=False, indent=1)
    f, m = res["FCFS"], res["Min-Min"]
    dm = (m["makespan_s"] / f["makespan_s"] - 1) * 100
    de = (m["espera_media_s"] / f["espera_media_s"] - 1) * 100
    print(f"\nMin-Min frente a FCFS: makespan {dm:+.1f} %, espera media {de:+.1f} %.")


if __name__ == "__main__":
    main()

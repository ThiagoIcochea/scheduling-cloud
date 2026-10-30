# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
"""Lee de Cloud Logging los tiempos medidos en Cloud Run y calcula el makespan real de cada estrategia."""
import json, subprocess, sys
proyecto, escala, estrategias = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
filtro = 'resource.type="cloud_run_job" AND jsonPayload.evento="vm_fin"'
salida = subprocess.run(["gcloud", "logging", "read", filtro, "--project", proyecto, "--freshness=2d",
                         "--format=json", "--limit=200"], capture_output=True, text=True, check=True).stdout
ultimos = {}
for e in json.loads(salida or "[]"):
    p = e.get("jsonPayload", {})
    clave = (p.get("estrategia"), p.get("vm"))
    if clave not in ultimos or e["timestamp"] > ultimos[clave][0]:
        ultimos[clave] = (e["timestamp"], p)
print(f"\n{'Estrategia':<10}{'VM1 (min)':>11}{'VM2 (min)':>11}{'VM3 (min)':>11}{'Cmax medido':>13}   vCPU")
res = {}
for est in estrategias:
    cargas = {vm: ultimos[(est, vm)][1]["carga_s"] / escala for vm in ("VM1", "VM2", "VM3") if (est, vm) in ultimos}
    cpu = {ultimos[(est, vm)][1].get("cpu") for vm in cargas}
    if not cargas:
        print(f"{est:<10} sin datos todavía"); continue
    res[est] = cargas
    print(f"{est:<10}" + "".join(f"{cargas.get(v, 0):>11.2f}" for v in ("VM1", "VM2", "VM3"))
          + f"{max(cargas.values()):>13.2f}   {','.join(map(str, cpu))}")
json.dump(res, open("resultados/resultados_gcp.json", "w"), indent=1)

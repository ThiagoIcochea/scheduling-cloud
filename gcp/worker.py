# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
# Se ejecuta en cada tarea de Cloud Run Jobs. La tarea N hace de VM(N+1) y procesa en orden
# los trabajos que el scheduler le asignó, ocupando CPU durante duración × ESCALA segundos.
import base64, json, os, time
vm = int(os.environ.get("CLOUD_RUN_TASK_INDEX", "0"))
plan = json.loads(base64.b64decode(os.environ["PLAN_B64"]))
escala = float(os.environ.get("ESCALA", "3"))      # segundos reales por minuto simulado
estrategia = os.environ.get("ESTRATEGIA", "")
nombre = f"VM{vm + 1}"
t0 = float(os.environ.get("T0", time.time()))
inicio_vm = time.time()
for job, dur in plan.get(nombre, []):
    ini = time.time()
    fin_objetivo = ini + dur * escala
    x = 0
    while time.time() < fin_objetivo:          # carga real de CPU (no solo sleep)
        x = (x * 1103515245 + 12345) % 2147483648
    fin = time.time()
    print(json.dumps({"evento": "job", "estrategia": estrategia, "vm": nombre, "job": job, "duracion_min": dur,
                      "inicio_s": round(ini - inicio_vm, 2), "fin_s": round(fin - inicio_vm, 2)}), flush=True)
print(json.dumps({"evento": "vm_fin", "estrategia": estrategia, "vm": nombre,
                  "carga_s": round(time.time() - inicio_vm, 2), "cpu": os.cpu_count()}), flush=True)

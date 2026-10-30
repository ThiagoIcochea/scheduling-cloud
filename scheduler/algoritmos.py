# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
"""Algoritmos de scheduling para asignar trabajos (jobs) a máquinas virtuales.

Supuestos de la guía: todos los trabajos llegan en t=0, cada VM ejecuta un trabajo a la vez,
no hay costo de cambio de contexto ni interrupciones (no expropiativo).
Una VM con capacidad (velocidad) s ejecuta un trabajo de duración d en d / s minutos.
"""
from dataclasses import dataclass, field
from itertools import product


@dataclass
class Asignacion:
    nombre: str
    vms: list                       # nombres de VM
    plan: dict = field(default_factory=dict)   # vm -> [(job, inicio, fin)]

    @property
    def cargas(self):
        return {vm: (self.plan[vm][-1][2] if self.plan[vm] else 0.0) for vm in self.vms}

    @property
    def makespan(self):
        return max(self.cargas.values())

    def metricas(self, total_trabajo):
        fines = [f for vm in self.vms for (_, _, f) in self.plan[vm]]
        inicios = [i for vm in self.vms for (_, i, _) in self.plan[vm]]
        n, cmax = len(fines), self.makespan
        cargas = list(self.cargas.values())
        media = sum(cargas) / len(cargas)
        return {
            "makespan": round(cmax, 2),
            "espera_media": round(sum(inicios) / n, 2),            # llegada en t=0 → espera = inicio
            "respuesta_media": round(sum(fines) / n, 2),           # tiempo de finalización medio
            "throughput_jobs_h": round(n / cmax * 60, 2),
            "utilizacion_pct": round(sum(cargas) / (cmax * len(cargas)) * 100, 1),
            "desbalance": round(max(cargas) - min(cargas), 2),
            "desv_carga": round((sum((c - media) ** 2 for c in cargas) / len(cargas)) ** 0.5, 2),
        }


def _vacio(nombre, vms):
    return Asignacion(nombre, list(vms), {vm: [] for vm in vms})


def _agregar(a, vm, job, dur, vel):
    ini = a.plan[vm][-1][2] if a.plan[vm] else 0.0
    a.plan[vm].append((job, ini, ini + dur / vel))


def round_robin(jobs, vms, velocidad=None):
    """Asigna J1→VM1, J2→VM2, J3→VM3, J4→VM1… sin mirar duración ni carga."""
    velocidad = velocidad or {vm: 1 for vm in vms}
    a = _vacio("Round Robin", vms)
    for k, (job, dur) in enumerate(jobs.items()):
        vm = vms[k % len(vms)]
        _agregar(a, vm, job, dur, velocidad[vm])
    return a


def _lista(nombre, orden, jobs, vms, velocidad, por_fin=False):
    """List scheduling: cada trabajo, en el orden dado, va a la VM que queda libre primero
    (o, si por_fin=True, a la VM donde terminaría antes: considera la capacidad)."""
    velocidad = velocidad or {vm: 1 for vm in vms}
    a = _vacio(nombre, vms)
    for job in orden:
        libre = {vm: (a.plan[vm][-1][2] if a.plan[vm] else 0.0) for vm in vms}
        if por_fin:
            vm = min(vms, key=lambda v: (libre[v] + jobs[job] / velocidad[v], vms.index(v)))
        else:
            vm = min(vms, key=lambda v: (libre[v], vms.index(v)))
        _agregar(a, vm, job, jobs[job], velocidad[vm])
    return a


def fcfs(jobs, vms, velocidad=None):
    """FCFS/FIFO: orden de llegada; cada trabajo va a la primera VM que queda libre."""
    return _lista("FCFS", list(jobs), jobs, vms, velocidad)


def sjf(jobs, vms, velocidad=None):
    """SJF: orden de menor a mayor duración; cada trabajo va a la primera VM que queda libre."""
    orden = sorted(jobs, key=lambda j: (jobs[j], j))
    return _lista("SJF", orden, jobs, vms, velocidad)


def lpt(jobs, vms, velocidad=None):
    """Asignación basada en carga (LPT): el trabajo más largo primero, a la VM donde terminaría antes."""
    orden = sorted(jobs, key=lambda j: (-jobs[j], j))
    return _lista("Basada en carga (LPT)", orden, jobs, vms, velocidad, por_fin=True)


def optimo(jobs, vms, velocidad=None):
    """Búsqueda exhaustiva (3^8 = 6561 combinaciones): mínimo makespan; desempate por menor desbalance.
    Dentro de cada VM los trabajos se ordenan de menor a mayor (reduce la espera media)."""
    velocidad = velocidad or {vm: 1 for vm in vms}
    nombres = list(jobs)
    mejor, clave_mejor = None, None
    for combo in product(range(len(vms)), repeat=len(nombres)):
        cargas = [0.0] * len(vms)
        for j, v in zip(nombres, combo):
            cargas[v] += jobs[j] / velocidad[vms[v]]
        clave = (round(max(cargas), 6), round(max(cargas) - min(cargas), 6))
        if clave_mejor is None or clave < clave_mejor:
            mejor, clave_mejor = combo, clave
    a = _vacio("Óptima (equilibrio de carga)", vms)
    grupos = {vm: [] for vm in vms}
    for j, v in zip(nombres, mejor):
        grupos[vms[v]].append(j)
    for vm in vms:
        for j in sorted(grupos[vm], key=lambda x: (jobs[x], x)):
            _agregar(a, vm, j, jobs[j], velocidad[vm])
    return a


def min_min(tareas, vms, mips):
    """Min-Min (laboratorio): en cada paso elige la tarea cuyo tiempo mínimo de finalización es el
    menor de todos y la asigna a la VM que la termina antes. tareas: {id: longitud en MI}."""
    a = _vacio("Min-Min", vms)
    libre = {vm: 0.0 for vm in vms}
    pendientes = dict(tareas)
    while pendientes:
        mejor = None
        for t, mi in pendientes.items():
            for vm in vms:
                fin = libre[vm] + mi / mips[vm]
                if mejor is None or fin < mejor[0]:
                    mejor = (fin, t, vm)
        fin, t, vm = mejor
        a.plan[vm].append((t, libre[vm], fin))
        libre[vm] = fin
        del pendientes[t]
    return a


def fcfs_hetero(tareas, vms, mips):
    """FCFS del laboratorio: orden de llegada, a la VM que queda libre primero (sin mirar su velocidad)."""
    a = _vacio("FCFS", vms)
    libre = {vm: 0.0 for vm in vms}
    for t, mi in tareas.items():
        vm = min(vms, key=lambda v: (libre[v], vms.index(v)))
        fin = libre[vm] + mi / mips[vm]
        a.plan[vm].append((t, libre[vm], fin))
        libre[vm] = fin
    return a


def max_min(tareas, vms, mips):
    """Max-Min: como Min-Min, pero en cada paso asigna primero la tarea cuyo tiempo mínimo de finalización es el mayor."""
    a = _vacio("Max-Min", vms)
    libre = {vm: 0.0 for vm in vms}
    pendientes = dict(tareas)
    while pendientes:
        mejores = {}
        for t, mi in pendientes.items():
            vm = min(vms, key=lambda v: libre[v] + mi / mips[v])
            mejores[t] = (libre[vm] + mi / mips[vm], vm)
        t = max(mejores, key=lambda x: mejores[x][0])
        fin, vm = mejores[t]
        a.plan[vm].append((t, libre[vm], fin))
        libre[vm] = fin
        del pendientes[t]
    return a


def desde_plan(nombre, jobs, plan, velocidad=None):
    """Construye una asignación manual {vm: [jobs en orden]}."""
    vms = list(plan); velocidad = velocidad or {vm: 1 for vm in vms}
    a = _vacio(nombre, vms)
    for vm, js in plan.items():
        for j in js:
            _agregar(a, vm, j, jobs[j], velocidad[vm])
    return a

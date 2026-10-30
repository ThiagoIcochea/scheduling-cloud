# Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORES = ["#B50D30", "#2BA6B5", "#F7931E", "#8CC63F", "#3B3561", "#E6007E", "#FFC20E", "#6D6884"]


def gantt(a, ruta, cota=None, titulo_extra="", etiquetas=True):
    fig, ax = plt.subplots(figsize=(9, 0.6 + 0.65 * len(a.vms)))
    for y, vm in enumerate(a.vms):
        for k, (job, ini, fin) in enumerate(a.plan[vm]):
            idx = int(job[1:]) if job[1:].isdigit() else k
            ax.barh(y, fin - ini, left=ini, color=COLORES[(idx - 1) % len(COLORES)], edgecolor="white", height=0.6)
            if etiquetas and fin - ini >= 1:
                ax.text((ini + fin) / 2, y, job, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(a.cargas[vm] + 0.2, y, f"{a.cargas[vm]:g}", va="center", fontsize=9)
    ax.axvline(a.makespan, color="#1F1B1C", ls="--", lw=1)
    ax.text(a.makespan, len(a.vms) - 0.45, f" Cmax = {a.makespan:g}", fontsize=9)
    if cota:
        ax.axvline(cota, color="#2BA6B5", ls=":", lw=1)
    ax.set_yticks(range(len(a.vms)), a.vms)
    ax.invert_yaxis()
    ax.set_xlabel("Tiempo (min)")
    ax.set_title(f"{a.nombre}{titulo_extra}", fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ruta, dpi=160)
    plt.close(fig)


def barras(res, ruta):
    nombres = list(res)
    cortos = [n.replace(" (equilibrio de carga)", "").replace("Basada en carga (LPT)", "LPT (carga)") for n in nombres]
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, (clave, titulo) in zip(axs, [("makespan", "Makespan (min)"), ("espera_media", "Espera media (min)"),
                                         ("desbalance", "Desbalance de carga (min)")]):
        vals = [res[n]["metricas"][clave] for n in nombres]
        barras_ = ax.bar(cortos, vals, color=COLORES[:len(nombres)])
        ax.bar_label(barras_, fmt="%g", fontsize=8)
        ax.set_title(titulo, fontsize=10)
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ruta, dpi=160)
    plt.close(fig)

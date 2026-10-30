# Scheduling y asignación eficiente de recursos en la nube

**Autor:** Thiago Paolo Icochea Rodriguez · **Código:** U22330428
**Curso:** Servicios Cloud · **Sección:** 45104 · **Docente:** Eleodoro Orbegoso Carrera · Universidad Tecnológica del Perú

Evaluación práctica individual (semana 12): comparar estrategias de scheduling para asignar trabajos a máquinas
virtuales y justificar cuál aprovecha mejor los recursos cloud.

## Contenido

| Ruta | Descripción |
|---|---|
| `scheduler/algoritmos.py` | Round Robin, FCFS, SJF, asignación basada en carga (LPT), búsqueda óptima, Min-Min y Max-Min |
| `scheduler/caso.py` | Caso de la evaluación: 8 trabajos en 3 VM de 4 vCPU/8 GB (y escenario heterogéneo de la pregunta 3) |
| `scheduler/laboratorio.py` | Guía de laboratorio: 50 tareas en 5 VM heterogéneas, FCFS vs Min-Min (y Max-Min) |
| `cloudsim/` | Mismo laboratorio en **CloudSim Plus (Java)**: 50 cloudlets, 5 VM (500–2000 MIPS), FCFS vs Min-Min (`bash cloudsim/ejecutar.sh`) |
| `ver.sh` | Muestra la salida por partes para las capturas (`bash ver.sh 1` … `6`) |
| `scheduler/excel.py` | Hoja de cálculo con fórmulas (cargas, makespan, cota inferior) |
| `gcp/ejecutar.sh` | Ejecución real en Google Cloud: cada estrategia es un Cloud Run Job con 3 tareas paralelas de 4 vCPU/8 GB |
| `resultados/` | Tablas (JSON/CSV), diagramas de Gantt, comparaciones y Excel generados |

## Uso

```bash
git clone https://github.com/ThiagoIcochea/scheduling-cloud.git && cd scheduling-cloud
bash ejecutar_todo.sh                      # simulación local o en Cloud Shell

gcloud config set project <PROJECT_ID>
bash gcp/ejecutar.sh                       # rr, sjf y propuesta en Cloud Run (1 min = 3 s)
bash gcp/limpiar.sh                        # elimina los jobs
```

## Resultados del caso (8 trabajos, 52 min en total, cota inferior ⌈52/3⌉ = 18 min)

| Estrategia | VM1 | VM2 | VM3 | Makespan | Espera media | Utilización |
|---|---|---|---|---|---|---|
| Round Robin | 17 | 21 | 14 | **21** | 6,62 | 82,5 % |
| FCFS | 21 | 17 | 14 | **21** | 5,62 | 82,5 % |
| SJF (VM libre primero) | 18 | 22 | 12 | **22** | 3,38 | 78,8 % |
| Basada en carga (LPT) | 18 | 16 | 18 | **18** | 7,62 | 96,3 % |
| Propuesta equilibrada | 18 | 17 | 17 | **18** | 7,25 | 96,3 % |

La asignación basada en carga alcanza la cota inferior (18 min), por lo que es óptima en makespan.

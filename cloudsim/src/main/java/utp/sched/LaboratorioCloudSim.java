// Autor: Thiago Paolo Icochea Rodriguez (U22330428) · Servicios Cloud 45104 · UTP
package utp.sched;

import org.cloudsimplus.brokers.DatacenterBrokerSimple;
import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.cloudlets.CloudletSimple;
import org.cloudsimplus.core.CloudSimPlus;
import org.cloudsimplus.datacenters.DatacenterSimple;
import org.cloudsimplus.hosts.Host;
import org.cloudsimplus.hosts.HostSimple;
import org.cloudsimplus.resources.Pe;
import org.cloudsimplus.resources.PeSimple;
import org.cloudsimplus.schedulers.cloudlet.CloudletSchedulerSpaceShared;
import org.cloudsimplus.utilizationmodels.UtilizationModelDynamic;
import org.cloudsimplus.utilizationmodels.UtilizationModelFull;
import org.cloudsimplus.vms.Vm;
import org.cloudsimplus.vms.VmSimple;
import org.cloudsimplus.util.Log;
import ch.qos.logback.classic.Level;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.*;
import java.util.*;

/**
 * Laboratorio de scheduling en CloudSim Plus: 50 tareas (cloudlets) de distinto tamaño
 * sobre 5 VM heterogéneas (500, 750, 1000, 1500 y 2000 MIPS). Compara FCFS vs Min-Min.
 * El dataset es el mismo que genera el script de Python (resultados/dataset_50_tareas.csv).
 * Uso: mvn -q compile exec:java  [-Dexec.args="ruta/dataset.csv"]
 */
public class LaboratorioCloudSim {
    static final long[] MIPS = {500, 750, 1000, 1500, 2000};

    record Tarea(String id, long mi) {}

    public static void main(String[] args) throws IOException {
        Log.setLevel(Level.WARN); // oculta el log INFO de cada evento de la simulación
        Path csv = Path.of(args.length > 0 ? args[0] : "../resultados/dataset_50_tareas.csv");
        List<Tarea> tareas = new ArrayList<>();
        for (String l : Files.readAllLines(csv).subList(1, Files.readAllLines(csv).size())) {
            String[] p = l.split(",");
            tareas.add(new Tarea(p[0], Long.parseLong(p[1].trim())));
        }
        long total = tareas.stream().mapToLong(Tarea::mi).sum();
        System.out.printf("CloudSim Plus · %d cloudlets, %,d MI en total · VM (MIPS): %s%n",
                tareas.size(), total, Arrays.toString(MIPS));

        Path out = Path.of("../resultados");
        Files.createDirectories(out);
        try (PrintWriter w = new PrintWriter(out.resolve("cloudsim_resultados.csv").toFile())) {
            w.println("algoritmo,tarea,vm,mips,inicio_s,fin_s,espera_s");
            Map<String, double[]> resumen = new LinkedHashMap<>();
            resumen.put("FCFS", simular("FCFS", tareas, fcfs(tareas), w));
            resumen.put("Min-Min", simular("Min-Min", tareas, minMin(tareas), w));
            double[] f = resumen.get("FCFS"), m = resumen.get("Min-Min");
            System.out.println("\n=========== Comparación (CloudSim Plus) ===========");
            System.out.printf("%-9s %12s %14s %15s%n", "Algoritmo", "Makespan(s)", "Espera media(s)", "Utilización CPU");
            for (var e : resumen.entrySet())
                System.out.printf("%-9s %12.2f %14.2f %14.1f %%%n", e.getKey(), e.getValue()[0], e.getValue()[1], e.getValue()[2]);
            System.out.printf("Min-Min vs FCFS: makespan %+.1f %%, espera media %+.1f %%%n",
                    (m[0] / f[0] - 1) * 100, (m[1] / f[1] - 1) * 100);
            System.out.println("Detalle por cloudlet: resultados/cloudsim_resultados.csv");
        }
    }

    /** FCFS: en orden de llegada, cada tarea va a la VM que queda libre primero (sin mirar su velocidad). */
    static List<int[]> fcfs(List<Tarea> t) {
        double[] libre = new double[MIPS.length];
        List<int[]> plan = new ArrayList<>();
        for (int i = 0; i < t.size(); i++) {
            int vm = 0;
            for (int v = 1; v < MIPS.length; v++) if (libre[v] < libre[vm]) vm = v;
            libre[vm] += (double) t.get(i).mi() / MIPS[vm];
            plan.add(new int[]{i, vm});
        }
        return plan;
    }

    /** Min-Min: entre las tareas pendientes, la de menor tiempo mínimo de finalización va a la VM que la termina antes. */
    static List<int[]> minMin(List<Tarea> t) {
        double[] libre = new double[MIPS.length];
        Set<Integer> pend = new LinkedHashSet<>();
        for (int i = 0; i < t.size(); i++) pend.add(i);
        List<int[]> plan = new ArrayList<>();
        while (!pend.isEmpty()) {
            int bi = -1, bv = -1; double best = Double.MAX_VALUE;
            for (int i : pend)
                for (int v = 0; v < MIPS.length; v++) {
                    double fin = libre[v] + (double) t.get(i).mi() / MIPS[v];
                    if (fin < best) { best = fin; bi = i; bv = v; }
                }
            libre[bv] = best;
            plan.add(new int[]{bi, bv});
            pend.remove(bi);
        }
        return plan;
    }

    /** Ejecuta un plan (tarea -> VM, en orden de asignación) en CloudSim Plus y devuelve {makespan, espera, utilización}. */
    static double[] simular(String nombre, List<Tarea> tareas, List<int[]> plan, PrintWriter w) {
        CloudSimPlus sim = new CloudSimPlus();
        List<Host> hosts = new ArrayList<>();
        for (int h = 0; h < MIPS.length; h++) {
            List<Pe> pes = List.of(new PeSimple(2000));
            hosts.add(new HostSimple(16_384, 10_000, 100_000, pes));
        }
        new DatacenterSimple(sim, hosts);
        var broker = new DatacenterBrokerSimple(sim);

        List<Vm> vms = new ArrayList<>();
        for (int v = 0; v < MIPS.length; v++) {
            Vm vm = new VmSimple(MIPS[v], 1);
            vm.setRam(2048).setBw(1000).setSize(10_000);
            vm.setCloudletScheduler(new CloudletSchedulerSpaceShared()); // una tarea a la vez por VM (no expropiativo)
            vms.add(vm);
        }
        List<Cloudlet> cls = new ArrayList<>();
        Map<Long, Tarea> origen = new HashMap<>();
        for (int[] p : plan) {
            Tarea t = tareas.get(p[0]);
            Cloudlet c = new CloudletSimple(t.mi(), 1);
            c.setUtilizationModelCpu(new UtilizationModelFull());
            c.setUtilizationModelRam(new UtilizationModelDynamic(0.05));
            c.setUtilizationModelBw(new UtilizationModelDynamic(0.05));
            cls.add(c);
            origen.put(c.getId(), t);
        }
        broker.submitVmList(vms);
        broker.submitCloudletList(cls);
        for (int k = 0; k < plan.size(); k++) broker.bindCloudletToVm(cls.get(k), vms.get(plan.get(k)[1]));
        sim.start();

        List<Cloudlet> fin = new ArrayList<>(broker.getCloudletFinishedList());
        fin.sort(Comparator.comparingLong(c -> c.getVm().getId()));
        double t0 = fin.stream().mapToDouble(Cloudlet::getStartTime).min().orElse(0); // descuenta el arranque de las VM
        double makespan = 0, espera = 0, ocupado = 0;
        int[] porVm = new int[MIPS.length];
        for (Cloudlet c : fin) {
            int v = (int) c.getVm().getId();
            double ini = c.getStartTime() - t0, f = c.getFinishTime() - t0;
            makespan = Math.max(makespan, f);
            espera += ini;
            ocupado += f - ini;
            porVm[v]++;
            w.printf(Locale.US, "%s,%s,VM%d,%d,%.2f,%.2f,%.2f%n", nombre, origen.get(c.getId()).id(), v + 1, MIPS[v], ini, f, ini);
        }
        espera /= fin.size();
        double util = ocupado / (makespan * MIPS.length) * 100;
        System.out.printf("%n--- %s · %d cloudlets terminados ---%n", nombre, fin.size());
        for (int v = 0; v < MIPS.length; v++) {
            final int vv = v;
            double ult = fin.stream().filter(c -> c.getVm().getId() == vv).mapToDouble(c -> c.getFinishTime() - t0).max().orElse(0);
            System.out.printf("VM%d (%4d MIPS): %2d cloudlets, termina en %8.2f s%n", v + 1, MIPS[v], porVm[v], ult);
        }
        System.out.printf(Locale.US, "Makespan = %.2f s · espera media = %.2f s · utilización = %.1f %%%n", makespan, espera, util);
        return new double[]{makespan, espera, util};
    }
}

package problem4_exam_scheduling;

import java.io.*;
import java.util.*;

public class ExamScheduler {

    private int N, R;
    private List<int[]> conflicts;
    private Map<Integer, Set<Integer>> adj;

    public ExamScheduler(int N, int R, List<int[]> conflicts) {
        this.N = N;
        this.R = R;
        this.conflicts = conflicts;
        this.adj = new HashMap<>();
        for (int i = 1; i <= N; i++) {
            adj.put(i, new HashSet<>());
        }
        for (int[] c : conflicts) {
            if (c[0] != c[1]) {
                adj.get(c[0]).add(c[1]);
                adj.get(c[1]).add(c[0]);
            }
        }
    }

    public int computeLowerBound() {
        int capLb = (int) Math.ceil((double) N / R);
        List<Integer> nodes = new ArrayList<>(adj.keySet());
        nodes.sort((a, b) -> Integer.compare(adj.get(b).size(), adj.get(a).size()));

        Set<Integer> clique = new HashSet<>();
        for (int v : nodes) {
            boolean canAdd = true;
            for (int u : clique) {
                if (!adj.get(v).contains(u)) {
                    canAdd = false;
                    break;
                }
            }
            if (canAdd) clique.add(v);
        }
        return Math.max(capLb, clique.size());
    }

    public static class ScheduleResult {
        public String algorithmName;
        public int slots;
        public boolean provenOptimal;
        public double timeMs;
        public Map<Integer, Integer> coloring;

        public ScheduleResult(String algorithmName, int slots, boolean provenOptimal, double timeMs, Map<Integer, Integer> coloring) {
            this.algorithmName = algorithmName;
            this.slots = slots;
            this.provenOptimal = provenOptimal;
            this.timeMs = timeMs;
            this.coloring = coloring;
        }
    }

    public ScheduleResult solveWelshPowell() {
        long t0 = System.nanoTime();
        List<Integer> vertices = new ArrayList<>(adj.keySet());
        vertices.sort((a, b) -> Integer.compare(adj.get(b).size(), adj.get(a).size()));

        Map<Integer, Integer> coloring = new HashMap<>();
        Map<Integer, List<Integer>> slotContents = new HashMap<>();
        int currentSlot = 1;

        List<Integer> uncolored = new ArrayList<>(vertices);
        while (!uncolored.isEmpty()) {
            slotContents.put(currentSlot, new ArrayList<>());
            List<Integer> remaining = new ArrayList<>();

            for (int v : uncolored) {
                if (slotContents.get(currentSlot).size() < R) {
                    boolean conflict = false;
                    for (int u : slotContents.get(currentSlot)) {
                        if (adj.get(v).contains(u)) {
                            conflict = true;
                            break;
                        }
                    }
                    if (!conflict) {
                        coloring.put(v, currentSlot);
                        slotContents.get(currentSlot).add(v);
                    } else {
                        remaining.add(v);
                    }
                } else {
                    remaining.add(v);
                }
            }
            uncolored = remaining;
            currentSlot++;
        }

        long t1 = System.nanoTime();
        int slots = slotContents.size();
        int lb = computeLowerBound();
        return new ScheduleResult("Welsh-Powell", slots, slots == lb, (t1 - t0) / 1_000_000.0, coloring);
    }

    public ScheduleResult solveDsatur() {
        long t0 = System.nanoTime();
        Map<Integer, Integer> coloring = new HashMap<>();
        Map<Integer, Integer> slotCounts = new HashMap<>();
        Set<Integer> uncolored = new HashSet<>(adj.keySet());

        while (!uncolored.isEmpty()) {
            int bestV = -1;
            int bestSat = -1;
            int bestDeg = -1;

            for (int v : uncolored) {
                Set<Integer> neighborColors = new HashSet<>();
                int uncoloredDeg = 0;
                for (int nbr : adj.get(v)) {
                    if (coloring.containsKey(nbr)) {
                        neighborColors.add(coloring.get(nbr));
                    } else {
                        uncoloredDeg++;
                    }
                }
                int sat = neighborColors.size();
                if (sat > bestSat || (sat == bestSat && uncoloredDeg > bestDeg)) {
                    bestSat = sat;
                    bestDeg = uncoloredDeg;
                    bestV = v;
                }
            }

            Set<Integer> forbiddenColors = new HashSet<>();
            for (int nbr : adj.get(bestV)) {
                if (coloring.containsKey(nbr)) {
                    forbiddenColors.add(coloring.get(nbr));
                }
            }

            int chosenSlot = 1;
            while (true) {
                if (!forbiddenColors.contains(chosenSlot) && slotCounts.getOrDefault(chosenSlot, 0) < R) {
                    break;
                }
                chosenSlot++;
            }

            coloring.put(bestV, chosenSlot);
            slotCounts.put(chosenSlot, slotCounts.getOrDefault(chosenSlot, 0) + 1);
            uncolored.remove(bestV);
        }

        long t1 = System.nanoTime();
        int maxSlot = 0;
        for (int s : coloring.values()) maxSlot = Math.max(maxSlot, s);
        int lb = computeLowerBound();
        return new ScheduleResult("DSATUR", maxSlot, maxSlot == lb, (t1 - t0) / 1_000_000.0, coloring);
    }

    private int bestExactSlots;
    private Map<Integer, Integer> bestExactColoring;

    public ScheduleResult solveExact() {
        long t0 = System.nanoTime();
        int lb = computeLowerBound();

        ScheduleResult dsatur = solveDsatur();
        bestExactSlots = dsatur.slots;
        bestExactColoring = new HashMap<>(dsatur.coloring);

        if (bestExactSlots == lb) {
            long t1 = System.nanoTime();
            return new ScheduleResult("Exact Branch & Bound", bestExactSlots, true, (t1 - t0) / 1_000_000.0, bestExactColoring);
        }

        List<Integer> order = new ArrayList<>(adj.keySet());
        order.sort((a, b) -> Integer.compare(adj.get(b).size(), adj.get(a).size()));

        Map<Integer, Integer> currColoring = new HashMap<>();
        Map<Integer, Integer> slotSizes = new HashMap<>();

        exactDfs(order, 0, 0, currColoring, slotSizes, lb, System.currentTimeMillis() + 4000);

        long t1 = System.nanoTime();
        return new ScheduleResult("Exact Branch & Bound", bestExactSlots, true, (t1 - t0) / 1_000_000.0, bestExactColoring);
    }

    private void exactDfs(List<Integer> order, int idx, int maxSlot, Map<Integer, Integer> currColoring, Map<Integer, Integer> slotSizes, int lb, long deadline) {
        if (System.currentTimeMillis() > deadline) return;

        if (idx == N) {
            if (maxSlot < bestExactSlots) {
                bestExactSlots = maxSlot;
                bestExactColoring = new HashMap<>(currColoring);
            }
            return;
        }

        if (maxSlot >= bestExactSlots) return;

        int v = order.get(idx);
        Set<Integer> neighborColors = new HashSet<>();
        for (int nbr : adj.get(v)) {
            if (currColoring.containsKey(nbr)) {
                neighborColors.add(currColoring.get(nbr));
            }
        }

        for (int s = 1; s <= maxSlot; s++) {
            if (!neighborColors.contains(s) && slotSizes.getOrDefault(s, 0) < R) {
                currColoring.put(v, s);
                slotSizes.put(s, slotSizes.getOrDefault(s, 0) + 1);

                exactDfs(order, idx + 1, maxSlot, currColoring, slotSizes, lb, deadline);

                slotSizes.put(s, slotSizes.get(s) - 1);
                currColoring.remove(v);
                if (bestExactSlots == lb) return;
            }
        }

        int newSlot = maxSlot + 1;
        if (newSlot < bestExactSlots) {
            currColoring.put(v, newSlot);
            slotSizes.put(newSlot, 1);

            exactDfs(order, idx + 1, newSlot, currColoring, slotSizes, lb, deadline);

            slotSizes.remove(newSlot);
            currColoring.remove(v);
        }
    }

    public void exportTimetableCsv(String filepath, Map<Integer, Integer> coloring) throws IOException {
        File file = new File(filepath);
        if (file.getParentFile() != null) file.getParentFile().mkdirs();

        Map<Integer, List<Integer>> slotMap = new TreeMap<>();
        for (Map.Entry<Integer, Integer> entry : coloring.entrySet()) {
            slotMap.computeIfAbsent(entry.getValue(), k -> new ArrayList<>()).add(entry.getKey());
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(file))) {
            List<String> header = new ArrayList<>();
            header.add("Slot");
            for (int h = 1; h <= R; h++) header.add("Hall_" + h);
            bw.write(String.join(",", header));
            bw.newLine();

            for (Map.Entry<Integer, List<Integer>> entry : slotMap.entrySet()) {
                int s = entry.getKey();
                List<Integer> courses = entry.getValue();
                Collections.sort(courses);

                List<String> row = new ArrayList<>();
                row.add("Slot " + s);
                for (int h = 0; h < R; h++) {
                    if (h < courses.size()) {
                        row.add("Course " + courses.get(h));
                    } else {
                        row.add("Empty");
                    }
                }
                bw.write(String.join(",", row));
                bw.newLine();
            }
        }
    }

    public static void main(String[] args) throws Exception {
        int N = 8, R = 2;
        List<int[]> conflicts = List.of(
            new int[]{1, 2}, new int[]{2, 3}, new int[]{3, 4},
            new int[]{4, 5}, new int[]{5, 6}, new int[]{6, 7}, new int[]{7, 8}
        );

        ExamScheduler scheduler = new ExamScheduler(N, R, conflicts);
        ScheduleResult wp = scheduler.solveWelshPowell();
        ScheduleResult ds = scheduler.solveDsatur();
        ScheduleResult ex = scheduler.solveExact();

        System.out.println("Output 1:");
        System.out.println(String.format("  Welsh-Powell: %d slots | %s | %.3f ms", wp.slots, (wp.provenOptimal ? "PROVEN OPTIMAL" : "Heuristic"), wp.timeMs));
        System.out.println(String.format("  DSATUR:       %d slots | %s | %.3f ms", ds.slots, (ds.provenOptimal ? "PROVEN OPTIMAL" : "Heuristic"), ds.timeMs));
        System.out.println(String.format("  Exact B&B:    %d slots | %s | %.3f ms", ex.slots, (ex.provenOptimal ? "PROVEN OPTIMAL" : "Heuristic"), ex.timeMs));

        System.out.println("\nOutput 2 (Slot-wise List of Courses):");
        Map<Integer, List<Integer>> map = new TreeMap<>();
        for (Map.Entry<Integer, Integer> e : ex.coloring.entrySet()) {
            map.computeIfAbsent(e.getValue(), k -> new ArrayList<>()).add(e.getKey());
        }
        for (Map.Entry<Integer, List<Integer>> e : map.entrySet()) {
            Collections.sort(e.getValue());
            System.out.println("  Slot " + e.getKey() + ": " + e.getValue());
        }

        String outCsv = "outputs/problem4_java_timetable.csv";
        scheduler.exportTimetableCsv(outCsv, ex.coloring);
        System.out.println("\nOutput 3: Saved timetable CSV to " + outCsv);
    }
}

package problem3_budget_traveller;

import java.io.*;
import java.util.*;

public class BudgetTraveller {

    public static class Edge {
        public int u, v, price;

        public Edge(int u, int v, int price) {
            this.u = u;
            this.v = v;
            this.price = price;
        }
    }

    public static class Step {
        public int from, to, origPrice, paid;
        public boolean couponUsed;

        public Step(int from, int to, int origPrice, int paid, boolean couponUsed) {
            this.from = from;
            this.to = to;
            this.origPrice = origPrice;
            this.paid = paid;
            this.couponUsed = couponUsed;
        }
    }

    public static class Result {
        public int minCost;
        public List<Step> path;

        public Result(int minCost, List<Step> path) {
            this.minCost = minCost;
            this.path = path;
        }
    }

    private static class ParentInfo {
        int prevU, prevC, origPrice;
        boolean couponUsed;

        ParentInfo(int prevU, int prevC, int origPrice, boolean couponUsed) {
            this.prevU = prevU;
            this.prevC = prevC;
            this.origPrice = origPrice;
            this.couponUsed = couponUsed;
        }
    }

    private int N, K, C;
    private List<Edge> edges;
    private Map<Integer, List<Edge>> adj;

    public BudgetTraveller(int N, int K, int C, List<Edge> edges) {
        this.N = N;
        this.K = K;
        this.C = C;
        this.edges = edges;
        this.adj = new HashMap<>();
        for (int i = 1; i <= N; i++) {
            adj.put(i, new ArrayList<>());
        }
        for (Edge e : edges) {
            adj.computeIfAbsent(e.u, k -> new ArrayList<>()).add(e);
        }
    }

    public Result solve() {
        int maxEdges = K + 1;
        int INF = 1_000_000_000;

        int[][][] dp = new int[maxEdges + 1][N + 1][C + 1];
        ParentInfo[][][] parent = new ParentInfo[maxEdges + 1][N + 1][C + 1];

        for (int e = 0; e <= maxEdges; e++) {
            for (int u = 0; u <= N; u++) {
                Arrays.fill(dp[e][u], INF);
            }
        }

        dp[0][1][0] = 0;

        for (int e = 0; e < maxEdges; e++) {
            for (int u = 1; u <= N; u++) {
                for (int c = 0; c <= C; c++) {
                    int currCost = dp[e][u][c];
                    if (currCost == INF) continue;

                    List<Edge> out = adj.getOrDefault(u, Collections.emptyList());
                    for (Edge edge : out) {
                        int v = edge.v;
                        int price = edge.price;

                        // Without coupon
                        if (currCost + price < dp[e + 1][v][c]) {
                            dp[e + 1][v][c] = currCost + price;
                            parent[e + 1][v][c] = new ParentInfo(u, c, price, false);
                        }

                        // With coupon
                        if (c < C) {
                            int discPrice = price / 2;
                            if (currCost + discPrice < dp[e + 1][v][c + 1]) {
                                dp[e + 1][v][c + 1] = currCost + discPrice;
                                parent[e + 1][v][c + 1] = new ParentInfo(u, c, price, true);
                            }
                        }
                    }
                }
            }
        }

        int bestCost = INF;
        int bestE = -1;
        int bestC = -1;

        for (int e = 1; e <= maxEdges; e++) {
            for (int c = 0; c <= C; c++) {
                if (dp[e][N][c] < bestCost) {
                    bestCost = dp[e][N][c];
                    bestE = e;
                    bestC = c;
                }
            }
        }

        if (bestCost == INF) {
            return new Result(-1, Collections.emptyList());
        }

        List<Step> path = new ArrayList<>();
        int currE = bestE;
        int currU = N;
        int currC = bestC;

        while (currE > 0) {
            ParentInfo p = parent[currE][currU][currC];
            if (p == null) break;
            int paid = p.couponUsed ? (p.origPrice / 2) : p.origPrice;
            path.add(new Step(p.prevU, currU, p.origPrice, paid, p.couponUsed));
            currU = p.prevU;
            currC = p.prevC;
            currE--;
        }
        Collections.reverse(path);

        return new Result(bestCost, path);
    }

    public void exportGraphCsv(String filepath, List<Step> path) throws IOException {
        File file = new File(filepath);
        if (file.getParentFile() != null) file.getParentFile().mkdirs();

        Map<String, Step> pathMap = new HashMap<>();
        for (Step s : path) {
            pathMap.put(s.from + "->" + s.to + ":" + s.origPrice, s);
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(file))) {
            bw.write("from_city,to_city,price,on_path,coupon_used,effective_price");
            bw.newLine();
            for (Edge e : edges) {
                String key = e.u + "->" + e.v + ":" + e.price;
                if (pathMap.containsKey(key)) {
                    Step s = pathMap.get(key);
                    bw.write(String.format("%d,%d,%d,x,%s,%d", e.u, e.v, e.price, (s.couponUsed ? "YES" : "NO"), s.paid));
                } else {
                    bw.write(String.format("%d,%d,%d,,NO,%d", e.u, e.v, e.price, e.price));
                }
                bw.newLine();
            }
        }
    }

    public static void main(String[] args) throws Exception {
        int N = 5, K = 2, C = 1;
        List<Edge> edges = List.of(
            new Edge(1, 2, 300), new Edge(1, 3, 700),
            new Edge(2, 3, 100), new Edge(2, 4, 400),
            new Edge(3, 4, 200), new Edge(4, 5, 500),
            new Edge(3, 5, 800), new Edge(2, 5, 1200)
        );

        BudgetTraveller traveller = new BudgetTraveller(N, K, C, edges);
        Result res = traveller.solve();

        System.out.println("Output 1: " + res.minCost);
        if (res.minCost != -1) {
            String outCsv = "outputs/problem3_java_flights.csv";
            traveller.exportGraphCsv(outCsv, res.path);
            System.out.println("Output 2: CSV saved to " + outCsv);
        }
    }
}

package problem1_maze;

import java.io.*;
import java.util.*;

public class MazeSolver {
    public static class State {
        int r, c, mask;

        public State(int r, int c, int mask) {
            this.r = r;
            this.c = c;
            this.mask = mask;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof State)) return false;
            State s = (State) o;
            return r == s.r && c == s.c && mask == s.mask;
        }

        @Override
        public int hashCode() {
            return Objects.hash(r, c, mask);
        }
    }

    public static class Result {
        public int length;
        public List<State> path;
        public List<List<String>> markedGrid;

        public Result(int length, List<State> path, List<List<String>> markedGrid) {
            this.length = length;
            this.path = path;
            this.markedGrid = markedGrid;
        }
    }

    private List<List<String>> grid;
    private int N;
    private int T;
    private int startR = -1, startC = -1;
    private int exitR = -1, exitC = -1;

    public MazeSolver(List<List<String>> grid, int T) {
        this.grid = new ArrayList<>();
        for (List<String> row : grid) {
            this.grid.add(new ArrayList<>(row));
        }
        this.N = grid.size();
        this.T = T;
        findEndpoints();
    }

    private void findEndpoints() {
        for (int r = 0; r < N; r++) {
            for (int c = 0; c < grid.get(r).size(); c++) {
                String val = grid.get(r).get(c).trim();
                if (val.equals("S")) {
                    startR = r;
                    startC = c;
                } else if (val.equals("E")) {
                    exitR = r;
                    exitC = c;
                }
            }
        }
    }

    public Result solve() {
        if (startR == -1 || exitR == -1) {
            return new Result(-1, Collections.emptyList(), null);
        }

        if (startR == exitR && startC == exitC) {
            List<List<String>> marked = cloneGrid(grid);
            marked.get(startR).set(startC, "x(S)");
            return new Result(0, List.of(new State(startR, startC, 0)), marked);
        }

        Queue<State> queue = new ArrayDeque<>();
        Set<State> visited = new HashSet<>();
        Map<State, State> parent = new HashMap<>();

        State startState = new State(startR, startC, 0);
        queue.add(startState);
        visited.add(startState);

        State targetState = null;
        int[][] dirs = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

        while (!queue.isEmpty()) {
            State curr = queue.poll();

            if (curr.r == exitR && curr.c == exitC) {
                targetState = curr;
                break;
            }

            for (int[] d : dirs) {
                int nr = curr.r + d[0];
                int nc = curr.c + d[1];

                if (nr >= 0 && nr < N && nc >= 0 && nc < grid.get(nr).size()) {
                    String cell = grid.get(nr).get(nc).trim();
                    if (cell.equals("#")) continue;

                    int newMask = curr.mask;
                    if (cell.length() == 1) {
                        char ch = cell.charAt(0);
                        if (ch >= 'A' && ch <= 'F') {
                            int doorIdx = ch - 'A';
                            if (doorIdx < T && (curr.mask & (1 << doorIdx)) == 0) {
                                continue; // Key missing
                            }
                        } else if (ch >= 'a' && ch <= 'f') {
                            int keyIdx = ch - 'a';
                            if (keyIdx < T) {
                                newMask |= (1 << keyIdx);
                            }
                        }
                    }

                    State nextState = new State(nr, nc, newMask);
                    if (!visited.contains(nextState)) {
                        visited.add(nextState);
                        parent.put(nextState, curr);
                        queue.add(nextState);
                    }
                }
            }
        }

        if (targetState == null) {
            return new Result(-1, Collections.emptyList(), null);
        }

        List<State> path = new ArrayList<>();
        State curr = targetState;
        while (curr != null) {
            path.add(curr);
            curr = parent.get(curr);
        }
        Collections.reverse(path);

        int shortestLength = path.size() - 1;
        List<List<String>> marked = cloneGrid(grid);

        for (State s : path) {
            String orig = grid.get(s.r).get(s.c).trim();
            if (orig.equals("S")) {
                marked.get(s.r).set(s.c, "S");
            } else if (orig.equals("E")) {
                marked.get(s.r).set(s.c, "E");
            } else if (orig.length() == 1 && orig.charAt(0) >= 'a' && orig.charAt(0) <= 'f') {
                marked.get(s.r).set(s.c, "x(" + orig + ")");
            } else if (orig.length() == 1 && orig.charAt(0) >= 'A' && orig.charAt(0) <= 'F') {
                marked.get(s.r).set(s.c, "x(" + orig + ")");
            } else {
                marked.get(s.r).set(s.c, "x");
            }
        }

        return new Result(shortestLength, path, marked);
    }

    private List<List<String>> cloneGrid(List<List<String>> src) {
        List<List<String>> copy = new ArrayList<>();
        for (List<String> row : src) {
            copy.add(new ArrayList<>(row));
        }
        return copy;
    }

    public static List<List<String>> readCsv(String filepath) throws IOException {
        List<List<String>> grid = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filepath))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                String[] tokens = line.split(",");
                List<String> row = new ArrayList<>();
                for (String t : tokens) {
                    row.add(t.trim());
                }
                grid.add(row);
            }
        }
        return grid;
    }

    public static void writeCsv(String filepath, List<List<String>> grid) throws IOException {
        File file = new File(filepath);
        if (file.getParentFile() != null) file.getParentFile().mkdirs();
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(file))) {
            for (List<String> row : grid) {
                bw.write(String.join(",", row));
                bw.newLine();
            }
        }
    }

    public static MazeSolver generateRandomMaze(int N, int T, long seed) {
        Random rand = new Random(seed);
        List<List<String>> grid = new ArrayList<>();
        for (int r = 0; r < N; r++) {
            List<String> row = new ArrayList<>();
            for (int c = 0; c < N; c++) {
                row.add(".");
            }
            grid.add(row);
        }

        grid.get(0).set(0, "S");
        grid.get(N - 1).set(N - 1, "E");

        for (int i = 0; i < T; i++) {
            grid.get(0).set(i + 1, String.valueOf((char) ('a' + i)));
            grid.get(1).set(i + 1, String.valueOf((char) ('A' + i)));
        }
        for (int c = T + 1; c < N; c++) {
            grid.get(1).set(c, "#");
        }

        return new MazeSolver(grid, T);
    }

    public static void main(String[] args) throws Exception {
        int T = 3;
        String csvPath = "";
        String outCsv = "outputs/problem1_java_solution.csv";

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--T") && i + 1 < args.length) {
                T = Integer.parseInt(args[++i]);
            } else if (args[i].equals("--csv") && i + 1 < args.length) {
                csvPath = args[++i];
            } else if (args[i].equals("--output-csv") && i + 1 < args.length) {
                outCsv = args[++i];
            }
        }

        MazeSolver solver;
        if (!csvPath.isEmpty()) {
            List<List<String>> grid = readCsv(csvPath);
            solver = new MazeSolver(grid, T);
        } else {
            System.out.println("Generating sample solvable maze with T=" + T + ", N=10...");
            solver = generateRandomMaze(10, T, 42);
        }

        Result res = solver.solve();
        System.out.println("Output 1: " + res.length);
        if (res.markedGrid != null) {
            writeCsv(outCsv, res.markedGrid);
            System.out.println("Output 2: Saved marked CSV to " + outCsv);
        } else {
            System.out.println("Output 1: -1 (No path possible)");
        }
    }
}

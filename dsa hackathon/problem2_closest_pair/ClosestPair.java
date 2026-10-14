package problem2_closest_pair;

import java.util.*;

public class ClosestPair {

    public static class Point {
        public double x, y;

        public Point(double x, double y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public String toString() {
            return String.format(Locale.US, "(%.4f, %.4f)", x, y);
        }
    }

    public static class Result {
        public double minDistance;
        public Point p1;
        public Point p2;
        public double executionTimeMs;

        public Result(double minDistance, Point p1, Point p2, double executionTimeMs) {
            this.minDistance = minDistance;
            this.p1 = p1;
            this.p2 = p2;
            this.executionTimeMs = executionTimeMs;
        }
    }

    public static double dist(Point p1, Point p2) {
        return Math.hypot(p1.x - p2.x, p1.y - p2.y);
    }

    public static Result bruteForce(List<Point> points) {
        long t0 = System.nanoTime();
        int n = points.size();
        if (n < 2) {
            return new Result(Double.POSITIVE_INFINITY, null, null, 0.0);
        }

        double minDist = Double.POSITIVE_INFINITY;
        Point best1 = null, best2 = null;

        for (int i = 0; i < n; i++) {
            Point pi = points.get(i);
            for (int j = i + 1; j < n; j++) {
                Point pj = points.get(j);
                double d = dist(pi, pj);
                if (d < minDist) {
                    minDist = d;
                    best1 = pi;
                    best2 = pj;
                }
            }
        }
        long t1 = System.nanoTime();
        return new Result(minDist, best1, best2, (t1 - t0) / 1_000_000.0);
    }

    public static Result divideAndConquer(List<Point> points) {
        long t0 = System.nanoTime();
        int n = points.size();
        if (n < 2) {
            return new Result(Double.POSITIVE_INFINITY, null, null, 0.0);
        }

        Point[] px = points.toArray(new Point[0]);
        Arrays.sort(px, (a, b) -> {
            if (Double.compare(a.x, b.x) != 0) return Double.compare(a.x, b.x);
            return Double.compare(a.y, b.y);
        });

        Point[] py = px.clone();
        Arrays.sort(py, (a, b) -> {
            if (Double.compare(a.y, b.y) != 0) return Double.compare(a.y, b.y);
            return Double.compare(a.x, b.x);
        });

        ResultPair pair = recursiveClosest(px, 0, n - 1, py);
        long t1 = System.nanoTime();
        return new Result(pair.dist, pair.p1, pair.p2, (t1 - t0) / 1_000_000.0);
    }

    private static class ResultPair {
        double dist;
        Point p1, p2;

        ResultPair(double dist, Point p1, Point p2) {
            this.dist = dist;
            this.p1 = p1;
            this.p2 = p2;
        }
    }

    private static ResultPair recursiveClosest(Point[] px, int low, int high, Point[] py) {
        int count = high - low + 1;
        if (count <= 3) {
            double minD = Double.POSITIVE_INFINITY;
            Point p1 = null, p2 = null;
            for (int i = low; i <= high; i++) {
                for (int j = i + 1; j <= high; j++) {
                    double d = dist(px[i], px[j]);
                    if (d < minD) {
                        minD = d;
                        p1 = px[i];
                        p2 = px[j];
                    }
                }
            }
            return new ResultPair(minD, p1, p2);
        }

        int mid = low + (high - low) / 2;
        Point midPoint = px[mid];

        // Split py into left and right
        Set<Point> leftSet = new HashSet<>();
        for (int i = low; i <= mid; i++) {
            leftSet.add(px[i]);
        }

        Point[] pyLeft = new Point[mid - low + 1];
        Point[] pyRight = new Point[high - mid];
        int li = 0, ri = 0;
        for (Point p : py) {
            if (leftSet.contains(p) && li < pyLeft.length) {
                pyLeft[li++] = p;
            } else if (ri < pyRight.length) {
                pyRight[ri++] = p;
            }
        }

        ResultPair leftRes = recursiveClosest(px, low, mid, pyLeft);
        ResultPair rightRes = recursiveClosest(px, mid + 1, high, pyRight);

        ResultPair best = (leftRes.dist <= rightRes.dist) ? leftRes : rightRes;
        double dMin = best.dist;

        // Build strip
        List<Point> strip = new ArrayList<>();
        for (Point p : py) {
            if (Math.abs(p.x - midPoint.x) < dMin) {
                strip.add(p);
            }
        }

        for (int i = 0; i < strip.size(); i++) {
            Point p = strip.get(i);
            for (int j = i + 1; j < Math.min(i + 8, strip.size()); j++) {
                Point q = strip.get(j);
                if ((q.y - p.y) >= dMin) break;
                double d = dist(p, q);
                if (d < dMin) {
                    dMin = d;
                    best = new ResultPair(dMin, p, q);
                }
            }
        }

        return best;
    }

    public static List<Point> generateRandomPoints(int n, double range, long seed) {
        Random rand = new Random(seed);
        List<Point> list = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            double x = -range + (2 * range) * rand.nextDouble();
            double y = -range + (2 * range) * rand.nextDouble();
            list.add(new Point(x, y));
        }
        return list;
    }

    public static void main(String[] args) {
        int N = 1000;
        if (args.length > 0) {
            try {
                N = Integer.parseInt(args[0]);
            } catch (NumberFormatException ignored) {}
        }

        List<Point> points = generateRandomPoints(N, 1000.0, 42);

        Result bf = bruteForce(points);
        Result dc = divideAndConquer(points);

        System.out.println(String.format(Locale.US, "First line (Brute-Force): %.6f, %s, %s", bf.minDistance, bf.p1, bf.p2));
        System.out.println(String.format(Locale.US, "Second line (Divide-and-Conquer): %.6f, %s, %s", dc.minDistance, dc.p1, dc.p2));
        System.out.println(String.format(Locale.US, "Third line: Brute-Force: %.4f ms | Divide-and-Conquer: %.4f ms", bf.executionTimeMs, dc.executionTimeMs));
    }
}

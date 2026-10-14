"""
Problem 2: Closest Pair of Points Comparative Analysis
Implements Brute-Force O(N^2) and Divide-and-Conquer O(N log N) algorithms.
Handles all corner cases (duplicates, collinear points, identical x/y, N < 2, N = 2).
Provides benchmarking and verification of identical minimum distance.
"""

import math
import time
import random
from typing import List, Tuple, Optional, Dict, Any


Point = Tuple[float, float]


def euclidean_dist(p1: Point, p2: Point) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def closest_pair_brute_force(points: List[Point]) -> Tuple[float, Optional[Point], Optional[Point]]:
    """
    Brute-force O(N^2) pairwise distance comparison.
    Returns: (min_dist, point1, point2)
    """
    n = len(points)
    if n < 2:
        return float('inf'), None, None
    if n == 2:
        return euclidean_dist(points[0], points[1]), points[0], points[1]

    min_dist = float('inf')
    best_pair = (None, None)

    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_dist(points[i], points[j])
            if d < min_dist:
                min_dist = d
                best_pair = (points[i], points[j])

    return min_dist, best_pair[0], best_pair[1]


def closest_pair_divide_and_conquer(points: List[Point], record_steps: bool = False) -> Tuple[float, Optional[Point], Optional[Point], Optional[Dict[str, Any]]]:
    """
    Divide-and-Conquer O(N log N) closest pair algorithm.
    Pre-sorts points by X, and recursively divides and merges using strip search.
    Returns: (min_dist, point1, point2, trace_data)
    """
    n = len(points)
    if n < 2:
        return float('inf'), None, None, None
    if n == 2:
        return euclidean_dist(points[0], points[1]), points[0], points[1], {"mid_x": (points[0][0] + points[1][0]) / 2, "d": euclidean_dist(points[0], points[1])}

    pts_sorted_x = sorted(points, key=lambda p: (p[0], p[1]))
    pts_sorted_y = sorted(points, key=lambda p: (p[1], p[0]))

    trace_data = {"dividing_lines": [], "final_strip": []} if record_steps else None

    def _closest_recursive(px: List[Point], py: List[Point]) -> Tuple[float, Point, Point]:
        num_pts = len(px)
        if num_pts <= 3:
            return closest_pair_brute_force(px)

        mid_idx = num_pts // 2
        mid_pt = px[mid_idx]
        mid_x = mid_pt[0]

        # Divide px
        left_px = px[:mid_idx]
        right_px = px[mid_idx:]

        # Divide py in O(N) using set of left points
        left_set = set(left_px)
        left_py = [p for p in py if p in left_set]
        right_py = [p for p in py if p not in left_set]

        # Conquer
        d_left, p1_l, p2_l = _closest_recursive(left_px, left_py)
        d_right, p1_r, p2_r = _closest_recursive(right_px, right_py)

        if d_left <= d_right:
            d_min = d_left
            best_pair = (p1_l, p2_l)
        else:
            d_min = d_right
            best_pair = (p1_r, p2_r)

        if record_steps:
            trace_data["dividing_lines"].append({"mid_x": mid_x, "d": d_min})

        # Strip check: points within distance d_min of mid_x
        strip = [p for p in py if abs(p[0] - mid_x) < d_min]
        strip_len = len(strip)

        for i in range(strip_len):
            # Geometric packing: only need to check at most next 7 points in sorted y
            for j in range(i + 1, min(i + 8, strip_len)):
                if (strip[j][1] - strip[i][1]) >= d_min:
                    break
                d = euclidean_dist(strip[i], strip[j])
                if d < d_min:
                    d_min = d
                    best_pair = (strip[i], strip[j])

        return d_min, best_pair[0], best_pair[1]

    d_final, p1, p2 = _closest_recursive(pts_sorted_x, pts_sorted_y)

    if record_steps:
        mid_val = pts_sorted_x[n // 2][0]
        final_strip_pts = [p for p in points if abs(p[0] - mid_val) < d_final]
        trace_data["final_mid_x"] = mid_val
        trace_data["final_d"] = d_final
        trace_data["final_strip_pts"] = final_strip_pts

    return d_final, p1, p2, trace_data


def generate_random_points(N: int, coord_range: float = 1000.0, seed: Optional[int] = None) -> List[Point]:
    """Generates N random 2D points (x, y)."""
    if seed is not None:
        random.seed(seed)
    return [(round(random.uniform(-coord_range, coord_range), 4),
             round(random.uniform(-coord_range, coord_range), 4)) for _ in range(N)]


def run_single_comparison(N: int, points: Optional[List[Point]] = None, seed: Optional[int] = 42):
    if points is None:
        points = generate_random_points(N, seed=seed)

    if N < 2:
        print("Error: At least 2 points are required to compute closest pair.")
        return

    # 1. Brute-Force
    t0 = time.perf_counter()
    bf_dist, bf_p1, bf_p2 = closest_pair_brute_force(points)
    t1 = time.perf_counter()
    bf_time_ms = (t1 - t0) * 1000.0

    # 2. Divide-and-Conquer
    t2 = time.perf_counter()
    dc_dist, dc_p1, dc_p2, _ = closest_pair_divide_and_conquer(points)
    t3 = time.perf_counter()
    dc_time_ms = (t3 - t2) * 1000.0

    # Output Format required by prompt:
    # First line (Brute-Force): Minimum distance (6 decimal places), followed by the two coordinates of the closest pair.
    # Second line (Divide-and-Conquer): Minimum distance (6 decimal places), followed by the two coordinates of the closest pair.
    # Third line: Execution time of each algorithm (in ms).
    print(f"Brute-Force: {bf_dist:.6f}, Point 1: {bf_p1}, Point 2: {bf_p2}")
    print(f"Divide-and-Conquer: {dc_dist:.6f}, Point 1: {dc_p1}, Point 2: {dc_p2}")
    print(f"Execution time (ms) - Brute-Force: {bf_time_ms:.4f} ms | Divide-and-Conquer: {dc_time_ms:.4f} ms")

    # Verification
    diff = abs(bf_dist - dc_dist)
    assert diff < 1e-9, f"Mismatch in distances: BF={bf_dist}, DC={dc_dist}"
    print("Verification: Both algorithms AGREED on minimum distance! Difference:", diff)


def benchmark_suite(sizes: List[int] = [10, 50, 100, 500, 1000, 2000, 3000, 5000]) -> Dict[str, Any]:
    """Runs comparative benchmark for increasing input sizes."""
    results = {
        "N": [],
        "bf_time_ms": [],
        "dc_time_ms": [],
        "bf_dist": [],
        "dc_dist": [],
        "agreed": []
    }

    print("\n" + "="*80)
    print(f"{'N':<8} | {'BF Dist':<12} | {'DC Dist':<12} | {'BF Time (ms)':<14} | {'DC Time (ms)':<14} | {'Speedup':<10} | {'Status'}")
    print("="*80)

    for n in sizes:
        pts = generate_random_points(n, seed=n * 7 + 13)

        # Time Brute Force
        t0 = time.perf_counter()
        bf_d, _, _ = closest_pair_brute_force(pts)
        t_bf = (time.perf_counter() - t0) * 1000.0

        # Time Divide & Conquer
        t0 = time.perf_counter()
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        t_dc = (time.perf_counter() - t0) * 1000.0

        agreed = abs(bf_d - dc_d) < 1e-9
        speedup = (t_bf / t_dc) if t_dc > 0 else 1.0

        results["N"].append(n)
        results["bf_time_ms"].append(t_bf)
        results["dc_time_ms"].append(t_dc)
        results["bf_dist"].append(bf_d)
        results["dc_dist"].append(dc_d)
        results["agreed"].append(agreed)

        status_str = "PASS" if agreed else "FAIL"
        print(f"{n:<8} | {bf_d:<12.6f} | {dc_d:<12.6f} | {t_bf:<14.4f} | {t_dc:<14.4f} | {speedup:<10.2f}x | {status_str}")

    print("="*80 + "\n")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Closest Pair of Points Comparative Analysis")
    parser.add_argument("--N", type=int, default=100, help="Number of points")
    parser.add_argument("--benchmark", action="store_true", help="Run full benchmark suite")
    args = parser.parse_args()

    if args.benchmark:
        benchmark_suite()
    else:
        print(f"Running comparison for N={args.N}:")
        run_single_comparison(args.N)

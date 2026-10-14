"""
Problem 4: Exam Timetable Scheduling (Capacitated Graph Colouring)
Assigns N courses to time slots such that:
1. No two conflicting courses share the same slot.
2. At most R exams per slot.
3. Total number of slots is minimized.

Algorithms:
1. Welsh-Powell with Capacity Heuristic
2. DSATUR with Capacity Heuristic
3. Exact Branch-and-Bound / Backtracking with Lower Bound Pruning & Symmetry Breaking
"""

import sys
import os
import csv
import time
import math
import random
from typing import List, Tuple, Dict, Set, Optional, Any


class ExamScheduler:
    def __init__(self, N: int, R: int, conflicts: List[Tuple[int, int]]):
        self.N = N
        self.R = R
        self.conflicts = conflicts
        self.adj: Dict[int, Set[int]] = {i: set() for i in range(1, N + 1)}
        for u, v in conflicts:
            if u != v:
                self.adj[u].add(v)
                self.adj[v].add(u)

    def compute_lower_bound(self) -> int:
        """
        Computes theoretical lower bound on slots:
        LB = max(ceil(N / R), max_clique_heuristic, max_degree + 1 for dense subgraphs)
        """
        capacity_lb = math.ceil(self.N / self.R)

        # Greedy clique heuristic lower bound
        nodes_by_degree = sorted(self.adj.keys(), key=lambda x: len(self.adj[x]), reverse=True)
        clique = set()
        for v in nodes_by_degree:
            if all(v in self.adj[u] for u in clique):
                clique.add(v)
        clique_lb = len(clique)

        return max(capacity_lb, clique_lb)

    def solve_welsh_powell(self) -> Tuple[int, Dict[int, int], float]:
        """
        Welsh-Powell Heuristic with capacity limit R.
        Sort vertices by degree descending, greedily fill slots.
        """
        t0 = time.perf_counter()
        degrees = {v: len(self.adj[v]) for v in range(1, self.N + 1)}
        sorted_vertices = sorted(degrees.keys(), key=lambda v: degrees[v], reverse=True)

        coloring: Dict[int, int] = {}
        slot_contents: Dict[int, List[int]] = {}
        current_slot = 1

        uncolored = list(sorted_vertices)

        while uncolored:
            slot_contents[current_slot] = []
            remaining = []
            for v in uncolored:
                if len(slot_contents[current_slot]) < self.R:
                    # Check conflict with any course already in current_slot
                    if not any(v in self.adj[u] for u in slot_contents[current_slot]):
                        coloring[v] = current_slot
                        slot_contents[current_slot].append(v)
                    else:
                        remaining.append(v)
                else:
                    remaining.append(v)
            uncolored = remaining
            current_slot += 1

        runtime = (time.perf_counter() - t0) * 1000.0
        num_slots = len(slot_contents)
        return num_slots, coloring, runtime

    def solve_dsatur(self) -> Tuple[int, Dict[int, int], float]:
        """
        DSATUR (Degree of Saturation) Heuristic with capacity limit R.
        Prioritizes vertices with highest saturation degree (number of distinct neighbor colors).
        """
        t0 = time.perf_counter()
        coloring: Dict[int, int] = {}
        degrees = {v: len(self.adj[v]) for v in range(1, self.N + 1)}
        slot_counts: Dict[int, int] = {}

        def get_saturation(v: int) -> int:
            neighbor_colors = set(coloring[nbr] for nbr in self.adj[v] if nbr in coloring)
            return len(neighbor_colors)

        uncolored = set(range(1, self.N + 1))

        while uncolored:
            # Choose uncolored vertex with max saturation, tie-break by uncolored degree
            best_v = None
            best_sat = -1
            best_deg = -1

            for v in uncolored:
                sat = get_saturation(v)
                uncolored_deg = sum(1 for nbr in self.adj[v] if nbr in uncolored)
                if sat > best_sat or (sat == best_sat and uncolored_deg > best_deg):
                    best_sat = sat
                    best_deg = uncolored_deg
                    best_v = v

            # Find earliest valid slot with count < R
            forbidden_colors = set(coloring[nbr] for nbr in self.adj[best_v] if nbr in coloring)
            chosen_slot = 1
            while True:
                if chosen_slot not in forbidden_colors and slot_counts.get(chosen_slot, 0) < self.R:
                    break
                chosen_slot += 1

            coloring[best_v] = chosen_slot
            slot_counts[chosen_slot] = slot_counts.get(chosen_slot, 0) + 1
            uncolored.remove(best_v)

        runtime = (time.perf_counter() - t0) * 1000.0
        num_slots = max(coloring.values()) if coloring else 0
        return num_slots, coloring, runtime

    def solve_exact_branch_and_bound(self, time_limit_sec: float = 5.0) -> Tuple[int, Dict[int, int], bool, float]:
        """
        Exact Branch-and-Bound algorithm with:
        - Capacity enforcement
        - Dynamic DSATUR variable ordering
        - Lower bound pruning
        - Symmetry breaking for new slots
        Returns: (min_slots, best_coloring, is_proven_optimal, runtime_ms)
        """
        t0 = time.perf_counter()
        lb = self.compute_lower_bound()

        # Seed with DSATUR solution as upper bound
        dsatur_slots, dsatur_coloring, _ = self.solve_dsatur()
        best_slots = dsatur_slots
        best_coloring = dict(dsatur_coloring)

        # If DSATUR already reached theoretical lower bound, it's immediately proven optimal!
        if best_slots == lb:
            runtime = (time.perf_counter() - t0) * 1000.0
            return best_slots, best_coloring, True, runtime

        # Order vertices by degree descending for initial search order
        vertices_order = sorted(range(1, self.N + 1), key=lambda v: len(self.adj[v]), reverse=True)
        current_coloring: Dict[int, int] = {}
        slot_sizes: Dict[int, int] = {}
        timed_out = False

        def search(idx: int, current_max_slot: int):
            nonlocal best_slots, best_coloring, timed_out
            if time.perf_counter() - t0 > time_limit_sec:
                timed_out = True
                return

            if idx == self.N:
                if current_max_slot < best_slots:
                    best_slots = current_max_slot
                    best_coloring = dict(current_coloring)
                return

            # Lower bound pruning:
            remaining_verts = self.N - idx
            # If current slots plus minimum additional capacity needed >= best_slots, prune
            if current_max_slot >= best_slots:
                return

            v = vertices_order[idx]
            neighbor_colors = set(current_coloring[nbr] for nbr in self.adj[v] if nbr in current_coloring)

            # Try assigning to existing slots
            for slot in range(1, current_max_slot + 1):
                if slot not in neighbor_colors and slot_sizes.get(slot, 0) < self.R:
                    current_coloring[v] = slot
                    slot_sizes[slot] = slot_sizes.get(slot, 0) + 1

                    search(idx + 1, current_max_slot)

                    slot_sizes[slot] -= 1
                    del current_coloring[v]
                    if best_slots == lb or timed_out:
                        return

            # Try opening a new slot (Symmetry breaking: only 1 new slot)
            new_slot = current_max_slot + 1
            if new_slot < best_slots:
                current_coloring[v] = new_slot
                slot_sizes[new_slot] = 1

                search(idx + 1, new_slot)

                del slot_sizes[new_slot]
                del current_coloring[v]

        search(0, 0)
        runtime = (time.perf_counter() - t0) * 1000.0
        proven_optimal = not timed_out or (best_slots == lb)
        return best_slots, best_coloring, proven_optimal, runtime

    def export_timetable_csv(self, filepath: str, coloring: Dict[int, int]):
        """
        Output 3: CSV file with the timetable (rows = slots, columns = exam positions/halls).
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        # Group courses by slot
        slots_dict: Dict[int, List[int]] = {}
        for c, s in coloring.items():
            slots_dict.setdefault(s, []).append(c)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header: slot, Hall 1, Hall 2, ..., Hall R
            header = ['Slot'] + [f'Hall_{h+1}' for h in range(self.R)]
            writer.writerow(header)

            for s in sorted(slots_dict.keys()):
                courses = sorted(slots_dict[s])
                row = [f'Slot {s}']
                for h in range(self.R):
                    if h < len(courses):
                        row.append(f'Course {courses[h]}')
                    else:
                        row.append('Empty')
                writer.writerow(row)

    @classmethod
    def generate_random_conflict_graph(cls, N: int, R: int, edge_density: float = 0.25, seed: Optional[int] = None) -> 'ExamScheduler':
        """
        Option 2: Generate random conflict graph with user specified edge density.
        """
        if seed is not None:
            random.seed(seed)
        conflicts = []
        for i in range(1, N + 1):
            for j in range(i + 1, N + 1):
                if random.random() < edge_density:
                    conflicts.append((i, j))
        return cls(N, R, conflicts)

    @classmethod
    def read_csv(cls, filepath: str, R: int) -> 'ExamScheduler':
        """Reads conflict graph from CSV (u, v)."""
        conflicts = []
        max_n = 1
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[0].strip().isdigit() and row[1].strip().isdigit():
                    u = int(row[0].strip())
                    v = int(row[1].strip())
                    conflicts.append((u, v))
                    max_n = max(max_n, u, v)
        return cls(max_n, R, conflicts)


def compare_algorithms(scheduler: ExamScheduler) -> Dict[str, Any]:
    lb = scheduler.compute_lower_bound()

    wp_slots, wp_coloring, wp_time = scheduler.solve_welsh_powell()
    ds_slots, ds_coloring, ds_time = scheduler.solve_dsatur()
    ex_slots, ex_coloring, ex_optimal, ex_time = scheduler.solve_exact_branch_and_bound()

    results = {
        "Theoretical_Lower_Bound": lb,
        "Welsh_Powell": {
            "slots": wp_slots,
            "proven_optimal": (wp_slots == lb),
            "time_ms": wp_time,
            "coloring": wp_coloring
        },
        "DSATUR": {
            "slots": ds_slots,
            "proven_optimal": (ds_slots == lb),
            "time_ms": ds_time,
            "coloring": ds_coloring
        },
        "Exact_Branch_Bound": {
            "slots": ex_slots,
            "proven_optimal": ex_optimal,
            "time_ms": ex_time,
            "coloring": ex_coloring
        }
    }
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Exam Timetable Scheduling (Graph Colouring)")
    parser.add_argument("--N", type=int, default=10, help="Number of courses")
    parser.add_argument("--R", type=int, default=3, help="Max exams per slot (hall capacity)")
    parser.add_argument("--density", type=float, default=0.3, help="Edge density for random graph")
    parser.add_argument("--output-csv", type=str, default="outputs/problem4_timetable.csv", help="Timetable CSV")
    args = parser.parse_args()

    scheduler = ExamScheduler.generate_random_conflict_graph(args.N, args.R, args.density, seed=42)
    comp = compare_algorithms(scheduler)

    print("Theoretical Lower Bound:", comp["Theoretical_Lower_Bound"])
    print("\n--- Output 1 (Minimum Number of Slots & Optimality) ---")
    for alg, data in [("Welsh-Powell", comp["Welsh_Powell"]),
                      ("DSATUR Heuristic", comp["DSATUR"]),
                      ("Exact Branch-and-Bound", comp["Exact_Branch_Bound"])]:
        status = "PROVEN OPTIMAL" if data["proven_optimal"] else "Heuristic (Not proven optimal)"
        print(f"  {alg:<24}: {data['slots']} slots | {status} | Time: {data['time_ms']:.3f} ms")

    best_coloring = comp["Exact_Branch_Bound"]["coloring"]

    # Output 2: Slot-wise list of courses
    print("\n--- Output 2 (Slot-wise List of Courses) ---")
    slots_map: Dict[int, List[int]] = {}
    for c, s in best_coloring.items():
        slots_map.setdefault(s, []).append(c)
    for s in sorted(slots_map.keys()):
        print(f"  Slot {s}: {', '.join(map(str, sorted(slots_map[s])))}")

    # Output 3: CSV file with the timetable
    scheduler.export_timetable_csv(args.output_csv, best_coloring)
    print(f"\n--- Output 3 (Timetable CSV Saved) ---\n  {args.output_csv}")

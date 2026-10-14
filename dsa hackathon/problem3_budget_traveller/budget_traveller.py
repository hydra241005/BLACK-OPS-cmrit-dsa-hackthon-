"""
Problem 3: Budget Traveller with Coupons
Solves minimum cost to travel from city 1 to city N with at most K stops and C discount coupons.
A coupon halves flight price (floor(p/2)). At most one coupon per flight.
Uses Multi-dimensional Layered Dynamic Programming / State-Space Dijkstra.
"""

import sys
import os
import csv
import heapq
import random
from typing import List, Tuple, Optional, Dict, Any


class FlightEdge:
    def __init__(self, u: int, v: int, price: int):
        self.u = u
        self.v = v
        self.price = price

    def __repr__(self):
        return f"({self.u}->{self.v}, p={self.price})"


class BudgetTraveller:
    def __init__(self, N: int, K: int, C: int, edges: List[Tuple[int, int, int]]):
        self.N = N
        self.K = K
        self.C = C
        self.edges = [FlightEdge(u, v, p) for u, v, p in edges]
        self.adj: Dict[int, List[Tuple[int, int]]] = {i: [] for i in range(1, N + 1)}
        for e in self.edges:
            self.adj[e.u].append((e.v, e.price))

    def solve(self) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Computes minimum cost to reach N from 1 with <= K stops (<= K+1 edges) and <= C coupons.
        Returns: (min_cost, path_details)
        where path_details is a list of steps: [{'from': u, 'to': v, 'orig_price': p, 'coupon': bool, 'cost': paid}]
        If unreachable, returns (-1, [])
        """
        max_edges = self.K + 1
        # dp[e][u][c] = minimum cost to reach city u using exactly e edges and c coupons
        # To reconstruct path, store parent: parent[e][u][c] = (prev_u, prev_c, orig_price, coupon_used)
        INF = float('inf')
        dp = [[[INF] * (self.C + 1) for _ in range(self.N + 1)] for _ in range(max_edges + 1)]
        parent = [[[None] * (self.C + 1) for _ in range(self.N + 1)] for _ in range(max_edges + 1)]

        dp[0][1][0] = 0

        for e in range(max_edges):
            for u in range(1, self.N + 1):
                for c in range(self.C + 1):
                    current_cost = dp[e][u][c]
                    if current_cost == INF:
                        continue

                    for v, price in self.adj[u]:
                        # 1. No coupon
                        no_coupon_cost = current_cost + price
                        if no_coupon_cost < dp[e + 1][v][c]:
                            dp[e + 1][v][c] = no_coupon_cost
                            parent[e + 1][v][c] = (u, c, price, False)

                        # 2. With coupon (if available)
                        if c < self.C:
                            discounted_price = price // 2
                            coupon_cost = current_cost + discounted_price
                            if coupon_cost < dp[e + 1][v][c + 1]:
                                dp[e + 1][v][c + 1] = coupon_cost
                                parent[e + 1][v][c + 1] = (u, c, price, True)

        # Find best cost to reach destination city N
        best_cost = INF
        best_e = -1
        best_c = -1

        for e in range(1, max_edges + 1):
            for c in range(self.C + 1):
                if dp[e][self.N][c] < best_cost:
                    best_cost = dp[e][self.N][c]
                    best_e = e
                    best_c = c

        if best_cost == INF:
            return -1, []

        # Reconstruct path
        path_details = []
        curr_e = best_e
        curr_u = self.N
        curr_c = best_c

        while curr_e > 0:
            prev_info = parent[curr_e][curr_u][curr_c]
            if prev_info is None:
                break
            prev_u, prev_c, orig_price, used_coupon = prev_info
            paid = (orig_price // 2) if used_coupon else orig_price
            path_details.append({
                'from': prev_u,
                'to': curr_u,
                'orig_price': orig_price,
                'coupon': used_coupon,
                'paid': paid
            })
            curr_u = prev_u
            curr_c = prev_c
            curr_e -= 1

        path_details.reverse()
        return best_cost, path_details

    def export_graph_csv(self, filepath: str, path_details: List[Dict[str, Any]]):
        """
        Output 2: CSV file of the graph with the path marked with 'x's
        (also indicate the flights on which coupons were used).
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Map edges to path step
        # Since multigraph can exist, track (u, v) in path
        path_edges = {}
        for idx, step in enumerate(path_details):
            key = (step['from'], step['to'])
            path_edges[key] = step

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['from_city', 'to_city', 'price', 'on_path', 'coupon_used', 'effective_price', 'step_number'])
            for edge in self.edges:
                key = (edge.u, edge.v)
                if key in path_edges and path_edges[key]['orig_price'] == edge.price:
                    step = path_edges[key]
                    writer.writerow([
                        edge.u, edge.v, edge.price, 'x',
                        'YES' if step['coupon'] else 'NO',
                        step['paid'],
                        path_details.index(step) + 1
                    ])
                    # Remove once matched to handle multigraph duplicates
                    del path_edges[key]
                else:
                    writer.writerow([edge.u, edge.v, edge.price, '', 'NO', edge.price, ''])

    @classmethod
    def read_csv(cls, filepath: str, K: int, C: int) -> 'BudgetTraveller':
        """
        Option 2: Read input graph from a CSV file.
        Format expected: u, v, price (or with header)
        """
        edges = []
        max_city = 1
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or not row[0].strip().isdigit():
                    continue
                u = int(row[0].strip())
                v = int(row[1].strip())
                p = int(row[2].strip())
                edges.append((u, v, p))
                max_city = max(max_city, u, v)
        return cls(max_city, K, C, edges)

    @classmethod
    def generate_random_graph(cls, N: int, K: int, C: int, edge_density: float = 0.35, seed: Optional[int] = None) -> 'BudgetTraveller':
        """
        Option 3: Generate a valid graph with user specified K and C,
        guaranteeing at least one path from 1 to N with <= K stops.
        """
        if seed is not None:
            random.seed(seed)

        edges = []
        # 1. Create guaranteed path from 1 to N with <= K stops (length between 1 and K+1)
        path_len = min(K + 1, N - 1)
        if path_len < 1:
            path_len = 1
        
        # Pick intermediate cities
        intermediate_pool = list(range(2, N))
        random.shuffle(intermediate_pool)
        chosen_intermediates = intermediate_pool[:path_len - 1]
        spine = [1] + chosen_intermediates + [N]

        for i in range(len(spine) - 1):
            u = spine[i]
            v = spine[i + 1]
            p = random.randint(50, 800)
            edges.append((u, v, p))

        # 2. Add random other edges
        existing = set((u, v) for u, v, _ in edges)
        for u in range(1, N + 1):
            for v in range(1, N + 1):
                if u != v and (u, v) not in existing:
                    if random.random() < edge_density:
                        p = random.randint(50, 1000)
                        edges.append((u, v, p))
                        existing.add((u, v))

        return cls(N, K, C, edges)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Budget Traveller with Coupons")
    parser.add_argument("--N", type=int, default=7, help="Number of cities")
    parser.add_argument("--K", type=int, default=3, help="Max stops")
    parser.add_argument("--C", type=int, default=2, help="Number of discount coupons")
    parser.add_argument("--csv", type=str, default="", help="CSV file input")
    parser.add_argument("--generate", action="store_true", help="Generate valid random graph")
    parser.add_argument("--output-csv", type=str, default="outputs/problem3_marked_flights.csv", help="Output CSV")
    args = parser.parse_args()

    if args.csv:
        traveller = BudgetTraveller.read_csv(args.csv, args.K, args.C)
    elif args.generate:
        traveller = BudgetTraveller.generate_random_graph(args.N, args.K, args.C, seed=42)
    else:
        # Sample graph
        sample_edges = [
            (1, 2, 200), (1, 3, 500), (2, 3, 100), (2, 4, 300),
            (3, 4, 150), (4, 5, 400), (3, 5, 600), (2, 5, 900)
        ]
        traveller = BudgetTraveller(N=5, K=2, C=1, edges=sample_edges)

    cost, path = traveller.solve()
    print("Output 1 (Minimum Cost):", cost)
    if cost != -1:
        print("Path taken:")
        for idx, step in enumerate(path):
            coupon_str = f" [Coupon Applied! Price: {step['orig_price']} -> {step['paid']}]" if step['coupon'] else f" [Price: {step['paid']}]"
            print(f"  Step {idx+1}: City {step['from']} -> City {step['to']}{coupon_str}")
        traveller.export_graph_csv(args.output_csv, path)
        print(f"Output 2 (Marked CSV saved to): {args.output_csv}")
    else:
        print("No route found from city 1 to city N within constraints.")

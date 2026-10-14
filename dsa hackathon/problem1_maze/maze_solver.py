"""
Problem 1: Maze with Keys and Doors
Solves the shortest path from S to E in an NxN grid with up to T (1 <= T <= 6) keys and doors.
Uses State-Space Breadth-First Search (BFS) with bitmasking.
"""

import sys
import os
import csv
import random
from collections import deque
from typing import List, Tuple, Optional, Dict, Set


class MazeSolver:
    def __init__(self, grid: List[List[str]], T: int = 6):
        self.grid = [list(row) for row in grid]
        self.N = len(grid)
        self.T = T
        self.start_pos = None
        self.exit_pos = None
        self._find_endpoints()

    def _find_endpoints(self):
        for r in range(self.N):
            for c in range(len(self.grid[r])):
                val = self.grid[r][c].strip()
                if val == 'S':
                    self.start_pos = (r, c)
                elif val == 'E':
                    self.exit_pos = (r, c)

    def solve(self) -> Tuple[int, List[Tuple[int, int, int]], Optional[List[List[str]]]]:
        """
        Runs BFS on state space (row, col, key_mask).
        Returns:
            (shortest_path_length, path_states, marked_grid)
            If no path exists, returns (-1, [], None)
        """
        if not self.start_pos or not self.exit_pos:
            return -1, [], None

        sr, sc = self.start_pos
        er, ec = self.exit_pos

        if sr == er and sc == ec:
            marked = [row[:] for row in self.grid]
            marked[sr][sc] = 'x(S)'
            return 0, [(sr, sc, 0)], marked

        # Queue stores: (row, col, mask)
        queue = deque([(sr, sc, 0)])
        visited = set([(sr, sc, 0)])
        parent: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}

        reached_state = None

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            r, c, mask = queue.popleft()

            if (r, c) == (er, ec):
                reached_state = (r, c, mask)
                break

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.N and 0 <= nc < len(self.grid[nr]):
                    cell = self.grid[nr][nc].strip()
                    if cell == '#':
                        continue  # Wall

                    new_mask = mask
                    # Check door 'A'-'F'
                    if 'A' <= cell <= 'F':
                        door_idx = ord(cell) - ord('A')
                        if door_idx < self.T:
                            if not (mask & (1 << door_idx)):
                                continue  # Do not have required key
                    # Check key 'a'-'f'
                    elif 'a' <= cell <= 'f':
                        key_idx = ord(cell) - ord('a')
                        if key_idx < self.T:
                            new_mask = mask | (1 << key_idx)

                    state = (nr, nc, new_mask)
                    if state not in visited:
                        visited.add(state)
                        parent[state] = (r, c, mask)
                        queue.append(state)

        if reached_state is None:
            return -1, [], None

        # Reconstruct path
        curr = reached_state
        path = []
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append((sr, sc, 0))
        path.reverse()

        shortest_len = len(path) - 1

        # Build marked grid for Output 2
        # Requirements: path marked with 'x's; keys picked up and doors opened must still be identifiable
        marked_grid = [row[:] for row in self.grid]
        path_coords = set((r, c) for r, c, _ in path)

        for r, c, m in path:
            orig = self.grid[r][c].strip()
            if orig == 'S':
                marked_grid[r][c] = 'S'
            elif orig == 'E':
                marked_grid[r][c] = 'E'
            elif 'a' <= orig <= 'f':
                marked_grid[r][c] = f"x({orig})"  # Key picked up, clearly identifiable
            elif 'A' <= orig <= 'F':
                marked_grid[r][c] = f"x({orig})"  # Door opened, clearly identifiable
            else:
                marked_grid[r][c] = 'x'

        return shortest_len, path, marked_grid

    @staticmethod
    def read_csv(filepath: str) -> Tuple[List[List[str]], int]:
        """Reads maze from CSV file."""
        grid = []
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    grid.append([cell.strip() for cell in row])
        
        # Infer T by inspecting keys/doors
        max_t = 1
        for row in grid:
            for cell in row:
                c = cell.strip()
                if len(c) == 1:
                    if 'a' <= c <= 'f':
                        max_t = max(max_t, ord(c) - ord('a') + 1)
                    elif 'A' <= c <= 'F':
                        max_t = max(max_t, ord(c) - ord('A') + 1)
        return grid, min(max_t, 6)

    @staticmethod
    def write_csv(filepath: str, grid: List[List[str]]):
        """Writes maze grid to CSV file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in grid:
                writer.writerow(row)

    @classmethod
    def generate_random_maze(cls, N: int, T: int, seed: Optional[int] = None) -> 'MazeSolver':
        """
        Generates a valid NxN maze with T keys and T doors with at least one solvable path.
        Partitions the grid into T+1 stages using barrier walls with a single Door choke-point,
        placing matching keys in preceding chambers, guaranteeing doors must be opened.
        """
        if seed is not None:
            random.seed(seed)

        assert 4 <= N <= 100, "N must be between 4 and 100"
        assert 1 <= T <= 6, "T must be between 1 and 6"

        grid = [['.' for _ in range(N)] for _ in range(N)]
        section_width = max(2, N // (T + 1))
        door_positions = []
        key_positions = []

        for i in range(T):
            wall_col = min((i + 1) * section_width, N - 2)
            for r in range(N):
                grid[r][wall_col] = '#'
            door_row = random.randint(1, N - 2)
            grid[door_row][wall_col] = chr(ord('A') + i)
            door_positions.append((door_row, wall_col))

            min_col = 0 if i == 0 else (i * section_width) + 1
            max_col = wall_col - 1
            key_r = random.randint(0, N - 1)
            key_c = random.randint(min_col, max(min_col, max_col))
            if key_r == 0 and key_c == 0:
                key_r = 1
            grid[key_r][key_c] = chr(ord('a') + i)
            key_positions.append((key_r, key_c))

        # Add random obstacles
        for r in range(N):
            for c in range(N):
                if grid[r][c] == '.' and random.random() < 0.15:
                    if not ((r == 0 and c == 0) or (r == N - 1 and c == N - 1)):
                        grid[r][c] = '#'

        grid[0][0] = 'S'
        grid[N - 1][N - 1] = 'E'

        # Clear neighbors of doors and keys inside their chamber, NEVER breaching barrier walls
        barrier_cols = set(w for _, w in door_positions)
        for pr, pc in door_positions + key_positions + [(0, 0), (N - 1, N - 1)]:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pr + dr, pc + dc
                if 0 <= nr < N and 0 <= nc < N:
                    if nc not in barrier_cols:
                        grid[nr][nc] = '.'

        solver = cls(grid, T)
        ans, _, _ = solver.solve()
        if ans != -1:
            return solver

        # Fallback guaranteed open corridor layout
        fallback_grid = [['.' for _ in range(N)] for _ in range(N)]
        fallback_grid[0][0] = 'S'
        fallback_grid[N - 1][N - 1] = 'E'
        for i in range(T):
            fallback_grid[0][i + 1] = chr(ord('a') + i)
            fallback_grid[1][i + 1] = chr(ord('A') + i)
        for c in range(T + 1, N):
            fallback_grid[1][c] = '#'
        return cls(fallback_grid, T)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maze with Keys and Doors Solver")
    parser.add_argument("--T", type=int, default=3, help="Number of distinct key/door types (1 <= T <= 6)")
    parser.add_argument("--csv", type=str, default="", help="Path to input maze CSV file")
    parser.add_argument("--generate", action="store_true", help="Generate random valid maze")
    parser.add_argument("--N", type=int, default=12, help="Grid size for generation")
    parser.add_argument("--output-csv", type=str, default="outputs/problem1_solution.csv", help="Output marked CSV file")
    args = parser.parse_args()

    if args.csv:
        grid, detected_T = MazeSolver.read_csv(args.csv)
        T = args.T if args.T else detected_T
        solver = MazeSolver(grid, T)
    elif args.generate:
        print(f"Generating valid {args.N}x{args.N} maze with T={args.T}...")
        solver = MazeSolver.generate_random_maze(args.N, args.T, seed=42)
    else:
        # Standard input interactive mode
        print("Enter T (number of distinct key/door types, 1 <= T <= 6):")
        try:
            line = input().strip()
            T = int(line) if line else 3
        except (EOFError, ValueError):
            T = 3
        print(f"Generating random solvable maze with T={T}, N=12...")
        solver = MazeSolver.generate_random_maze(12, T, seed=100)

    length, path, marked = solver.solve()
    print("Output 1 (Shortest path length):", length)

    if marked is not None:
        solver.write_csv(args.output_csv, marked)
        print(f"Output 2 (Marked maze CSV saved to): {args.output_csv}")
    else:
        print("No valid path from S to E found.")

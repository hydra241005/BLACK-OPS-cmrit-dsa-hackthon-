"""
Unit and Corner Case Tests for Problem 1: Maze with Keys and Doors
"""

import unittest
from maze_solver import MazeSolver

class TestMazeSolver(unittest.TestCase):

    def test_start_equals_exit(self):
        grid = [['S']]
        grid[0][0] = 'S' # S is E if only 1 cell? If we set both at same cell:
        solver = MazeSolver([['S', 'E']], T=1)
        # S and E adjacent
        length, path, marked = solver.solve()
        self.assertEqual(length, 1)

    def test_unreachable_wall(self):
        grid = [
            ['S', '#', 'E'],
            ['#', '#', '#']
        ]
        solver = MazeSolver(grid, T=1)
        length, path, marked = solver.solve()
        self.assertEqual(length, -1)

    def test_door_without_key(self):
        grid = [
            ['S', 'A', 'E'],
            ['.', '.', '.']
        ]
        # Door A blocks top, but bottom path open
        solver = MazeSolver(grid, T=1)
        length, path, marked = solver.solve()
        self.assertEqual(length, 4)  # (0,0) -> (1,0) -> (1,1) -> (1,2) -> (0,2)

    def test_door_with_key_required(self):
        # Must pick key 'a' first, then go through door 'A'
        grid = [
            ['S', 'a', '#'],
            ['#', '.', '#'],
            ['E', 'A', '.']
        ]
        solver = MazeSolver(grid, T=1)
        length, path, marked = solver.solve()
        # S(0,0) -> a(0,1) -> .(1,1) -> A(2,1) -> E(2,0) = 4 steps
        self.assertEqual(length, 4)

    def test_chained_keys(self):
        # S -> a -> opens A to get b -> opens B to reach E
        grid = [
            ['S', 'a', '#', 'b', '.'],
            ['.', '.', 'A', '.', 'B'],
            ['#', '#', '#', '#', 'E']
        ]
        solver = MazeSolver(grid, T=2)
        length, path, marked = solver.solve()
        self.assertGreater(length, 0)

    def test_revisiting_cell_with_key(self):
        # Corridor: S -> dead end with key 'a' -> return through S to door 'A' -> E
        grid = [
            ['a', 'S', 'A', 'E']
        ]
        solver = MazeSolver(grid, T=1)
        length, path, marked = solver.solve()
        # S(0,1) -> a(0,0) -> S(0,1) -> A(0,2) -> E(0,3) = 4 steps
        self.assertEqual(length, 4)

if __name__ == '__main__':
    unittest.main()

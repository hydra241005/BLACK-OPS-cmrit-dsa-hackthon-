"""
Unit and Corner Case Tests for Problem 4: Exam Timetable Scheduling
"""

import unittest
import math
from exam_scheduler import ExamScheduler, compare_algorithms

class TestExamScheduler(unittest.TestCase):

    def test_no_conflicts(self):
        # 6 courses, no conflicts, R = 2 -> Exactly ceil(6 / 2) = 3 slots
        scheduler = ExamScheduler(N=6, R=2, conflicts=[])
        res = compare_algorithms(scheduler)
        self.assertEqual(res["Exact_Branch_Bound"]["slots"], 3)
        self.assertTrue(res["Exact_Branch_Bound"]["proven_optimal"])

    def test_complete_graph(self):
        # Complete graph K_4: all pairs conflict -> Exactly 4 slots, regardless of R
        conflicts = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        scheduler = ExamScheduler(N=4, R=3, conflicts=conflicts)
        res = compare_algorithms(scheduler)
        self.assertEqual(res["Exact_Branch_Bound"]["slots"], 4)
        self.assertTrue(res["Exact_Branch_Bound"]["proven_optimal"])

    def test_capacity_one(self):
        # R = 1 -> Each hall holds only 1 exam -> N slots always required
        scheduler = ExamScheduler(N=5, R=1, conflicts=[(1, 2)])
        res = compare_algorithms(scheduler)
        self.assertEqual(res["Exact_Branch_Bound"]["slots"], 5)

    def test_bipartite_graph(self):
        # Bipartite with 4 vertices: (1, 3), (1, 4), (2, 3), (2, 4). R = 2
        # Can be colored with 2 slots: {1, 2} in slot 1, {3, 4} in slot 2.
        conflicts = [(1, 3), (1, 4), (2, 3), (2, 4)]
        scheduler = ExamScheduler(N=4, R=2, conflicts=conflicts)
        res = compare_algorithms(scheduler)
        self.assertEqual(res["Exact_Branch_Bound"]["slots"], 2)

    def test_star_graph(self):
        # Node 1 connected to 2, 3, 4, 5. N=5, R=2
        # Node 1 takes 1 slot. Nodes 2, 3, 4, 5 can share slots with capacity 2 -> ceil(4/2) = 2 slots
        # Total = 1 + 2 = 3 slots.
        conflicts = [(1, 2), (1, 3), (1, 4), (1, 5)]
        scheduler = ExamScheduler(N=5, R=2, conflicts=conflicts)
        res = compare_algorithms(scheduler)
        self.assertEqual(res["Exact_Branch_Bound"]["slots"], 3)

    def test_proven_optimal_flag(self):
        scheduler = ExamScheduler.generate_random_conflict_graph(8, 2, 0.3, seed=123)
        res = compare_algorithms(scheduler)
        self.assertTrue(res["Exact_Branch_Bound"]["proven_optimal"])


if __name__ == '__main__':
    unittest.main()

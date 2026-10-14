"""
Unit and Corner Case Tests for Problem 2: Closest Pair of Points
Tests:
1. N < 2 (handling gracefully)
2. N = 2 (base case)
3. Duplicate points (distance = 0.000000)
4. Collinear points (horizontal line, vertical line, diagonal line)
5. Points sharing same x or y coordinate
6. Agreement between Brute-Force and Divide-and-Conquer on random sets
"""

import unittest
import math
from closest_pair import (
    closest_pair_brute_force, closest_pair_divide_and_conquer, generate_random_points
)

class TestClosestPair(unittest.TestCase):

    def test_n_less_than_two(self):
        # N = 0
        bf_d, p1, p2 = closest_pair_brute_force([])
        dc_d, _, _, _ = closest_pair_divide_and_conquer([])
        self.assertEqual(bf_d, float('inf'))
        self.assertEqual(dc_d, float('inf'))

        # N = 1
        bf_d, p1, p2 = closest_pair_brute_force([(10.0, 20.0)])
        dc_d, _, _, _ = closest_pair_divide_and_conquer([(10.0, 20.0)])
        self.assertEqual(bf_d, float('inf'))
        self.assertEqual(dc_d, float('inf'))

    def test_n_equals_two(self):
        pts = [(1.0, 2.0), (4.0, 6.0)]
        expected_d = 5.0  # sqrt(3^2 + 4^2) = 5
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, expected_d, places=6)
        self.assertAlmostEqual(dc_d, expected_d, places=6)

    def test_duplicate_points(self):
        pts = [(5.0, 5.0), (1.0, 1.0), (5.0, 5.0), (10.0, 10.0)]
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, 0.0, places=6)
        self.assertAlmostEqual(dc_d, 0.0, places=6)

    def test_horizontal_collinear_points(self):
        pts = [(float(x), 5.0) for x in [10, 20, 25, 27, 40, 60]]
        # Closest is 25 and 27 -> dist = 2.0
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, 2.0, places=6)
        self.assertAlmostEqual(dc_d, 2.0, places=6)

    def test_vertical_collinear_points(self):
        pts = [(3.0, float(y)) for y in [100, 50, 48.5, 20, 0]]
        # Closest is 50 and 48.5 -> dist = 1.5
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, 1.5, places=6)
        self.assertAlmostEqual(dc_d, 1.5, places=6)

    def test_diagonal_collinear_points(self):
        pts = [(float(i), float(i)) for i in [0, 10, 12, 30, 45]]
        # Closest is (10, 10) and (12, 12) -> dist = sqrt(2^2 + 2^2) = sqrt(8)
        expected = math.sqrt(8)
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, expected, places=6)
        self.assertAlmostEqual(dc_d, expected, places=6)

    def test_shared_coordinates(self):
        # Multiple points sharing either same x or same y
        pts = [(1.0, 2.0), (1.0, 5.0), (1.0, 10.0), (3.0, 2.0), (8.0, 2.0)]
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, dc_d, places=6)

    def test_random_large_agreement(self):
        pts = generate_random_points(300, seed=999)
        bf_d, _, _ = closest_pair_brute_force(pts)
        dc_d, _, _, _ = closest_pair_divide_and_conquer(pts)
        self.assertAlmostEqual(bf_d, dc_d, places=6)


if __name__ == '__main__':
    unittest.main()

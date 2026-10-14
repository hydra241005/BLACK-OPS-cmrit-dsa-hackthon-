"""
Unit and Corner Case Tests for Problem 3: Budget Traveller with Coupons
"""

import unittest
from budget_traveller import BudgetTraveller

class TestBudgetTraveller(unittest.TestCase):

    def test_unreachable_stops(self):
        # 1 -> 2 -> 3 -> 4, but K=1 allows at most 1 stop (2 edges: 1->2->3 max)
        edges = [(1, 2, 100), (2, 3, 100), (3, 4, 100)]
        traveller = BudgetTraveller(N=4, K=1, C=0, edges=edges)
        cost, path = traveller.solve()
        self.assertEqual(cost, -1)

    def test_direct_flight_no_stop(self):
        edges = [(1, 4, 1000), (1, 2, 100), (2, 4, 100)]
        # K=0 allows only direct flight (0 intermediate stops)
        traveller = BudgetTraveller(N=4, K=0, C=1, edges=edges)
        cost, path = traveller.solve()
        # Coupon halves 1000 to 500
        self.assertEqual(cost, 500)
        self.assertEqual(len(path), 1)

    def test_coupon_selection_optimal(self):
        # 1 -> 2 ($100) -> 3 ($800) -> 4 ($50)
        # K=2, C=1 -> Coupon should be applied on $800 flight (becomes $400)
        # Total cost: 100 + 400 + 50 = 550
        edges = [(1, 2, 100), (2, 3, 800), (3, 4, 50)]
        traveller = BudgetTraveller(N=4, K=2, C=1, edges=edges)
        cost, path = traveller.solve()
        self.assertEqual(cost, 550)
        # Verify coupon was applied on flight 2 -> 3
        coupon_applied_flight = [s for s in path if s['coupon']]
        self.assertEqual(len(coupon_applied_flight), 1)
        self.assertEqual(coupon_applied_flight[0]['from'], 2)
        self.assertEqual(coupon_applied_flight[0]['to'], 3)

    def test_zero_cost_edge(self):
        edges = [(1, 2, 0), (2, 3, 0)]
        traveller = BudgetTraveller(N=3, K=2, C=2, edges=edges)
        cost, path = traveller.solve()
        self.assertEqual(cost, 0)

    def test_cycle_in_graph(self):
        # Cycle 1 -> 2 -> 1, but destination is 3
        edges = [(1, 2, 50), (2, 1, 50), (2, 3, 300)]
        traveller = BudgetTraveller(N=3, K=2, C=1, edges=edges)
        cost, path = traveller.solve()
        # 1 -> 2 (50) -> 3 (300 -> 150) = 200
        self.assertEqual(cost, 200)

    def test_more_coupons_than_flights(self):
        edges = [(1, 2, 301), (2, 3, 501)]
        # K=3, C=5 (more than 2 flights)
        # Prices halved: 301 // 2 = 150, 501 // 2 = 250 -> Total = 400
        traveller = BudgetTraveller(N=3, K=3, C=5, edges=edges)
        cost, path = traveller.solve()
        self.assertEqual(cost, 400)


if __name__ == '__main__':
    unittest.main()

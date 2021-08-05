from unittest import TestCase
from unittest.mock import patch

from tspvisual.solvers.ga import GASolver
from tspvisual.tsp import TSP, Path


class TestGASolver(TestCase):

    def setUp(self):
        tsp = TSP()
        self.gasolver = GASolver()
        self.gasolver.tsp = tsp

        self.data = [
            ([0, 4, 1, 2, 6, 12, 3, 7, 14, 9, 10, 11, 5, 13, 8],
             [5, 3, 0, 13, 10, 7, 11, 12, 8, 6, 9, 4, 1, 2, 14], (6, 9)),

            ([8, 4, 7, 3, 6, 2, 5, 1, 9, 0],
             [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], (3, 7)),

            ([0, 1, 2, 3, 4, 5, 6, 7, 8],
             [4, 2, 5, 6, 7, 0, 1, 8, 3], (2, 5)),

            ([0, 1, 2, 3, 4, 5, 6],
             [3, 1, 6, 0, 2, 4, 5], (1, 3)),

            ([0, 2, 4, 3, 5, 1, 0],
             [0, 4, 1, 2, 3, 5, 0], (3, 5))
        ]

    def test_crossover_ox(self):
        expected = [
            [0, 13, 10, 11, 12, 8, 6, 3, 7, 14, 9, 4, 1, 2, 5],
            [0, 4, 7, 3, 6, 2, 5, 1, 8, 9],
            [0, 2, 3, 4, 5, 1, 8, 6, 7],
            [0, 1, 2, 3, 4, 5, 6],
            [0, 4, 2, 3, 5, 1, 0]
        ]

        self._test_crossover(self.gasolver._crossover_ox, expected)

    def test_crossover_pmx(self):
        expected = [
            [5, 11, 0, 13, 10, 12, 3, 7, 14, 9, 6, 4, 1, 2, 8],
            [0, 7, 4, 3, 6, 2, 5, 1, 8, 9],
            [7, 0, 2, 3, 4, 5, 1, 8, 6],
            [0, 1, 2, 3, 6, 4, 5],
            [0, 4, 2, 3, 5, 1, 0]
        ]

        self._test_crossover(self.gasolver._crossover_pmx, expected)

    def test_crossover_nwox(self):
        expected = [
            [5, 0, 13, 10, 11, 12, 3, 7, 14, 9, 8, 6, 4, 1, 2],
            [0, 4, 7, 3, 6, 2, 5, 1, 8, 9],
            [6, 7, 2, 3, 4, 5, 0, 1, 8],
            [6, 1, 2, 3, 0, 4, 5],
            [0, 4, 2, 3, 5, 1, 0]
        ]

        self._test_crossover(self.gasolver._crossover_nwox, expected)

    @patch('tspvisual.tsp.TSP.path_dist', return_value=0)
    @patch('tspvisual.solvers.ga.GASolver._rand_subpath')
    def _test_crossover(self, fun, expected, mock_rand_subpath, mock_dist):
        for (p1, p2, subpath), exp in zip(self.data, expected):
            with self.subTest(p1=p1, p2=p2, subpath=subpath):
                mock_rand_subpath.return_value = subpath
                self.gasolver.tsp.specification['DIMENSION'] = len(p1) - 1
                parent1 = Path(path=p1)
                parent2 = Path(path=p2)
                child = fun(parent1, parent2)
                self.assertListEqual(child.path, exp)

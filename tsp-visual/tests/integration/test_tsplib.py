import os
import unittest
from tempfile import NamedTemporaryFile

from tspvisual.tsplib import TSPLib, TSPLibTour


class TestTSPLib(unittest.TestCase):

    def setUp(self):
        self.tsplib = TSPLib()

    def test_specification(self):
        expected = {
            'NAME': 'gr17',
            'TYPE': 'TSP',
            'COMMENT': '17-city problem (Groetschel)',
            'DIMENSION': 17,
            'EDGE_WEIGHT_TYPE': 'EXPLICIT',
            'EDGE_WEIGHT_FORMAT': 'LOWER_DIAG_ROW'
        }

        self.tsplib.load('tests/fixtures/gr17.tsp')
        self.assertDictEqual(self.tsplib.specification, expected)

    def test_coords(self):
        expected = [
            (16.47, 96.10),
            (16.47, 94.44),
            (20.09, 92.54),
            (22.39, 93.37),
            (25.23, 97.24),
            (22.00, 96.05),
            (20.47, 97.02),
            (17.20, 96.29),
            (16.30, 97.38),
            (14.05, 98.12),
            (16.53, 97.38),
            (21.52, 95.59),
            (19.41, 97.13),
            (20.09, 94.55)
        ]

        self.tsplib.load('tests/fixtures/burma14.tsp')
        self.assertListEqual(self.tsplib.coords, expected)

    def test_display(self):
        expected = [
            (1150, 1760), (630, 1660), (40, 2090), (750, 1100),
            (750, 2030), (1030, 2070), (1650, 650), (1490, 1630),
            (790, 2260), (710, 1310), (840, 550), (1170, 2300),
            (970, 1340), (510, 700), (750, 900), (1280, 1200),
            (230, 590), (460, 860), (1040, 950), (590, 1390),
            (830, 1770), (490, 500), (1840, 1240), (1260, 1500),
            (1280, 790), (490, 2130), (1460, 1420), (1260, 1910), (360, 1980)
        ]

        self.tsplib.load('tests/fixtures/bayg29.tsp')
        self.assertListEqual(self.tsplib.display, expected)

    def test_weights(self):
        expected = [
            [0, -1, -1, -1, -1, -1],
            [4,  0, -1, -1, -1, -1],
            [9,  4,  0, -1, -1, -1],
            [7,  4,  2,  0, -1, -1],
            [12, 9,  5,  5,  0, -1],
            [7,  6,  7,  5,  7,  0]
        ]

        self.tsplib.load('tests/fixtures/test6.tsp')
        self.assertListEqual(self.tsplib.weights, expected)

    def test_weight_explicit(self):
        data = [
            (9, 6, 444),
            (12, 1, 567),
            (1, 12, 567),
            (0, 0, 0),
            (16, 16, 0),
            (0, 15, 246)
        ]

        self.tsplib.load('tests/fixtures/gr17.tsp')

        for i, j, expected in data:
            with self.subTest(i=i, j=j):
                result = self.tsplib.weight(i, j)
                self.assertEqual(result, expected)

    def test_weight_euc_2d(self):
        data = [
            (3, 2, 2),
            (2, 3, 2),
            (0, 0, 0),
            (5, 5, 0),
            (4, 0, 12),
            (3, 1, 4)
        ]

        self.tsplib.load('tests/fixtures/test6.tsp')

        for i, j, expected in data:
            with self.subTest(i=i, j=j):
                result = self.tsplib.weight(i, j)
                self.assertEqual(result, expected)


class TestTSPLibTour(unittest.TestCase):

    def setUp(self):
        self.tsplibtour = TSPLibTour()
        self.expected_spec = {
            'NAME': 'bayg29.opt.tour',
            'COMMENT': 'Optimum solution of bayg29',
            'TYPE': 'TOUR',
            'DIMENSION': 29,
        }
        self.expected_tour = [1, 28, 6, 12, 9, 26, 3, 29, 5, 21, 2, 20, 10, 4,
                              15, 18, 14, 17, 22, 11, 19, 25, 7, 23, 8, 27, 16,
                              13, 24]

    def test_specification(self):
        self.tsplibtour.load('tests/fixtures/bayg29.opt.tour')
        self.assertDictEqual(self.tsplibtour.specification, self.expected_spec)

    def test_tour(self):
        self.tsplibtour.load('tests/fixtures/bayg29.opt.tour')
        self.assertListEqual(self.tsplibtour.tour, self.expected_tour)

    def test_exception(self):
        with self.assertRaises(TypeError):
            self.tsplibtour.load('tests/fixtures/bayg29.tsp')

    def test_write(self):
        tmp = NamedTemporaryFile(delete=False, mode='w')
        tmp.close()
        self.tsplibtour = TSPLibTour()
        self.tsplibtour.specification = self.expected_spec
        self.tsplibtour.tour = self.expected_tour
        self.tsplibtour.write(tmp.name)
        result = self._cmp_files(tmp.name, 'tests/fixtures/bayg29.opt.tour')
        self.assertTrue(result)
        os.unlink(tmp.name)

    @staticmethod
    def _cmp_files(file1, file2):
        """Compare files ignoring differences in newline character.

        Used for the same result between OS'es.
        """

        l1 = l2 = True
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            while l1 and l2:
                l1 = f1.readline()
                l2 = f2.readline()
                if l1 != l2:
                    return False
        return True

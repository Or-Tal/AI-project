import numpy as np
from noa_kirel.solver import Solver
from noa_kirel.constants import BF_SOL
from itertools import product
from time import time


class BruteForceSolver(Solver):
    """
    baseline greedy solver
    """
    def __init__(self, n_cities: int, costs: dict, revenues: dict, tour_length: int):
        super().__init__()
        self.cities = np.arange(n_cities)
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)
        self.name = BF_SOL
        self.best_score = np.NINF
        self.best_sol = None
        self.counter = 1
        self.start_time = 0

    def score(self, sol: np.ndarray):
        """
        calculate the score for a given solution
        """
        acc_score = list()
        prev = -1
        visited = set()
        for i, x in enumerate(sol):
            r = self.rev[(x, i)] if x not in visited else 0
            acc_score.append(r - self.costs[(prev, x)])
            prev = x
            visited.add(x)
        return sum(acc_score)

    def product(self, repeat):

        def single_cell():
            for i in self.cities:
                yield i

        generators = [single_cell() for _ in range(repeat)]
        while True:
            yield [generators[i].__next__() for i in range(repeat)]

    def solve(self):
        self.best_score = np.NINF
        self.best_sol = None
        self.counter = 1
        self.start_time = time()

        for sol in product(self.cities, repeat=self.n):
            sol = np.array(sol)
            tmp_score = self.score(sol)
            if tmp_score > self.best_score:
                self.best_sol = sol
                self.best_score = tmp_score
            yield sol, tmp_score, time() - self.start_time, self.best_sol, self.best_score, self.counter / self.n

        return self.best_sol, self.best_score, time() - self.start_time, self.best_sol, self.best_score, 1


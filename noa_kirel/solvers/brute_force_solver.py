import numpy as np
from noa_kirel.solver import Solver
from itertools import product
from noa_kirel.constants import BF_SOL
from time import time


class BruteForceSolver(Solver):
    """
    baseline greedy solver
    """
    def __init__(self, n_cities: int, costs: dict, revenues: dict, tour_length: int, ver: int):
        super().__init__()
        self.cities = np.arange(n_cities)
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)
        self.name = BF_SOL
        self.ver = ver

    def score(self, sol: np.ndarray):
        """
        calculate the score for a given solution
        """
        acc_score = 0
        prev = -1
        visited = set()
        if self.ver == 2:
            preprev = -1
        for i, x in enumerate(sol):
            r = self.rev[(x, i)] if x not in visited else 0
            acc_score += r - self.costs[(prev, x), i] - (self.costs[(preprev, prev, x), i] if self.ver == 2 else 0)
            if self.ver == 2:
                preprev = prev
            prev = x
            visited.add(x)
        return acc_score

    def solve(self):
        start_time = time()
        best_score = np.NINF
        best_sol = None
        counter = 0
        for sol in product(self.cities, repeat=self.n):
            sol = np.array(sol)
            tmp_score = self.score(sol)
            if tmp_score > best_score:
                best_sol = sol
                best_score = tmp_score
            counter = counter + 1
            yield sol, tmp_score, time() - start_time, best_sol, \
                  best_score,  counter/len(self.cities) ** self.n

        return best_sol, best_score, time() - start_time, best_sol, best_score, 1


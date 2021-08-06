import numpy as np
from typing import List, Dict
from solver import Solver
from itertools import permutations


class Optimal(Solver):
    """
    baseline greedy solver
    """
    def __init__(self,
                 cities,
                 costs,
                 revenues,
                 tour_length):
        self.cities = set(range(cities))
        self.costs = costs
        self.rev = revenues
        self.n = tour_length

    def score(self, sol: np.ndarray):
        """
        calculate the score for a given solution
        """
        acc_score = 0
        prev = -1
        for x in sol:
            acc_score += self.rev[x] - self.costs[(prev, x)]
            prev = x
        return acc_score

    def solve(self):
        best_score = np.NINF
        best_sol = None
        for sol in permutations(self.cities, r=int(self.n)):
            sol = np.array(sol)
            tmp_score = self.score(sol)
            if tmp_score > best_score:
                best_sol = sol
                best_score = tmp_score
        return best_sol




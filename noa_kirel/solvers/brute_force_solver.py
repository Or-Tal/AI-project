import numpy as np
from noa_kirel.solver import Solver
from itertools import permutations


class BruteForceSolver(Solver):
    """
    baseline greedy solver
    """
    def __init__(self, n_cities: int, costs: dict, revenues: dict, tour_length: int):
        super().__init__()
        self.cities = set(range(n_cities))
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)
        self.name = "brute_force"

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

    def solve(self, ret_generator=True):
        best_score = np.NINF
        best_sol = None
        scores = []
        for sol in permutations(self.cities, r=self.n):
            sol = np.array(sol)
            tmp_score = self.score(sol)
            if tmp_score > best_score:
                best_sol = sol
                best_score = tmp_score
            if ret_generator:
                yield sol, tmp_score
            scores.append(best_score)
        return best_sol, best_score if ret_generator else scores





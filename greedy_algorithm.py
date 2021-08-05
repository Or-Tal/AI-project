import numpy as np
from typing import List, Dict
from solver import Solver
from copy import deepcopy


class Greedy(Solver):
    """
    baseline greedy solver
    """
    def __init__(self, n_cities: int,
                 costs: Dict[(int, int)],
                 revenues: Dict[int],
                 tour_length: int):
        self.cities = set(range(n_cities))
        self.costs = costs
        self.rev = revenues
        self.n = tour_length

    def solve(self):
        sol = list()
        opts = deepcopy(self.cities)

        for i in range(self.n):

            # re-init loop vars
            best_score = np.NINF
            best_candidate = None

            # find the best next candidate
            prev = -1 if len(sol) == 0 else sol[-1]
            for x in opts:
                tmp_score = self.rev[x] - self.costs[(prev, x)]
                if tmp_score > best_score:
                    best_score = tmp_score
                    best_candidate = x

            # adds best candidate to solution
            sol.append(best_candidate)
            opts = opts - {best_candidate}

        # return greedy solution
        return sol



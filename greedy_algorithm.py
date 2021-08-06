import numpy as np
from typing import List, Dict
from solver_old import Solver
from copy import deepcopy


class Greedy(Solver):
    """
    baseline greedy solver
    """
    def __init__(self,
                 n_cities,
                 costs,
                 revenues,
                 tour_length):
        self.cities = set(range(n_cities))
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)

    def solve(self):
        sol = list()
        opts = deepcopy(self.cities)
        scores = [0]

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
            scores.append(scores[-1] + best_score)

        # return greedy solution
        return sol, scores[1:]



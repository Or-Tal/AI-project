import numpy as np
from noa_kirel.solver import Solver
from copy import deepcopy


class GreedySolver(Solver):
    """
    baseline greedy solver
    """
    def __init__(self,
                 n_cities: int,
                 costs: dict,
                 revenues: dict,
                 tour_length: int):
        super().__init__()
        self.cities = np.arange(n_cities)
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)
        self.name = "greedy"

    def score(self, sol):
        res = 0
        prev = -1
        seen = set()
        for x in sol:
            r = self.rev[x] if x not in seen else 0
            res += r - self.costs[(prev, x)]
            prev = x
        return res

    def solve(self, ret_generator=True):
        sol = list()
        opts = self.cities
        scores = list()
        for i in range(self.n):

            # re-init loop vars
            best_score = np.NINF
            best_candidate = None

            # find the best next candidate
            prev = -1 if len(sol) == 0 else sol[-1]
            for x in opts:
                tmp_score = self.rev[x, i] - self.costs[(prev, x)]
                if tmp_score > best_score:
                    best_score = tmp_score
                    best_candidate = x

            # adds best candidate to solution
            sol.append(best_candidate)
            scores.append(self.score(sol))

            # generator case
            if ret_generator:
                yield sol, scores[-1]

        # return greedy solution
        return sol, scores[-1] if ret_generator else scores[1:]


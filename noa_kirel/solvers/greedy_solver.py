import numpy as np
from noa_kirel.solver import Solver
from time import time


class GreedySolver(Solver):
    """
    baseline greedy solver
    """
    def __init__(self,
                 n_cities: int,
                 costs: dict,
                 revenues: dict,
                 tour_length: int,
                 ver=1):
        super().__init__()
        self.cities = np.arange(n_cities)
        self.costs = costs
        self.rev = revenues
        self.n = int(tour_length)
        self.name = "greedy"
        self.ver = 0

    def score(self, sol):
        res = 0
        visited = set()
        prev = -1
        if self.ver == 2:
            preprev = -1
        for i, x in enumerate(sol):
            rev = self.rev[(x, i)] if x not in visited else 0
            res += (rev - self.costs[(prev, x), i] - (self.costs[(preprev, prev, x), i] if self.ver == 2 else 0))
            visited.add(x)
            if self.ver == 2:
                preprev = prev
            prev = x

        return res

    def solve(self):
        start_time = time()
        sol = list()
        opts = self.cities
        score = 0
        visited = set()
        for i in range(self.n):

            # re-init loop vars
            best_score = np.NINF
            best_candidate = None

            # find the best next candidate
            if self.ver == 2:
                preprev = -1 if len(sol) < 2 else sol[-2]
            prev = -1 if len(sol) == 0 else sol[-1]
            for x in opts:
                r = self.rev[x, i] if x not in visited else 0
                tmp_score = r - self.costs[(prev, x), i] - (self.costs[(preprev, prev, x), i] if self.ver == 2 else 0)
                if tmp_score > best_score:
                    best_score = tmp_score
                    best_candidate = x

            # adds best candidate to solution
            visited.add(best_candidate)
            sol.append(best_candidate)
            score = self.score(sol)

            # generator case
            yield sol, score, time() - start_time, sol, score, sol, score, (i + 1) / self.n

        # return greedy solution
        return sol, score, time() - start_time, sol, score, 1


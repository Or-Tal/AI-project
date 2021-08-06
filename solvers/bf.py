from copy import deepcopy
from itertools import permutations
from math import factorial

from tspvisual.solver import Solver, SolverState
from tspvisual.tsp import TSP, Path


class BFSolver(Solver):
    """Brute force solver for TSP.
    """

    name = 'Brute Force'
    properties = []

    def __init__(self):
        super().__init__()

    def solve(self, tsp, steps=True):
        # Make sure given argument is of correct type
        if not isinstance(tsp, TSP):
            raise TypeError('solve() argument has to be of type \'TSP\'')
        self.tsp = tsp

        # Create starting path: 0, 1, 2, ..., 0, this path will be permuted
        path = Path(self.tsp.dimension + 1)
        path.path = list(range(len(path) - 1)) + [0]
        path.distance = self.tsp.path_dist(path)
        # Best path
        min_path = deepcopy(path)
        # Create permutations skipping the last stop (return to 0)
        perms = permutations(path.path[1:-1])

        if steps:
            total = factorial(self.tsp.dimension - 1)

        # Start the timer
        self._start_timer()

        # Loop through all permutations to find the shortest path
        for i, perm in enumerate(perms):
            path.path = [0] + list(perm) + [0]
            path.distance = self.tsp.path_dist(path)

            if path.distance < min_path.distance:
                min_path = deepcopy(path)

            if steps:
                # Need to use deepcopies because object could change before the
                # reference will be used
                yield SolverState(self._time(), i / total, deepcopy(path),
                                  deepcopy(min_path))

        yield SolverState(self._time(), 1, None, min_path, True)

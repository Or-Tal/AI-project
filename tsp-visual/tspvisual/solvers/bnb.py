from copy import deepcopy
from math import factorial, inf

from tspvisual.solver import Solver, SolverState
from tspvisual.tsp import TSP, Path


class BnBSolver(Solver):
    """Branch-and-bound solver for TSP
    """

    name = 'Branch and Bound'
    properties = []

    def __init__(self):
        super().__init__()

    def solve(self, tsp, steps=True):
        # Make sure given argument is of correct type
        if not isinstance(tsp, TSP):
            raise TypeError('solve() argument has to be of type \'TSP\'')
        self.tsp = tsp

        # Total and current number of steps for calculating progress
        if steps:
            total = factorial(self.tsp.dimension - 1) * 2
            current = 0

        # Working path
        path = Path(self.tsp.dimension + 1)
        path[-1] = 0
        # Minimal path and distance
        min_path = Path(self.tsp.dimension + 1)
        min_path.distance = inf
        # Nodes list (used as a stack)
        stack = []

        # Add starting city (0) to the stack
        stack.append((0, 0, 0))

        # Start the timer
        self._start_timer()

        while len(stack) > 0:
            # Increment step counter
            if steps:
                current += 1

            # Get node from the top of the stack
            cur_node = stack.pop()
            city, dist, level = cur_node
            # Update current path with this node
            path[level] = city
            # This is the level of all children of this node
            next_level = level + 1

            # If it's the last level of the tree
            if level == self.tsp.dimension - 1:
                path.distance = dist + self.tsp.dist(city, 0)
                # Yield the current state
                if steps:
                    yield SolverState(self._time(), current / total,
                                      deepcopy(path), deepcopy(min_path))
                # Distance of full path with return to 0
                # Keep it if it's better than the current minimum
                if path.distance < min_path.distance:
                    min_path = deepcopy(path)
                else:
                    continue

            # Iterate through all cities
            for i in range(self.tsp.dimension):
                # Skip current city itself, its predecessors and starting city
                if i == city or path.in_path(i, next_level) or i == 0:
                    continue

                # Skip this node if its distance is greater than min path
                next_dist = dist + self.tsp.dist(city, i)
                if next_dist >= min_path.distance:
                    continue

                # If it's valid node push it onto stack
                stack.append((i, next_dist, next_level))

        yield SolverState(self._time(), 1, None, deepcopy(min_path), True)

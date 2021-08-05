from copy import deepcopy
from math import exp, log
from random import randint, random

from tspvisual.solver import Property, Solver, SolverState
from tspvisual.tsp import TSP, Neighbourhood, Path


class SASolver(Solver):
    """Simulated annealing solver for TSP.
    """

    name = 'Simulated Annealing'
    properties = [
        Property('Initial temperature', 'init_temp', float, 1000),
        Property('End temperature', 'end_temp', float, 0.01),
        Property('Cooling rate', 'cooling_rate', float, 0.001),
        Property('Neighbourhood', 'neighbourhood', Neighbourhood, 'INVERT'),
        Property('Run time [ms]', 'run_time', int, 0)
    ]

    def __init__(self):
        super().__init__()
        self.init_temp = 1000
        self.end_temp = 0.01
        self.cooling_rate = 0.001
        self.neighbourhood = Neighbourhood.INVERT
        self.run_time = 0

    def solve(self, tsp, steps=True):
        # Make sure given argument is of correct type
        if not isinstance(tsp, TSP):
            raise TypeError('solve() argument has to be of type \'TSP\'')
        self.tsp = tsp

        # Total number of iterations or time for calculating progress
        if steps:
            current = 0
            iters = log(self.end_temp / self.init_temp, 1 - self.cooling_rate)
            total = self.run_time if self.run_time else iters

        # Start with random path
        cur_path = Path(self.tsp.dimension + 1)
        cur_path.path = list(range(len(cur_path) - 1)) + [0]
        cur_path.shuffle(1, -1)
        cur_path.distance = self.tsp.path_dist(cur_path)

        # And set it as current minimum
        min_path = deepcopy(cur_path)

        # Start the timer
        self._start_timer()

        # Init temperature
        temp = self.init_temp
        # Repeat as long as system temperature is higher than minimum
        while True:
            # Update iteration counter ro time counterif running in step mode
            if steps:
                current = self._time_ms() if self.run_time else current + 1

            # Get random neighbour of current path
            new_path = self._rand_neigh(cur_path)

            # Difference between current and new path
            delta_dist = new_path.distance - cur_path.distance

            # If it's shorter or equal
            if delta_dist <= 0:
                # If it's shorter set it as current minimum
                if new_path.distance < min_path.distance:
                    min_path = deepcopy(new_path)
                # Set new path as current path
                cur_path = deepcopy(new_path)
            elif exp(-delta_dist / temp) > random():
                # If path is longer accept it with random probability
                cur_path = deepcopy(new_path)

            # Cooling down
            temp *= 1 - self.cooling_rate

            # Terminate search after reaching end temperature
            if not self.run_time and temp < self.end_temp:
                break

            # Terminate search after exceeding specified runtime
            # We use `total` to not have to convert to nanoseconds every time
            if self.run_time and self._time_ms() >= self.run_time:
                break

            # Report current solver state
            if steps:
                yield SolverState(self._time(), current / total,
                                  deepcopy(new_path), deepcopy(min_path))

        yield SolverState(self._time(), 1, None, deepcopy(min_path), True)

    def _rand_neigh(self, path):
        """Generates random neighbour of a given path.

        :param Path path: Path to generate neighbour of.
        :return: Random neighbour.
        :rtype: Path
        """

        i = j = randint(1, self.tsp.dimension - 1)

        while i == j:
            j = randint(1, self.tsp.dimension - 1)

        neighbour = deepcopy(path)
        neighbour.move(self.neighbourhood, i, j)
        neighbour.distance = self.tsp.path_dist(neighbour)

        return neighbour

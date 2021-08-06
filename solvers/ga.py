from copy import deepcopy
from enum import Enum
from random import randint, random

from tspvisual.solver import Property, Solver, SolverState
from tspvisual.tsp import TSP, Neighbourhood, Path

Crossover = Enum('Crossover', 'OX PMX NWOX')


class GASolver(Solver):
    """Genetic Algorithm solver for TSP.
    """

    name = 'Genetic Algorithm'
    properties = [
        Property('Population size', 'population_size', int, 80),
        Property('Elite size', 'elite_size', int, 30),
        Property('Mutation rate', 'mutation_rate', float, 0.05),
        Property('Generations', 'generations', int, 2000),
        Property('Run time [ms]', 'run_time', int, 0),
        Property('Crossover type', 'crossover_type', Crossover, 'NWOX'),
        Property('Mutation type', 'mutation_type', Neighbourhood,
                 'INVERT')
    ]

    def __init__(self):
        super().__init__()
        self.population_size = 80
        self.elite_size = 30
        self.mutation_rate = 0.05
        self.generations = 2000
        self.run_time = 0
        self.crossover_type = Crossover.NWOX
        self.mutation_type = Neighbourhood.INVERT
        self._population = []
        self._mating_pool = []

    def solve(self, tsp, steps=True):
        # Make sure given argument is of correct type
        if not isinstance(tsp, TSP):
            raise TypeError('solve() argument has to be of type \'TSP\'')
        self.tsp = tsp

        # Init population and the best path
        self._init_population()
        min_path = self._population[0]

        # Total number of iterations or runtime
        if steps:
            total = self.generations if not self.run_time else self.run_time

        # Number of evolved generations
        evolved = 0

        # Start the timer
        self._start_timer()

        # Repeat until end conditions are met
        while True:
            # Selection, breeding and mutation
            self._selection()
            self._breeding()
            self._mutation()

            # Sort the population
            self._population.sort(key=lambda p: p.distance)

            # If the best path in this generation is better than overall
            # minimum set it as the current minimum
            if self._population[0].distance < min_path.distance:
                min_path = deepcopy(self._population[0])

            # Increment generation counter
            evolved += 1

            if steps:
                current = evolved if not self.run_time else self._time_ms()
                yield SolverState(self._time(), current / total,
                                  deepcopy(self._population[0]),
                                  deepcopy(min_path))

            # Terminate evolution after reaching generations limit
            if not self.run_time and evolved >= self.generations:
                break

            # Terminate search after exceeding specified runtime
            if self.run_time and self._time_ms() >= self.run_time:
                break

        yield SolverState(self._time(), 1, None, deepcopy(min_path), True)

    def _init_population(self):
        """Initializes population by creating specified number of random paths.
        """

        self._population.clear()
        for _ in range(self.population_size):
            path = Path(self.tsp.dimension + 1)
            path.path = list(range(self.tsp.dimension)) + [0]
            path.shuffle(1, -1)
            path.distance = self.tsp.path_dist(path)
            self._population.append(path)

        self._population.sort(key=lambda p: p.distance)

    def _selection(self):
        """Fills mating pool with individuals chosen using elitism
        and Roulette Wheel Selection.
        """

        self._mating_pool.clear()

        # Calculate population distances cumulative sums and pick probabilty
        tot_sum = 0
        cum_sums = []
        for i in range(len(self._population)):
            tot_sum += self._population[i].distance
            cum_sums.append(tot_sum)
        probs = [(cs / tot_sum) for cs in cum_sums]

        # For each free place in mating pool
        for _ in range(self.population_size - self.elite_size):
            # Spin the roulette
            roulette = random()

            # Find first path with probability higher than roulette number
            for i, prob in enumerate(probs):
                if roulette <= prob:
                    self._mating_pool.append(self._population[i])
                    break

    def _crossover(self, parent1, parent2):
        """Performs currently selected crossover on two given paths.

        :param Path parent1: First parent path.
        :param Path parent2: Second parent path.
        :return: Child path.
        :rtype: Path
        """

        crossovers = {
            Crossover.OX: self._crossover_ox,
            Crossover.PMX: self._crossover_pmx,
            Crossover.NWOX: self._crossover_nwox
        }

        return crossovers[self.crossover_type](parent1, parent2)

    def _crossover_ox(self, parent1, parent2):
        """Performs order crossover to create a child path from two given
        parent paths.

        :param Path parent1: First parent path.
        :param Path parent2: Second parent path.
        :return: Child path.
        :rtype: Path
        """

        # Initial child path
        child = Path(len(parent1))

        # Copy random subpath from parent 1 to child
        start, end = self._rand_subpath()
        subpath = parent1.path[start:end+1]
        tmp = parent2.path

        # Rotate tmp with pivot in the end + 1
        tmp = tmp[end+1:] + tmp[:end+1]
        # Remove cities found in subpath from parent 2
        tmp = list(filter(lambda x: x not in subpath, tmp))

        # Join subpath and tmp to form a child
        child.path = subpath + tmp

        # Rotate the path so it always starts at 0
        last_zero_idx = len(child) - child[::-1].index(0) - 1
        child.path = child[last_zero_idx:] + child[:last_zero_idx]

        child.distance = self.tsp.path_dist(child)
        return child

    def _crossover_pmx(self, parent1, parent2):
        """Performs partially matched crossover to create a child path from two
        given parent paths.

        :param Path parent1: First parent path.
        :param Path parent2: Second parent path.
        :return: Child path.
        :rtype: Path
        """

        # Starting path
        child = Path(len(parent1))

        # Copy random subpath from parent 1 to child and create mapping
        start, end = self._rand_subpath()
        child[start:end+1] = parent1[start:end+1]

        # Create mapping
        mapping = dict(zip(parent1[start:end+1], parent2[start:end+1]))

        # Copy stops from parent 2 to child using mapping if necessary
        child_pos = 0
        while child_pos < self.tsp.dimension + 1:
            # Skip already filled subpath
            if start <= child_pos <= end:
                child_pos = end + 1
                continue

            # Get city at current stop in parent 2
            city = parent2[child_pos]

            # Trace mapping if it exists
            while city in mapping:
                city = mapping[city]

            # Set stop in the child path
            child[child_pos] = city
            child_pos += 1

        child.distance = self.tsp.path_dist(child)
        return child

    def _crossover_nwox(self, parent1, parent2):
        """Performs non wrapping order crossover to create a child path from
        two given parents paths.

        :param Path parent1: First parent path.
        :param Path parent2: Second parent path.
        :return: Child path.
        :rtype: Path
        """

        # Initial child path
        child = Path(self.tsp.dimension + 1)

        # Copy random subpath from parent 1 to child
        start, end = self._rand_subpath()
        child[start:end+1] = parent1[start:end+1]

        # Fill in child's empty slots with cities from parent 2 in order
        parent_pos = child_pos = 0
        while parent_pos < self.tsp.dimension + 1:
            # Skip already filled subpath
            if start <= child_pos <= end:
                child_pos = end + 1
                continue

            # Get city from parent path
            city = parent2[parent_pos]

            if child.in_path(city):
                # If this city is already in child path then go to next one
                parent_pos += 1
                continue
            else:
                # Otherwise add it to child path and go to next
                child[child_pos] = city
                child_pos += 1
                parent_pos += 1

        # Add return to 0 if last stop is empty
        child[-1] = child[-1] if child[-1] != -1 else 0

        child.distance = self.tsp.path_dist(child)
        return child

    def _breeding(self):
        """Creates a new population by crossing over each individual in mating
        pool with the next one in order.
        """

        # Clear population with retaining the elite
        self._population = self._population[:self.elite_size]

        # Crossover individuals with the next one
        for i in range(self.population_size - self.elite_size - 1):
            child = self._crossover(self._mating_pool[i],
                                    self._mating_pool[i+1])
            self._population.append(child)

        # Wrap around and crossover last individual with the first one
        child = self._crossover(self._mating_pool[-1], self._mating_pool[0])
        self._population.append(child)

    def _mutation(self):
        """Mutates population using currently set mutation rate
        and mutation type.
        """

        for path in self._population[self.elite_size:]:
            if random() <= self.mutation_rate:
                i, j = self._rand_subpath()
                path.move(self.mutation_type, i, j)
                path.distance = self.tsp.path_dist(path)

    def _rand_subpath(self):
        """Randomly chooses two stops in path creating random subpath.

        :return: Subpath's start and end indices.
        :rtype: tuple
        """

        i = j = randint(1, self.tsp.dimension - 1)

        while i == j:
            j = randint(1, self.tsp.dimension - 1)

        return min(i, j), max(i, j)

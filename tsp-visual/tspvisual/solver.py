import abc
import time
from collections import namedtuple

SolverState = namedtuple('SolverState', 'time progress current best final',
                         defaults=[False])

Property = namedtuple('Property', 'name field type default')


class Solver(abc.ABC):
    """TSP solver base class. Defines interface for getting solver name and
    properties as well as solving TSP instances.
    """

    def __init__(self):
        self._start_time = 0

    @property
    @abc.abstractmethod
    def name(self):
        """Returns name of the solver.

        :return: Name.
        :rtype: string
        """

        raise NotImplementedError('Solvers must have name property.')

    @property
    @abc.abstractmethod
    def properties(self):
        """Returns list of solver properties.

        :return: List of properties.
        :rtype: list
        """

        raise NotImplementedError('Solvers must implement properties method.')

    @abc.abstractmethod
    def solve(self, tsp, steps=True):
        """Solves given instance and returns a generator of SolverState
        objects. If `steps` argument is set to True solver state is generated
        with each algorithm step, otherwise just the final one is
        returned.

        :param TSP tsp: TSP instance to solve.
        :param bool full: Whether to retur all intermediate states.
        :return: Generator of consecutive states.
        :rtype: generator
        """

        raise NotImplementedError('Solvers must implement solve method.')

    def result(self, tsp):
        """Solves given instance and returns the result.

        This function is just a wrapper around `solve` to avoid returning
        a generator when the only thing needed is a result.

        :param TSP tsp: TSP instance to solve.
        :return: Best found path.
        :rtype: Path
        """

        return next(self.solve(tsp, steps=False)).best

    def _start_timer(self):
        """Stores current time for further calculations of run time.
        """

        self._start_time = time.perf_counter_ns()

    def _time(self):
        """Calculates time elapsed since calling `_start_timer`.
        """

        return time.perf_counter_ns() - self._start_time

    def _time_ms(self):
        """Returns time elapsed since calling `_start_timer` in milliseconds.
        """

        return self._time() // (10 ** 6)

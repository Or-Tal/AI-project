import abc
import time


class Solver(abc.ABC):
    """TSP solver base class. Defines interface for getting solver name and
    properties as well as solving TSP instances.
    """

    def __init__(self):
        self._start_time = 0

    @abc.abstractmethod
    def solve(self, ret_generator=True):
        """
        main call method to solve a given initialized tsp problem.
        :param ret_generator: boolean flag, if True this method should return a generator to iterate over generated
                              (state, score) during the algorithm's iterations.
                              if false, this returns the best solution and a list of accumulated best scores.
        """

        raise NotImplementedError('Solvers must implement solve method.')

    def _start_timer(self):
        """
        Stores current time for further calculations of run time.
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

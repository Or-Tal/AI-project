import numpy as np

INITIAL_CITY = '_'


def get_fitness_function(transfer_costs, city_rev):
    """
    Fitness function factory
    :param transfer_costs: python dictionary - {(src, dst) : transfer cost}
    :param city_rev: python dictionary - {city : revenue}
    :return: a fitness function according to the revenue and cost function
    """
    def fitness_function(solution):
        """
        Fitness function for the genetic algorithm for the singer's tour, taking in consideration the city's revenue
        and the transfer cost from city to city
        :param solution: ndarray representing the tour
        :return: total revenue from the solution tour
        """
        if not solution:
            return 0

        visited = set()
        fitness = 0
        prev = INITIAL_CITY

        for cur_city in solution:
            cur_rev = city_rev[cur_city] if cur_city not in visited else 0
            fitness += cur_rev - transfer_costs[(prev, cur_city)]
            prev = cur_city
            visited.add(cur_city)

        return fitness
    return fitness_function


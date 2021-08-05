import numpy as np
from solver import Solver

POPULATION_SIZE = 0
PATH_SIZE = 0
EVEN = 2
ODD = 1


class GeneticSolver(Solver):
    def __init__(self, fitness_func, partition_func, city_selection_func, score_threshold):
        Solver.__init__(self)
        self.__fitness_func = fitness_func
        self.__partition_func = partition_func
        self.__city_selection_func = city_selection_func
        self.__threshold = score_threshold


# def genetic_algorithm(population, fitness_func, partition_func,
#                       city_selection_func, threshold):
    def genetic_algorithm(self):
        """
        produce the new generation of states by selection, crossover and mutation
        :param population: 2d nd-array of randomly generated states
        :param fitness_func: giving higher values for better states
        :return: 2d nd-array of new population
        """
        population = self.get_init_population()
        best_solution = None
        population_size = len(population)
        new_population = np.empty((population_size, PATH_SIZE))
        step = 0
        while best_solution is None:
            weights = selection_func(population, self.__fitness_func)  # weights is np.array
            num_of_genes = len(population) - EVEN
            if population_size % 2 == 0:
                np.insert(new_population, population[np.argmax(weights)], population[np.argmax(weights)])
            else:
                np.insert(new_population, population[np.argmax(weights)])
                num_of_genes = len(population) - ODD

            for gen in range(num_of_genes // 2):
                x, y = random_select(population, weights)
                x_new, y_new = cross_over(x, y, self.__partition_func)
                np.insert(new_population, x_new, y_new)
            new_population = mutation(new_population, self.__city_selection_func)
            step += 1
            best_solution = self.__get_best_solution(new_population, self.__fitness_func)

        return new_population


    def __get_best_solution(self, population, step):
        pass


    def get_init_population(self):
        pass


def random_select(population, weight):
    return 0, 1



def selection_func(population, fitness_func):
    return 0


def cross_over(x, y, partition_func):
    return 0, 1


def p_func(population_size):
    """
    decides the point of merge between two vectors
    :param population_size: int
    :return: bin vec
    """
    return 0


def mutation(new_population, city_selection_func):
    for gen in new_population:
        idx_to_be_mutated = choose_idx_to_be_mutated(gen)



    return 0



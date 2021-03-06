import numpy as np
from scipy.special import softmax
from noa_kirel.solver import Solver
from time import time

INITIAL_CITY = -1


class GeneticSolver(Solver):
    """
    A class for a Genetic algorithm solver for the tour planning problem
    """

    def __init__(self,
                 num_cities,
                 population_size,
                 tour_length,
                 partition_func,
                 city_selection_func,
                 score_threshold,
                 steps_threshold,
                 mutate_p,
                 elitism_factor,
                 transfer_costs,
                 city_revs,
                 ver=1):
        """
        Initializer for the genetic solver
        :param num_cities: number of possible cities for performing
        :param population_size: number of solutions to hold at a time
        :param tour_length: length of the tour
        :param partition_func: function for partitioning solutions in the crossover phase
        :param city_selection_func: function for selecting a city for injecting to a mutation
        :param score_threshold: threshold which above it a solution is considered as 'good enough'
        :param steps_threshold: max number of iterations for the algorithm
        :param mutate_p: probability for mutation generation
        :param elitism_factor: number of gens to pass as is each iteration
        :param transfer_costs: python dictionary - {(src, dst) : transfer cost}
        :param city_revs: python dictionary - {city : revenue}
        """

        Solver.__init__(self)
        self.__num_cities = num_cities
        self.__population_size = population_size
        self.__tour_length = tour_length
        # self.__fitness_func = self.__get_fitness_function(transfer_costs, city_revs, ver)
        self.__partition_func = partition_func
        self.__city_selection_func = city_selection_func
        self.__score_threshold = score_threshold
        self.__steps_threshold = steps_threshold
        self.__mutate_p = mutate_p
        self.__elitism_factor = elitism_factor
        self.__initial_population = self.__get_init_population()
        self.name = "genetic"
        self.__ver = ver
        self.__city_rev = city_revs
        self.__transfer_costs = transfer_costs

    def fitness_function(self, solution):
        """
        Fitness function for the genetic algorithm for the singer's tour, taking in consideration the city's revenue
        and the transfer cost from city to city
        :param solution: ndarray representing the tour
        :return: total revenue from the solution tour
        """
        if solution is None or solution.size == 0:
            return 0

        visited = set()
        fitness = 0
        if self.__ver == 2:
            preprev = INITIAL_CITY
        prev = INITIAL_CITY

        for i, cur_city in enumerate(solution):
            cur_rev = self.__city_rev[(cur_city, i)] if cur_city not in visited else 0
            fitness += (cur_rev - self.__transfer_costs[(prev, cur_city), i]
                        - (self.__transfer_costs[(preprev, prev, cur_city), i] if self.__ver == 2 else 0))
            if self.__ver == 2:
                preprev = prev
            prev = cur_city
            visited.add(cur_city)

        return fitness

    # @staticmethod
    # def __get_fitness_function(transfer_costs, city_rev, ver):
    #     """
    #     Fitness function factory
    #     :param transfer_costs: python dictionary - {(src, dst) : transfer cost}
    #     :param city_rev: python dictionary - {city : revenue}
    #     :return: a fitness function according to the revenue and cost function
    #     """
    #
    #     def fitness_function(solution):
    #         """
    #         Fitness function for the genetic algorithm for the singer's tour, taking in consideration the city's revenue
    #         and the transfer cost from city to city
    #         :param solution: ndarray representing the tour
    #         :return: total revenue from the solution tour
    #         """
    #         if solution is None or solution.size == 0:
    #             return 0
    #
    #         visited = set()
    #         fitness = 0
    #         if ver == 2:
    #             preprev = INITIAL_CITY
    #         prev = INITIAL_CITY
    #
    #         for i, cur_city in enumerate(solution):
    #             cur_rev = city_rev[(cur_city, i)] if cur_city not in visited else 0
    #             fitness += (cur_rev - transfer_costs[(prev, cur_city), i]
    #                         - (transfer_costs[(preprev, prev, cur_city), i] if ver == 2 else 0))
    #             if ver == 2:
    #                 preprev = prev
    #             prev = cur_city
    #             visited.add(cur_city)
    #
    #         return fitness
    #
    #     return fitness_function

    def __get_init_population(self):
        """
        Randomize an initial population for the genetic algorithm
        :return: 2d-array of the generated solutions of shape (population_size, tour_length)
        """
        return np.random.choice(np.arange(self.__num_cities), size=(self.__population_size, self.__tour_length))

    def solve(self):
        """
        Solves the tour planning using a genetic algorithm
        :return: 1d-array of the best solution found by the algorithm
        """
        start = time()
        best_solution, best_score = None, 0
        step = 1
        population = self.__initial_population
        scores = self.__get_scores(population)
        elitism_factor = self.__elitism_factor if (self.__elitism_factor + self.__population_size) % 2 == 0 \
            else self.__elitism_factor + 1
        flag = True

        while flag:
            weights = self.__selection_func(scores)  # weights is np.array
            indices = weights.argsort()[-elitism_factor:]
            new_population = np.zeros((self.__population_size, self.__tour_length), dtype=int)
            new_population[-elitism_factor:] = population[indices]

            num_of_genes = self.__population_size - elitism_factor
            for i in range(num_of_genes // 2):
                x, y = self.__random_select(population, weights)
                x_new, y_new = self.__crossover(x, y)
                new_population[i * 2:i * 2 + 2] = [x_new, y_new]

            new_population = self.__mutation(new_population)
            scores = self.__get_scores(new_population)
            flag, best_solution, best_score = self.__get_best_solution(new_population, scores, step)
            step += 1
            population = new_population
            yield best_solution, best_score, time() - start, best_solution, best_score, (step - 1) / self.__steps_threshold

        return best_solution, best_score, time() - start, best_solution, best_score, 1

    def __get_scores(self, population):
        """
        :param population: 2d-array of solutions
        :return: 1d-array of scores
        """
        return np.array([self.fitness_function(solution) for solution in population])
        # return np.array([self.__fitness_func(solution) for solution in population])

    @staticmethod
    def __selection_func(scores):
        """
        Computes probabilities for each solution in population according to its score
        :param scores: 1d-array of scores
        :return: 1d-array of the probabilities for each solution in population
        """
        normalized_scores = scores / np.max(scores)
        return softmax(normalized_scores)

    @staticmethod
    def __random_select(population, weights):
        """
        Chooses randomly a pair of solutions from populations according to weights
        :param population: 2d-array of solutions
        :param weights: 1d-array of the probabilities for each solution in population
        :return: 2d-array of the two chosen solutions
        """
        indices = np.arange(len(population))
        chosen = np.random.choice(indices, size=2, p=weights)
        return population[chosen]

    def __crossover(self, x, y):
        """
        Generates 2 new solution from crossover of x and y
        :param x: 1d-array of a solution
        :param y: 1d-array of a solution
        :return: two 1d-arrays of the new solutions
        """
        partition, opposite_partition = self.__partition_func(self.__tour_length)
        new_x, new_y = np.zeros_like(x), np.zeros_like(y)

        new_x[partition], new_y[partition] = x[partition], y[partition]
        new_x[opposite_partition], new_y[opposite_partition] = y[opposite_partition], x[opposite_partition]

        return new_x, new_y

    def __mutation(self, population):
        """
        Randomly injects mutation to some of the solutions in population
        :param population: 2d-array of solutions
        :return: 2d-array of the new, mutated solutions
        """
        idx_to_be_mutated = np.random.choice([0, 1], size=len(population), p=[1 - self.__mutate_p, self.__mutate_p])
        indices = np.argwhere(idx_to_be_mutated).flatten()
        genes_to_be_mutated = population[indices]
        for i in range(len(genes_to_be_mutated)):
            mutation_idx = np.random.randint(self.__tour_length)
            mutation_city = self.__city_selection_func(population, self.__num_cities)
            gen = genes_to_be_mutated[i]
            gen[mutation_idx] = mutation_city
            population[indices[i]] = gen
        return population

    def __get_best_solution(self, population, scores, step):
        """
        :param population: 2d-array of solutions
        :param scores: 1d-array of scores
        :param step: current step number
        :return: The best solution if its score is higher than score threshold or if passed steps threshold,
                 else None
        """
        best_solution, best_score = population[np.argmax(scores)], np.max(scores)
        flag = not (step > self.__steps_threshold or best_score >= self.__score_threshold)
        return flag, best_solution, best_score

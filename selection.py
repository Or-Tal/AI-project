import numpy as np
from scipy.special import softmax


def selection_func(population, fitness_func):
    """
    Computes probabilities for each solution in population according to its score
    :param population: 2d-array of solutions
    :param fitness_func: a score function for the solutions in population
    :return: 1d-array of the probabilities for each solution in population
    """
    scores = [fitness_func(solution) for solution in population]
    return softmax(scores)


def random_select(population, weights):
    """
    Chooses randomly a pair of solutions from populations according to weights
    :param population: 2d-array of solutions
    :param weights: 1d-array of the probabilities for each solution in population
    :return: 2d-array of the two chosen solutions
    """
    indices = np.arange(len(population))
    chosen = np.random.choice(indices, size=2, p=weights)
    return population[chosen]


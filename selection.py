from scipy.special import softmax


def selection_func(population, fitness_func):
    """
    Computes probabilities for each solution in population according to its score
    :param population: 2d ndarray of solutions
    :param fitness_func: a score function for the solutions in population
    :return: ndarray of the probabilities for each solution in population
    """
    scores = [fitness_func(solution) for solution in population]
    return softmax(scores)


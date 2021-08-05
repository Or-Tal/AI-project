import numpy as np


def continuous_partition(n):
    """
    Randomizes a partition between 2 genetic solutions
    :param n: length of a solution
    :return: a binary 1d-array representing which indices to take from the first solution to the crossover solution
    """
    slice_point = np.random.randint(n)
    indices = np.ones(n)
    indices[slice_point:] = 0
    return indices


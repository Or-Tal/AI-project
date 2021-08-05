import numpy as np


def partition_1(n):
    """
    Randomizes a continuous partition between 2 genetic solutions
    :param n: length of a solution
    :return: a binary 1d-array representing which indices to take from the first solution to the crossover solution
    """
    slice_point = np.random.randint(n)
    indices = np.ones(n)
    indices[slice_point:] = 0
    return indices


def partition_2(n):
    """
    Randomizes a non-continuous partition between 2 genetic solutions
    :param n: length of a solution
    :return: a binary 1d-array representing which indices to take from the first solution to the crossover solution
    """
    num_indices_to_flip = np.random.randint(n)
    indices_to_flip = np.random.choice(np.arange(n), size=num_indices_to_flip)
    indices = np.ones(n)
    indices[indices_to_flip] = 0
    return indices


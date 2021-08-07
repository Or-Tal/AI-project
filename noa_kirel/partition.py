import numpy as np


def partition_1(n):
    """
    Randomizes a continuous partition between 2 genetic solutions
    :param n: length of a solution
    :return: a binary 1d-array representing which indices to take from the first solution to the crossover solution
    """
    slice_point = np.random.randint(n)
    indices = np.arange(n)
    indices, opposite_indices = indices[:slice_point], indices[slice_point:]
    return indices, opposite_indices


def partition_2(n):
    """
    Randomizes a non-continuous partition between 2 genetic solutions
    :param n: length of a solution
    :return: a binary 1d-array representing which indices to take from the first solution to the crossover solution
    """
    # num_indices_to_flip = np.random.randint(n)
    # indices_to_flip = np.random.choice(np.arange(n), size=num_indices_to_flip)
    # indices = np.ones(n, dtype=int)
    # indices[indices_to_flip] = 0
    indices = sorted(np.random.randint(0, n, 2))
    return np.arange(indices[1], indices[0]), np.concatenate([np.arange(indices[1]), np.arange(indices[0], n)])


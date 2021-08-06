import numpy as np
from scipy.special import softmax


def city_selection_1(population, num_cities):
    """
    Selects a city for mutation
    :param population: 2d-array of solutions
    :param num_cities: int, number of cities
    :return: index of the city to be inserted to the mutation
    """
    cities_counter = np.bincount(population.flatten().astype(int), minlength=num_cities)
    p = softmax(1 - (cities_counter / population.size))
    chosen_city = np.random.choice(num_cities, size=1, p=p)[0]
    return chosen_city



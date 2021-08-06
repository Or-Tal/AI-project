import numpy as np
CITIES = "num_cities"
COSTS = "costs_by_city_x_city"
REV = "revenue_by_city"
GEN = "genetic"
OPT = "optimal"
GREEDY = "greedy"


def load_dset(path):
    return np.load(path, allow_pickle=True).tolist()

import numpy as np
CITIES = "num_cities"
COSTS = "costs_by_city_x_city"
REV = "revenue_by_city"
GEN = "genetic"
# todo kick out optimal and replace by brute force
OPT = "optimal"
GREEDY = "greedy"
BF_SOL = "brute_force"

# genetic ctor params for gui
POP_SIZE = "population_size"
TOUR_LEN = "tour_length"
STEPS = "generations"
MUT_RATE = "mutate_rate"
NUM_ELITE = "elitism_factor"

def load_dset(path):
    return np.load(path, allow_pickle=True).tolist()

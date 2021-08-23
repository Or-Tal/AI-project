import numpy as np
from collections import namedtuple
from noa_kirel.main import main_func
from noa_kirel.constants import *
import os


Args = namedtuple("args", ['dset_path',
                           'algorithm',
                           'partition',
                           'city_selection',
                           'p_mutation',
                           'step_th',
                           'score_th',
                           'population_size',
                           'tour_length',
                           'elitism_factor',
                           'save_name',
                           'alg_ver'])


def run_hyperparams(cur_dset_paths,
                    cur_p_mutations,
                    cur_steps_thresholds,
                    cur_score_thresholds,
                    cur_population_sizes,
                    cur_algorithms,
                    cur_tour_lengths=None,
                    cur_elitism_factors=None,
                    prefix=None,
                    ver=1):
    for path in cur_dset_paths:
        new_path = f"./datasets{'2' if ver == 2 else ''}/{path}"
        num_cities = int(path.split(sep='_')[0])
        if cur_tour_lengths is None:
            cur_tour_lengths = [3, 6]
            # cur_tour_lengths = np.linspace(3, num_cities, num_cities // 3, dtype=int)

        for i1, population_size in enumerate(cur_population_sizes):
            if cur_elitism_factors is None:
                cur_elitism_factors = [1, 3] if population_size % 2 == 1 else [2]
            for i2, elitism_factor in enumerate(cur_elitism_factors):
                if population_size <= elitism_factor:
                    continue
                for i3, p in enumerate(cur_p_mutations):
                    for i4, steps_threshold in enumerate(cur_steps_thresholds):
                        for i5, score_threshold in enumerate(cur_score_thresholds):
                            for algorithm in cur_algorithms:
                                if algorithm != GEN and (i1 != 0 or i2 != 0 or i3 != 0 or i4 != 0 or i5 != 0):
                                    continue
                                for length in cur_tour_lengths:
                                    save_name = f"{f'{prefix}/' if prefix is not None else ''}num_cities_" \
                                                f"{num_cities}_p_{p}_population_{population_size}_" \
                                                f"{algorithm}_elitism_{elitism_factor}_len_{length}"
                                    if os.path.exists(f"./results/{save_name}.png"):
                                        print(f"skipping: {save_name}")
                                        continue
                                    args = Args(new_path, algorithm, 1, 1, p,
                                                steps_threshold, score_threshold, population_size, length,
                                                elitism_factor, save_name, ver)
                                    main_func(args)


if __name__ == '__main__':
    small_dset_paths = ["9_cities.npy", "12_cities.npy", "15_cities.npy"]
    # large_dset_paths = ["50_cities.npy", "80_cities.npy",
    #                     "100_cities.npy", "150_cities.npy", "200_cities.npy", "300_cities.npy",
    #                     "400_cities.npy", "500_cities.npy"]
    large_dset_paths = ["50_cities.npy", "80_cities.npy",
                        "100_cities.npy"]
    ver = 2
    p_mutations = [0.1]
    steps_thresholds = [15000]
    score_thresholds = [np.inf]
    small_population_sizes = [7, 10, 20, 50]
    large_population_sizes = [150]
    large_tour_lengths = [30, 50]
    large_elitism_factors = [20, 30]

    run_hyperparams(small_dset_paths, p_mutations, steps_thresholds,
                    score_thresholds, small_population_sizes, [GEN, GREEDY, BF_SOL], prefix="small", ver=ver)

    run_hyperparams(large_dset_paths, p_mutations, steps_thresholds,
                    score_thresholds, large_population_sizes, [GEN, GREEDY], large_tour_lengths,
                    large_elitism_factors, prefix="large", ver=ver)


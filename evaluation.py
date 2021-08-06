import numpy as np
from collections import namedtuple
from main import main_func

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
                           'save_name'])


def run_hyperparams(cur_dset_paths,
                    cur_partitions,
                    cur_city_selections,
                    cur_p_mutations,
                    cur_steps_thresholds,
                    cur_score_thresholds,
                    cur_population_sizes,
                    cur_algorithms,
                    cur_tour_lengths=None,
                    cur_elitism_factors=None):
    for path in cur_dset_paths:
        new_path = f"./datasets/{path}"
        num_cities = int(path.split(sep='_')[0])
        if not cur_tour_lengths:
            cur_tour_lengths = np.linspace(3, num_cities, num_cities // 3, dtype=int)

        for population_size in cur_population_sizes:
            if not cur_elitism_factors:
                cur_elitism_factors = [1, 3] if population_size % 2 == 1 else [2]
            for tour_length in cur_tour_lengths:
                for elitism_factor in cur_elitism_factors:
                    if population_size <= elitism_factor:
                        continue
                    for partition in cur_partitions:
                        for city_selection in cur_city_selections:
                            for p in cur_p_mutations:
                                for steps_threshold in cur_steps_thresholds:
                                    for score_threshold in cur_score_thresholds:
                                        for algorithm in cur_algorithms:
                                            save_name = f"num_cities_{num_cities}_length_{tour_length}_partition_{1}" \
                                                        f"_city_selection_{city_selection}_p_{p}_" \
                                                        f"steps_{steps_threshold}_score_{score_thresholds}_population_" \
                                                        f"{population_size}_{algorithm}"
                                            args = Args(new_path, algorithm, partition, city_selection, p,
                                                        steps_threshold, score_threshold, population_size, tour_length,
                                                        elitism_factor, save_name)
                                            main_func(args)


if __name__ == '__main__':
    small_dset_paths = ["3_cities.npy", "6_cities.npy", "9_cities.npy", "12_cities.npy", "15_cities.npy"]
    large_dset_paths = ["50_cities.npy", "60_cities.npy", "70_cities.npy", "80_cities.npy", "90_cities.npy",
                        "100_cities.npy"]
    partitions = [1]
    city_selections = [1]
    p_mutations = [0.001, 0.01, 0.1, 0.2]
    steps_thresholds = [500, 2000]
    score_thresholds = [np.inf]
    small_population_sizes = [7, 10, 20, 50]
    large_population_sizes = [10, 30, 50, 100]
    large_tour_lengths = [10, 25, 40]
    large_elitism_factors = [2, 6, 10, 30]

    run_hyperparams(small_dset_paths, partitions, city_selections, p_mutations, steps_thresholds,
                    score_thresholds, small_population_sizes, ["genetic"])

    run_hyperparams(large_dset_paths, partitions, city_selections, p_mutations, steps_thresholds,
                    score_thresholds, large_population_sizes, ["genetic"], large_tour_lengths)


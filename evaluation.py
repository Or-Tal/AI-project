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
                           'save_name'])


def run_hyperparams(cur_dset_paths,
                    cur_partitions,
                    cur_city_selections,
                    cur_p_mutations,
                    cur_steps_thresholds,
                    cur_score_thresholds,
                    cur_population_sizes,
                    cur_algorithms,
                    cur_tour_lengths=None):
    for path in cur_dset_paths:
        new_path = f"./datasets/{path}"
        num_cities = int(path.split(sep='_')[0])
        if not cur_tour_lengths:
            cur_tour_lengths = np.linspace(3, num_cities, num_cities // 3, dtype=int)
        for tour_length in cur_tour_lengths:
            for partition in cur_partitions:
                for city_selection in cur_city_selections:
                    for p in cur_p_mutations:
                        for steps_threshold in cur_steps_thresholds:
                            for score_threshold in cur_score_thresholds:
                                for population_size in cur_population_sizes:
                                    for algorithm in cur_algorithms:
                                        save_name = f"num_cities_{num_cities}_length_{tour_length}_partition_{1}" \
                                                    f"_city_selection_{city_selection}_p_{p}_" \
                                                    f"steps_{steps_threshold}_score_{score_thresholds}_population_" \
                                                    f"{population_size}_{algorithm}"
                                        args = Args(new_path, algorithm, partition, city_selection, p,
                                                    steps_threshold, score_threshold, population_size, tour_length,
                                                    save_name)
                                        main_func(args)


if __name__ == '__main__':
    small_dset_paths = [""]
    large_dset_paths = [""]
    partitions = [1, 2]
    city_selections = [1]
    p_mutations = [0.001, 0.01, 0.1, 0.2, 0.5, 0.7, 1]
    small_steps_thresholds = [10, 20, 30]
    large_steps_thresholds = [50, 100, 300, 500, 1000]
    score_thresholds = [np.inf]
    population_sizes = [3, 5, 7]
    algorithms = ["genetic", "optimal", "greedy"]
    large_tour_lengths = [5, 10, 25, 40]

    run_hyperparams(small_dset_paths, partitions, city_selections, p_mutations, small_steps_thresholds,
                    score_thresholds, population_sizes, algorithms)
    run_hyperparams(large_dset_paths, partitions, city_selections, p_mutations, large_steps_thresholds,
                    score_thresholds, population_sizes, algorithms, large_tour_lengths)


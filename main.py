import numpy as np
import argparse
import os
import city_selection
import partition
from constants import *
from generate_dataset import main_gen_func


def load_dset(dset_path: str, a: argparse.ArgumentParser) -> object:
    """
    loads dataset from dset_path
    :return: dictionary describing the dataset
    """
    if dset_path is None:
        return main_gen_func(a)
    elif len(dset_path) < 4 or dset_path[-4:] != ".npy" or not \
            os.path.exists(dset_path):
        raise ValueError("invalid dset path was given")
    return np.load(dset_path, allow_pickle=True).tolist()


def check_args(a: argparse.ArgumentParser):
    """
    validated arguments, throws ValueError in case of invalid arguments
    :param a:
    :return:
    """
    # TODO fill
    pass


def get_solver(a):
    if a.algorithm == GREEDY:
        # TODO fill
        pass
    elif a.algorithm == OPT:
        # TODO fill
        pass
    else:
        partition_func = getattr(partition, f"partition_{a.partition}")
        city_selection_func = getattr(partition, f"city_selection_{a.city_selection}")


def main_func(a):
    """
    main function that runs the solver
    """
    dset = load_dset(a.dset_path, a)
    check_args(a)


def parse_args():
    parser = argparse.ArgumentParser()

    # global arguments
    parser.add_argument("--dset_path", required=False, help="path/to/dataset.npy\nif you wish to regenerate a dataset"
                                                            " and run using the generated don't pass anything.\n see "
                                                            "n, max_cost, max_rev, min_rev, save_path arguments")
    parser.add_argument("--algorithm", required=False, help="genetic/optimal/greedy, default=greedy", default=GREEDY)
    parser.add_argument("--partition", required=False, help="partition function version - only for genetic", default=1)
    parser.add_argument("--city_selection", required=False, help="city selection function version - only for genetic",
                        default=1)

    # genetic alg related arguments
    # -- generate dset case
    parser.add_argument("--n", default=100, help="num_of_cities - generate dset case", required=False)
    parser.add_argument("--max_cost", default=100, help="max cost for each transition - generate dset case",
                        required=False)
    parser.add_argument("--max_rev", default=300, help="max cost for each transition - generate dset case",
                        required=False)
    parser.add_argument("--min_rev", default=50, help="max cost for each transition - generate dset case",
                        required=False)
    parser.add_argument("--save_path", default=None, help="path_to_save_dir/filename.npy - generate dset case, if you "
                                                          "don't wish to save the dataset, don't specify this",
                        required=False)
    # -- hyper parameters
    parser.add_argument("--p_mutation", default=0.1, help="p in range (0,1) used as bernoulli factor for mutation "
                                                          "generation", required=False)
    parser.add_argument("--step_th", default=1e3, help="threshold for max number of generations to consider",
                        required=False)
    parser.add_argument("--score_th", default=np.inf, help="threshold for max score", required=False)
    parser.add_argument("--population_size", default=100, help="population size", required=False)
    parser.add_argument("--tour_length", default=30, help="number of tour days", required=False)

    ret = parser.parse_args()
    return ret


if __name__ == "__main__":
    args = parse_args()
    main_func(args)

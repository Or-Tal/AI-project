import argparse
import os
from noa_kirel import city_selection
from noa_kirel import partition
import pandas as pd
import matplotlib.pyplot as plt
from noa_kirel.constants import *
from noa_kirel.generate_dataset import main_gen_func
from noa_kirel.solvers.greedy_solver import GreedySolver
from noa_kirel.solvers.brute_force_solver import BruteForceSolver
from noa_kirel.solvers.genetic_solver import GeneticSolver


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


def check_args(a, dset):
    """
    validated arguments, throws ValueError in case of invalid arguments
    :param a:
    :return:
    """
    if a.algorithm == GEN:
        if a.p_mutation < 0 or a.p_mutation > 1 or \
           a.tour_length > dset[CITIES] or a.elitism_factor > a.population_size:
            raise ValueError("invalid hyper-parameters were given to genetic algorithm initializer")


def get_solver(a, dset):
    if a.algorithm == GREEDY:
        return GreedySolver(dset[CITIES], dset[COSTS], dset[REV], a.tour_length)
    elif a.algorithm == BF_SOL:
        return BruteForceSolver(dset[CITIES], dset[COSTS], dset[REV], a.tour_length)
    else:
        partition_func = getattr(partition, f"partition_{a.partition}")
        city_selection_func = getattr(city_selection, f"city_selection_{a.city_selection}")
        return GeneticSolver(dset[CITIES],
                             a.population_size,
                             a.tour_length,
                             partition_func,
                             city_selection_func,
                             a.score_th,
                             a.step_th,
                             a.p_mutation,
                             a.elitism_factor,
                             dset[COSTS],
                             dset[REV])


def save_results(sol, scores, times, a):
    if not os.path.exists("results"):
        os.mkdir("results")
    if len(a.save_name.split("/")) == 2 and not os.path.exists(f"./results/{a.save_name.split('/')[0]}"):
        os.mkdir(f"./results/{a.save_name.split('/')[0]}")

    np.save(f"./results/{a.save_name}", {"solution": sol, "scores": scores})
    df = pd.DataFrame.from_dict({"scores": scores, "times": times})
    fig = plt.figure()
    plt.plot(scores)
    plt.title("Score as a function of iteration")
    plt.ylabel("Score")
    plt.xlabel("iter")
    plt.savefig(f"./results/{a.save_name}.png")
    plt.close(fig)
    df.to_csv(f"./results/{a.save_name}.csv")


def main_func(a):
    """
    main function that runs the solver
    """
    dset = load_dset(a.dset_path, a)
    check_args(a, dset)
    solver = get_solver(a, dset)
    ret = np.array([x for x in solver.solve()])
    sol, scores, times = ret[:, 0][-1], ret[:, 1], ret[:, 2]
    save_results(sol, scores, times, a)


def parse_args():
    parser = argparse.ArgumentParser()

    # global arguments
    parser.add_argument("--dset_path", required=False, help="path/to/dataset.npy\nif you wish to regenerate a dataset"
                                                            " and run using the generated don't pass anything.\n see "
                                                            "n, max_cost, max_rev, min_rev, save_path arguments")
    parser.add_argument("--algorithm", required=False, help="genetic/optimal/greedy, default=greedy", default=GREEDY)
    parser.add_argument("--save_name", required=True, help="name of the results file to be saved",
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
    parser.add_argument("--p_mutation", default=0.3, help="p in range (0,1) used as bernoulli factor for mutation "
                                                          "generation", required=False)
    parser.add_argument("--step_th", default=2e4, help="threshold for max number of generations to consider",
                        required=False)
    parser.add_argument("--score_th", default=np.inf, help="threshold for max score", required=False)
    parser.add_argument("--population_size", default=200, help="population size", required=False)
    parser.add_argument("--tour_length", default=10, help="number of tour days", required=False)
    parser.add_argument("--elitism_factor", default=50, help="elitism factor", required=False)
    parser.add_argument("--partition", required=False, help="partition function version - only for genetic", default=1)
    parser.add_argument("--city_selection", required=False, help="city selection function version - only for genetic",
                        default=1)

    ret = parser.parse_args()
    return ret


if __name__ == "__main__":
    args = parse_args()
    main_func(args)

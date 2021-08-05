import argparse
import numpy as np
import os
from constants import *
from itertools import permutations
from typing import Dict


def randomize_cost(num_cities: int, max_cost: int) -> Dict[(int, int)]:
    """
    generates a dictionary of (city_A, city_B) -> cost of going from A to B
    costs are randomly generated from range 0 - max_cost.
    :param num_cities: number of cities in dataset
    :param max_cost: maximal cost for single transition
    :return: a dictionary of (city_A, city_B) -> cost of going from A to B
    """
    cities = np.array(permutations(np.arange(num_cities), 2))

    def get_cost(x, y):
        return 0 if x == y else np.random.randint(max(1, max_cost // 10), max_cost)

    return {cities[i]: x for i, x in enumerate(map(get_cost, cities))}


def gen_dset(num_cities: int,
             max_cost: int,
             min_rev: int,
             max_rev: int) -> Dict[str]:
    costs = randomize_cost(num_cities, max_cost)
    revenues = {i: np.random.randint(min_rev, max_rev) for i in range(num_cities)}
    return {CITIES: revenues.keys(), COSTS: costs, REV: revenues}


def get_base_dir_and_name(save_path: str) -> (str, str):
    path = save_path.split("/")
    base_dir, file_name = "", f"{path[-1]}"
    if file_name[-4:] != ".npy":
        file_name += ".npy"
    if len(save_path.strip(r"[ \t\n]")) == 0:
        raise ValueError("invalid path was given")
    elif len(path) > 2:
        if not os.path.exists("/".join(path[:-1])):
            if not os.path.exists("/".join(path[:-2])):
                raise ValueError("invalid path was given")
            else:
                os.mkdir("/".join(path[:-1]))
                base_dir = "/".join(path[:-1])

    elif len(path) > 1 and not os.path.exists("/".join(path[:-1])):
        os.mkdir("/".join(path[:-1]))
    elif len(path) == 1:
        base_dir = "."
    else:
        base_dir = "/".join(path[:-1])

    return base_dir, file_name


def gen_dset_and_save(num_cities: int,
                      max_cost: int,
                      min_rev: int,
                      max_rev: int,
                      save_path: str):
    dset = gen_dset(num_cities, max_cost, min_rev, max_rev)
    base_dir, file_name = get_base_dir_and_name(save_path)
    np.save("/".join([base_dir, file_name]), dset)

    return dset

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", default=100, help="num_of_cities", required=False)
    parser.add_argument("--max_cost", default=100, help="max cost for each transition", required=False)
    parser.add_argument("--max_rev", default=300, help="max cost for each transition", required=False)
    parser.add_argument("--min_rev", default=50, help="max cost for each transition", required=False)
    parser.add_argument("--save_path", default=None, help="path_to_save_dir/filename.npy", required=False)

    args = parser.parse_args()

    if args.save_path is None:
        return gen_dset(args.n, args.max_cost, args.min_cost, args.max_cost)

    return gen_dset_and_save(args.n, args.max_cost, args.min_cost, args.max_cost, args.save_path)

if __name__ == "__main__":
    main()
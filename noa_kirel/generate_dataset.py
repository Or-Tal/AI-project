import argparse
import numpy as np
import os
from noa_kirel.constants import *
from itertools import product


def randomize_cost(num_cities: int, max_cost: int, revenues: dict) -> dict:
    """
    generates a dictionary of (city_A, city_B) -> cost of going from A to B
    costs are randomly generated from range 0 - max_cost.
    :param num_cities: number of cities in dataset
    :param max_cost: maximal cost for single transition
    :return: a dictionary of (city_A, city_B) -> cost of going from A to B
    """
    cities = [x for x in product(np.arange(num_cities), repeat=2)]

    def get_cost(xy):
        x, y = xy
        return 0 if x == y else np.random.randint(max(1, max_cost // 10), max_cost)\
                                # + (np.random.randint(30, 45) * revenues[y, 0]) // 100  \
                                # + (np.random.randint(30, 45) * revenues[x, 0]) // 100

    ret = {cities[i]: x for i, x in enumerate(map(get_cost, cities))}
    for i in range(num_cities):
        ret[(-1, i)] = np.random.randint(max(1, max_cost // 10), max_cost) \
                       # + (np.random.randint(30, 45) * revenues[i]) // 100

    return ret


def gen_dset(num_cities: int,
             max_cost: int,
             min_rev: int,
             max_rev: int):

    revenues = {(i, j): np.random.randint(min_rev, max_rev) for i in range(num_cities) for j in range(num_cities)}
    costs = randomize_cost(num_cities, max_cost, revenues)
    return {CITIES: num_cities, COSTS: costs, REV: revenues}


def get_base_dir_and_name(save_path: str) -> (str, str):
    """
    TODO fill
    :param save_path:
    :return:
    """
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
        base_dir = "noa_kirel"
    else:
        base_dir = "/".join(path[:-1])

    return base_dir, file_name


def gen_dset_and_save(num_cities: int,
                      max_cost: int,
                      min_rev: int,
                      max_rev: int,
                      save_path: str):
    """
    generated dataset and save to given path
    """
    dset = gen_dset(num_cities, max_cost, min_rev, max_rev)
    # TODO gen coords
    base_dir, file_name = get_base_dir_and_name(save_path)
    np.save("/".join([base_dir, file_name]), dset)
    return dset


def main_gen_func(a):
    if a.save_path is None:
        return gen_dset(int(a.n), int(a.max_cost), int(a.min_rev), int(a.max_rev))

    return gen_dset_and_save(int(a.n), int(a.max_cost), int(a.min_rev),
                             int(a.max_rev), a.save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", default=100, help="num_of_cities", required=False)
    parser.add_argument("--max_cost", default=50, help="max cost for each transition", required=False)
    parser.add_argument("--max_rev", default=300, help="max cost for each transition", required=False)
    parser.add_argument("--min_rev", default=50, help="max cost for each transition", required=False)
    # parser.add_argument("--save_path", default=None, help="path_to_save_dir/filename.npy", required=False)
    parser.add_argument("--save_path", default="./noa_kirel/datasets/a.npy", help="path_to_save_dir/filename.npy",
                        required=False)

    args = parser.parse_args()
    main_gen_func(args)

import argparse
import numpy as np
import os
from noa_kirel.constants import *
from itertools import product


def randomize_cost(num_cities: int, max_cost: int, revenues: dict, ver: int) -> dict:
    """
    generates a dictionary of (city_A, city_B) -> cost of going from A to B
    costs are randomly generated from range 0 - max_cost.
    :param num_cities: number of cities in dataset
    :param max_cost: maximal cost for single transition
    :return: a dictionary of (city_A, city_B) -> cost of going from A to B
    """
    cities = [x for x in product(np.arange(num_cities), repeat=2)]
    triplets = [x for x in product(np.arange(num_cities), repeat=3)]

    def get_cost(xy):
        x, y = xy
        return 0 if x == y else np.random.randint(max(1, max_cost // 10), max_cost)\
                                + (np.random.randint(30, 45) * revenues[y, 0]) // 100  \
                                + (np.random.randint(30, 45) * revenues[x, 0]) // 100

    def get_cost2(xyz):
        x, y, z = xyz
        return 0 if z == y else np.random.randint(max(1, max_cost // 10), max_cost)

    ret = {(cities[i], j): x for j in range(num_cities) for i, x in enumerate(map(get_cost, cities))}
    if ver == 2:
        for j in range(num_cities):
            for i, x in enumerate(map(get_cost2, triplets)):
                ret[(triplets[i], j)] = x
    for i in range(num_cities):
        for j in range(num_cities):
            if ver == 2:
                ret[(-1, -1, i), j] = np.random.randint(max(1, max_cost // 10), max_cost) \
                                     + (np.random.randint(30, 45) * revenues[i, 0])
                for k in range(num_cities):
                    ret[(-1, k, i), j] = np.random.randint(max(1, max_cost // 10), max_cost) \
                                          + (np.random.randint(30, 45) * revenues[i, 0])
            ret[(-1, i), j] = np.random.randint(max(1, max_cost // 10), max_cost) \
                              + (np.random.randint(30, 45) * revenues[i, 0]) // 100

    return ret


def gen_dset(num_cities: int,
             max_cost: int,
             min_rev: int,
             max_rev: int,
             ver: int):

    revenues = {(i, j): np.random.randint(min_rev, max_rev) for i in range(num_cities) for j in range(num_cities)}
    costs = randomize_cost(num_cities, max_cost, revenues, ver)
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
                      save_path: str,
                      ver: int):
    """
    generated dataset and save to given path
    """
    base_dir, file_name = get_base_dir_and_name(save_path)
    if os.path.exists("/".join([base_dir, file_name])):
        return
    dset = gen_dset(num_cities, max_cost, min_rev, max_rev, ver)
    np.save("/".join([base_dir, file_name]), dset)
    return dset


def main_gen_func(a):
    if a.save_path is None:
        return gen_dset(int(a.n), int(a.max_cost), int(a.min_rev), int(a.max_rev), int(a.ver))

    return gen_dset_and_save(int(a.n), int(a.max_cost), int(a.min_rev),
                             int(a.max_rev), a.save_path, int(a.ver))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", default=100, help="num_of_cities", required=False)
    parser.add_argument("--ver", default=1, help="version", required=False)
    parser.add_argument("--max_cost", default=100, help="max cost for each transition", required=False)
    parser.add_argument("--max_rev", default=500, help="max cost for each transition", required=False)
    parser.add_argument("--min_rev", default=100, help="max cost for each transition", required=False)
    # parser.add_argument("--max_cost", default=100000, help="max cost for each transition", required=False)
    # parser.add_argument("--max_rev", default=10000000, help="max cost for each transition", required=False)
    # parser.add_argument("--min_rev", default=10000, help="max cost for each transition", required=False)
    parser.add_argument("--save_path", default=None, help="path_to_save_dir/filename.npy", required=False)
    # parser.add_argument("--save_path", default="./noa_kirel/datasets/a.npy", help="path_to_save_dir/filename.npy",
    #                     required=False)

    args = parser.parse_args()
    main_gen_func(args)

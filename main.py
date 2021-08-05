import numpy as np
import argparse
import os
from constants import *


def load_dset(dset_path):
    if len(dset_path) < 4 or dset_path[-4:] != ".npy" or not \
            os.path.exists(dset_path):
        raise ValueError("invalid dset path was given")
    return np.load(dset_path, allow_pickle=True).tolist()


def main_func():
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dset_path", required=True, help="path/to/dataset.npy")
    parser.add_argument("--model_type", required=False, help="genetic/optimal/greedy, default=greedy", default=GREEDY)
    parser.add_argument("--selection_func", required=False, help="path/to/dataset.npy", default=1)
    parser.add_argument("--selection_func", required=False, help="path/to/dataset.npy", default=1)


if __name__ == "__main__":
    args = parse_args()

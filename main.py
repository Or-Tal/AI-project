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
import os
import pandas as pd
from noa_kirel.constants import *

ANALYZE_SMALL_PATH = "analyzed_small_results.csv"
ANALYZE_BIG_PATH = "analyzed_big_results.csv"

COLS_BIG_CITY = ["num_cities", "population_size", "elitism_factor", "p_mutant", "genetic_first_max_iteration",
                 "genetic_max_score", "greedy_max_score", "genetic_time_achieved", "greedy_time_achieved"]

COLS_SMALL_CITY = ["num_cities", "population_size", "elitism_factor", "p_mutant", "genetic_first_max_iteration",
                   "genetic_max_score", "greedy_max_score", "bf_max_score", "genetic_time_achieved",
                   "greedy_time_achieved", "bf_time_achived"]


def is_interesting(filename):
    split_path = filename.split('_')
    algorithm = split_path[-3]
    return filename != ANALYZE_BIG_PATH and filename != ANALYZE_SMALL_PATH \
           and filename[-3:] == 'csv' and algorithm == GEN


def get_csvs(dir_path):
    """
    :param dir_path: str, name of the directory
    :return: list of all csv paths in requested dir
    """
    return [filename for filename in os.listdir(dir_path) if is_interesting(filename)]


def parse_csv(csv_path, small_cities=False):
    split_path = csv_path.split('_')
    num_cities = int(split_path[2])
    population_size = int(split_path[-4])
    elitism_factor = int(split_path[-1][:-4])
    p_mutant = float(split_path[4])

    genetic_df = pd.read_csv(csv_path).rename(columns={"Unnamed: 0": 'iteration'})
    gen_first_max_iteration = genetic_df['scores'].argmax()
    gen_max_value = genetic_df['scores'].max()
    gen_time_achieved = genetic_df['times'].iloc[gen_first_max_iteration]

    split_path[-3] = GREEDY
    greedy_csv_path = '_'.join(split_path)
    greedy_df = pd.read_csv(greedy_csv_path).rename(columns={"Unnamed: 0": 'iteration'})
    greedy_max_value = greedy_df['scores'].iloc[-1]
    greedy_time_achieved = greedy_df['times'].iloc[-1]

    df_dict = {"num_cities": [num_cities],
               "population_size": [population_size],
               "elitism_factor": [elitism_factor],
               "p_mutant": [p_mutant],
               "genetic_first_max_iteration": [gen_first_max_iteration],
               "genetic_max_score": [gen_max_value],
               "greedy_max_score": [greedy_max_value],
               "genetic_time_achieved": [gen_time_achieved],
               "greedy_time_achieved": [greedy_time_achieved]}

    if small_cities:
        split_path[-3] = BF_SOL
        bf_csv_path = '_'.join(split_path)
        bf_df = pd.read_csv(bf_csv_path).rename(columns={"Unnamed: 0": 'iteration'})
        bf_max_value = bf_df['scores'].iloc[-1]
        bf_time_achieved = bf_df['times'].iloc[-1]
        df_dict["bf_max_score"] = [bf_max_value]
        df_dict["bf_time_achieved"] = [bf_time_achieved]

    cols = COLS_SMALL_CITY if small_cities else COLS_BIG_CITY
    analyzed_df = pd.DataFrame(df_dict)[cols]

    return analyzed_df


def analyze_big_dataset():
    files = get_csvs("results/big")
    all_concatenated = pd.concat([parse_csv(f"results/big/{file}") for file in files])
    all_concatenated = all_concatenated.sort_values(by=['num_cities', 'population_size',
                                                        'elitism_factor', 'p_mutant'])
    all_concatenated.to_csv(f"results/big/{ANALYZE_BIG_PATH}", index=False)


def analyze_small_dataset():
    files = get_csvs("results/small")
    all_concatenated = pd.concat([parse_csv(f"results/small/{file}", small_cities=True) for file in files])
    all_concatenated = all_concatenated.sort_values(by=['num_cities', 'population_size',
                                                        'elitism_factor', 'p_mutant'])
    all_concatenated.to_csv(f"results/small/{ANALYZE_SMALL_PATH}", index=False)


if __name__ == '__main__':
    analyze_small_dataset()
    analyze_big_dataset()



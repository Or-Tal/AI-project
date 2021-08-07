import os
import pandas as pd
from noa_kirel.constants import *
from fix_brute_force_script import fix

ANALYZE_SMALL_PATH = "analyzed_small_results.csv"
ANALYZE_LARGE_PATH = "analyzed_large_results.csv"

COLS_LARGE_CITY = ["num_cities", "tour_length", "population_size", "elitism_factor", "p_mutant",
                   "genetic_first_max_iteration", "genetic_max_score", "greedy_max_score",
                   "genetic_time_achieved", "greedy_time_achieved"]

COLS_SMALL_CITY = ["num_cities", "tour_length", "population_size", "elitism_factor", "p_mutant",
                   "genetic_first_max_iteration", "genetic_max_score", "greedy_max_score", "bf_max_score",
                   "genetic_time_achieved", "greedy_time_achieved", "bf_time_achieved"]


def is_interesting(filename):
    if filename == ANALYZE_SMALL_PATH or filename == ANALYZE_LARGE_PATH:
        return False
    split_path = filename.split('_')
    algorithm = split_path[7]
    return filename[-3:] == 'csv' and algorithm == GEN


def get_csvs(dir_path):
    """
    :param dir_path: str, name of the directory
    :return: list of all csv paths in requested dir
    """
    return [filename for filename in os.listdir(dir_path) if is_interesting(filename)]


def parse_csv(csv_path, small_cities=False):
    split_path = csv_path.split('_')
    num_cities = int(split_path[2])
    p_mutant = float(split_path[4])
    population_size = int(split_path[6])
    elitism_factor = int(split_path[9])
    tour_length = int(split_path[11][:-4])

    genetic_df = pd.read_csv(csv_path).rename(columns={"Unnamed: 0": 'iteration'})
    gen_first_max_iteration = genetic_df['scores'].argmax()
    gen_max_value = genetic_df['scores'].max()
    gen_time_achieved = genetic_df['times'].iloc[gen_first_max_iteration]

    split_path[7] = GREEDY
    greedy_csv_path = '_'.join(split_path)
    try:
        greedy_df = pd.read_csv(greedy_csv_path).rename(columns={"Unnamed: 0": 'iteration'})
        greedy_max_value = greedy_df['scores'].iloc[-1]
        greedy_time_achieved = greedy_df['times'].iloc[-1]
    except FileNotFoundError:
        greedy_max_value = pd.NA
        greedy_time_achieved = pd.NA

    df_dict = {"num_cities": [num_cities],
               "tour_length": [tour_length],
               "population_size": [population_size],
               "elitism_factor": [elitism_factor],
               "p_mutant": [p_mutant],
               "genetic_first_max_iteration": [gen_first_max_iteration],
               "genetic_max_score": [gen_max_value],
               "greedy_max_score": [greedy_max_value],
               "genetic_time_achieved": [gen_time_achieved],
               "greedy_time_achieved": [greedy_time_achieved]}

    if small_cities:
        try:
            split_path[7] = "bruteForce"
            bf_csv_path = '_'.join(split_path)
            bf_df = pd.read_csv(bf_csv_path).rename(columns={"Unnamed: 0": 'iteration'})
            bf_max_value = bf_df['scores'].iloc[-1]
            bf_time_achieved = bf_df['times'].iloc[-1]
            df_dict["bf_max_score"] = [bf_max_value]
            df_dict["bf_time_achieved"] = [bf_time_achieved]
        except FileNotFoundError:
            df_dict["bf_max_score"] = [pd.NA]
            df_dict["bf_time_achieved"] = [pd.NA]

    cols = COLS_SMALL_CITY if small_cities else COLS_LARGE_CITY
    analyzed_df = pd.DataFrame(df_dict)[cols]

    return analyzed_df


def analyze_large_dataset():
    files = get_csvs("results/large")
    all_concatenated = pd.concat([parse_csv(f"results/large/{file}") for file in files])
    all_concatenated = all_concatenated.sort_values(by=['num_cities', 'population_size',
                                                        'elitism_factor', 'p_mutant'])
    all_concatenated.to_csv(f"results/large/{ANALYZE_LARGE_PATH}", index=False)


def analyze_small_dataset():
    files = get_csvs('results/small')
    all_concatenated = pd.concat([parse_csv(f"results/small/{file}", small_cities=True) for file in files])
    all_concatenated = all_concatenated.sort_values(by=['num_cities', 'population_size',
                                                        'elitism_factor', 'p_mutant'])
    all_concatenated.to_csv(f"results/small/{ANALYZE_SMALL_PATH}", index=False)


if __name__ == '__main__':
    # fix("results/small")
    # analyze_small_dataset()
    analyze_large_dataset()



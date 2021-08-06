import os
import pandas as pd


ANALYZE_PATH = "analyzed_results.csv"


def is_interesting(filename):
    return filename != ANALYZE_PATH and filename[-3:] == 'csv' and int(filename.split('_')[-6]) == 2000


def get_csvs(dir_path):
    """
    :param dir_path: str, name of the directory
    :return: list of all csv paths in requested dir
    """
    return [filename for filename in os.listdir(dir_path) if is_interesting(filename)]


def parse_csv(csv_path):
    split_path = csv_path.split('_')
    num_cities = int(split_path[2])
    tour_length = int(split_path[4])
    population_size = int(split_path[-4])
    elitism_factor = int(split_path[-1])
    p_mutant = float(split_path[-10])

    df = pd.read_csv(csv_path).rename(columns={"Unnamed: 0": 'iteration'})
    first_max_iteration = df['scores'].argmax()
    max_value = df['scores'].max()

    analyzed_df = pd.DataFrame({"num_cities": [num_cities],
                                "tour_length": [tour_length],
                                "population_size": [population_size],
                                "elitism_factor": [elitism_factor],
                                "p_mutant": [p_mutant],
                                "first_max_iteration": [first_max_iteration],
                                "max_score": [max_value]})

    return analyzed_df


if __name__ == '__main__':
    files = get_csvs("results")
    # files.sort(key=lambda file: (file.split('_')[2], file.split('_')[4], file.split('_')[-8], file.split('_')[-2]))
    all_concatenated = pd.concat([parse_csv(f"results/{file}") for file in files])
    all_concatenated = all_concatenated.sort_values(by=['num_cities', 'tour_length', 'population_size',
                                                        'elitism_factor', 'p_mutant'])
    all_concatenated.to_csv(f"results/{ANALYZE_PATH}", index=False)

import bz2
import csv
import json
import os
import textwrap
from io import StringIO
from pandas import DataFrame
import os
import matplotlib.pyplot as plt
import pandas as pd
import pygraphviz as pgv
from tabulate import tabulate
import requests
import statistics
import math

import sys

from dataset_displayers.similarity_utils import get_jaccard_similarity, get_common_tropes_similarity

sys.path.append("..")

from dataset_displayers.tropes_similarity import TropesSimilarityChecker
from rating_evaluator.evaluator_tests import EvaluatorTests

data = {}

def read_compressed_json(file_path):
    if file_path in data:
        return data[file_path]

    with open(file_path, 'rb') as file:
        compressed_content = file.read()
    content_bytes = bz2.decompress(compressed_content)
    content = json.loads(content_bytes.decode('utf-8'))

    data[file_path] = content
    return content


def reverse_dictionary(original_dictionary):
    reversed_dictionary = {}
    for key, value in original_dictionary.items():
        for element in value:
            if element not in reversed_dictionary:
                reversed_dictionary[element] = []
            reversed_dictionary[element].append(key)
    return reversed_dictionary


def draw_graphviz(dot, filename):
    new_dot = dot.replace('type="start"', 'shape="ellipse" margin=0.2')
    new_dot = new_dot.replace('type="database"', 'shape="cylinder" margin=0.2')
    new_dot = new_dot.replace('type="tool"', 'shape="box" margin=0.2')
    new_dot = new_dot.replace('type="process"', 'shape="box3d" margin=0.2 style="filled" fillcolor="lightblue"')
    new_dot = new_dot.replace('type="data"', 'shape="polygon" skew=0.5 margin=0')

    G = pgv.AGraph(string=new_dot)
    G.layout(prog='dot')
    if not os.path.isdir('figures'):
        os.makedirs('figures')
    G.draw(os.path.join('figures', filename))


def get_table_for_dataframe(df, fixed_width=None, **kwargs):
    latex_code = tabulate(df, headers=df, tablefmt='latex_raw', **kwargs)
    latex_code = latex_code.replace('%', '\\%')
    if fixed_width is not None:
        latex_code = latex_code.replace('\\begin{tabular}','\\begin{tabularx}{\\textwidth}')
        latex_code = latex_code.replace('\\end{tabular}', '\\end{tabularx}')
        latex_code = latex_code.replace('{lr}','{Xr}')
        latex_code = latex_code.replace('{rllrrl}', '{rLLrrl}')
        latex_code = latex_code.replace('[GENRE]','')
    return latex_code

def get_tabularx_for_dataframe(df, **kwargs):
    latex_code = tabulate(df, headers=df, tablefmt='latex_raw', **kwargs)
    latex_code = latex_code.replace('%', '\\%')
    latex_code = latex_code.replace('\\begin{tabular}', '\\begin{tabularx}')
    latex_code = latex_code.replace('\\end{tabular}', '\\end{tabularx}')
    return latex_code

def tex_wrap_and_escape(text, length=40):
    if isinstance(text, str):
        wrapped_text = textwrap.fill(text, length)
        if '\n' in wrapped_text:
            wrapped_text = '\makecell[tl]{' + wrapped_text.replace('\n', ' \\\\ ') + '}'
        return tex_escape(wrapped_text)
    if isinstance(text, list):
        text = ', '.join([str(element) for element in text])
        return tex_wrap_and_escape(text)
    return text


def tex_escape(text):
    CHARS = {
        '&': '\&',
        '%': '\%',
        '$': '\$',
        '#': '\#',
        '_': '\_',
        '^': '\^',
    }

    if isinstance(text, str):
        return ("".join([CHARS.get(char, char) for char in text]))

    return text


def get_experiment_execution_information(log_file_path):
    with open(log_file_path, 'r') as scraper_log:
        lines = scraper_log.readlines()
        first_line = lines[0]
        last_line = lines[-1]

    parameters_as_text = first_line.split('Init script: ')[1]
    input_log = json.loads(parameters_as_text)
    keys = [tex_wrap_and_escape(key) for key in input_log.keys()]
    values = [tex_wrap_and_escape(key) for key in input_log.values()]
    processed_dictionary = dict(parameter=keys, value=values)
    input_dataframe = pd.DataFrame.from_dict(processed_dictionary)

    summary_as_text = last_line.split('Finish script: ')[1]
    output_log = json.loads(summary_as_text)
    keys = [tex_wrap_and_escape(key) for key in output_log.keys()]
    values = [tex_wrap_and_escape(key) for key in output_log.values()]
    processed_dictionary = dict(parameter=keys, value=values)
    output_dataframe = pd.DataFrame(processed_dictionary)
    return input_dataframe, output_dataframe


def read_dataframe(file_path, use_hdf=True):
    if file_path in data:
        return data[file_path]

    if file_path.endswith('csv.bz2'):
        content = None

        file_hdf = file_path.replace('csv.bz2', 'h5')
        if os.path.isfile(file_hdf):
            content = pd.read_hdf(file_hdf)
        else:
            with open(file_path, 'rb') as file:
                compressed_content = file.read()
            csv_content = bz2.decompress(compressed_content)
            content = pd.read_csv(StringIO(csv_content.decode('utf-8')))
            if use_hdf:
                content.to_hdf(file_hdf, 'tripdata')

    data[file_path] = content
    return content


def plot_regression(dataframe, x_column, y_column, color='red'):
    Y = dataframe[y_column]
    X = dataframe[x_column]

    X = X.values.reshape(len(X), 1)
    Y = Y.values.reshape(len(Y), 1)

    X_train = X[:-250]
    X_test = X[-250:]
    Y_train = Y[:-250]
    Y_test = Y[-250:]

    from sklearn import linear_model
    regr = linear_model.LinearRegression()

    regr.fit(X_train, Y_train)
    plt.plot(X_test, regr.predict(X_test), color=color, linewidth=3, )


def extract_iterations_from_log(log_file_name):
    iteration_line = '^.*\\| Iteration ([0-9]+), loss = ([0-9\.]+)$'
    validation_score = '^.*\\| Validation score: ([0-9\\-\\+\\.]+)$'

    values = []
    with open(log_file_name, 'r') as scraper_log:
        lines = scraper_log.readlines()
    import re
    for line in lines:
        matches = re.search(iteration_line, line)
        if matches:
            entry = {'iteration': float(matches.group(1)), 'loss': float(matches.group(2))}
            values.append(entry)
        matches = re.search(validation_score, line)
        if matches:
            entry = values[-1]
            entry['validation'] = float(matches.group(1))

    return pd.DataFrame(values)

def extract_grid_parameters_from_log_and_results(log_file_name):
    result_line = '^.*\\| Result: [^\{]*(.*)$'

    values = []
    with open(log_file_name, 'r') as scraper_log:
        lines = scraper_log.readlines()
    import re
    for line in lines:
        matches = re.search(result_line, line)
        if matches:
            text = matches.group(1)
            text = re.sub("'hidden_layer_sizes': \\(([^\\)]*)\\)", "'hidden_layer_sizes': '(\\1)'", text)
            text = text.replace('\'','"')
            entry = json.loads(text)
            entry = {key.replace('_',' '):value for key,value in entry.items()}
            values.append(entry)
    dataframe = pd.DataFrame(values)
    dataframe = dataframe[['activation','alpha','hidden layer sizes','learning rate','max iter','solver','mean','std']]
    dataframe = dataframe.sort_values(by='mean', ascending=False).reset_index(drop=True)
    return dataframe


def human_readable(value):
    if isinstance(value, float):
        print ("{0:.3f}".format(value))
        return

    print (str(value))


def human_readable_percent(value):
    if isinstance(value, float):
        print ("{0:.2f}".format(value))
        return

    print (str(value))

def get_solutions_analysis(film_extended_dataset_dictionary, recommender_details_log):
    checker = TropesSimilarityChecker()
    checker.load_extended_dataset_json(film_extended_dataset_dictionary)

    solutions = []
    ratings = []

    with open(recommender_details_log) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count += 1
            if row[3] == '0.016666666666666666' and row[4] == '0.25' and row[5] == '200':
                ratings.append(float(row[8]))
                tropes = set([item.strip() for item in row[10:]])
                solutions.append(tropes)
    pairs = []

    copy_of_solutions = solutions.copy()
    while len(copy_of_solutions):
        current_candidate = copy_of_solutions.pop(0)
        for other_candidate in copy_of_solutions:
            pairs.append((current_candidate, other_candidate))

    # math.factorial(30) / (math.factorial(2) * math.factorial(30-2))
    jaccard_coefficients_intra_synthetic = []
    common_coefficients_intra_synthetic = []
    for pair in pairs:
        similarity = get_jaccard_similarity(pair[0], pair[1])
        jaccard_coefficients_intra_synthetic.append(similarity)
        similarity = get_common_tropes_similarity(pair[0], pair[1])
        common_coefficients_intra_synthetic.append(similarity)

    jaccard_coefficients_inter_corpus = []
    common_coefficients_inter_corpus = []
    for solution in solutions:
        for existing_film in checker.films:
            film_tropes = set(existing_film["tropes"])

            similarity = get_jaccard_similarity(solution, film_tropes)
            jaccard_coefficients_inter_corpus.append(similarity)
            similarity = get_common_tropes_similarity(solution, film_tropes)
            common_coefficients_inter_corpus.append(similarity)

    nan_values = len(jaccard_coefficients_inter_corpus) - len(jaccard_coefficients_intra_synthetic)

    ratings = DataFrame.from_dict({'rating': ratings})

    jaccard_coefficients = DataFrame.from_dict(
        {'intra-synthetic Cj': jaccard_coefficients_intra_synthetic + [None for index in range(0, nan_values)],
         'inter-corpus Cj': jaccard_coefficients_inter_corpus})

    common_coefficients = DataFrame.from_dict(
        {'intra-synthetic Cc': common_coefficients_intra_synthetic + [None for index in range(0, nan_values)],
         'inter-corpus Cj': common_coefficients_inter_corpus})

    all_the_tropes_in_synthetic_films = set()
    for solution in solutions:
        all_the_tropes_in_synthetic_films.update(solution)
    #236
    films_that_contain_any_trope = set()
    for trope in all_the_tropes_in_synthetic_films:
        for existing_film in checker.films:
            if trope in existing_film['tropes']:
                films_that_contain_any_trope.add(existing_film['name'])
    #10022
    ratings_films_in_tropes = []
    for existing_film in checker.films:
        if existing_film['name'] in films_that_contain_any_trope:
            ratings_films_in_tropes.append(existing_film['rating'])

    # TODO Pending...


    return ratings, jaccard_coefficients, common_coefficients

if __name__ == '__main__':
    FILM_EXTENDED_DATASET_DICTIONARY_BZ2_FILE = '../datasets/extended_dataset.json.bz2'
    RECOMMENDER_DETAILS_LOG = '../logs/recommender_summary.log'
    ratings, jaccard, common = get_solutions_analysis(FILM_EXTENDED_DATASET_DICTIONARY_BZ2_FILE,
                                                      RECOMMENDER_DETAILS_LOG)

    pass

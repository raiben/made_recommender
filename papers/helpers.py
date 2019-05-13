import bz2
import json

import pandas as pd
from pandas import DataFrame
from tabulate import tabulate


def read_compressed_json(file_path):
    with open(file_path, 'rb') as file:
        compressed_content = file.read()
    content = bz2.decompress(compressed_content)
    return json.loads(content)


def reverse_dictionary(original_dictionary):
    reversed_dictionary = {}
    for key, value in original_dictionary.items():
        for element in value:
            if element not in reversed_dictionary:
                reversed_dictionary[element] = []
            reversed_dictionary[element].append(key)
    return reversed_dictionary


import pygraphviz as pgv
import os


def draw_graphviz(dot, filename):
    new_dot = dot.replace('type="database"', 'shape="cylinder" margin="0.2"')
    new_dot = new_dot.replace('type="process"', 'shape="box" margin="0.2" style="filled" fillcolor="gray91"')
    new_dot = new_dot.replace('type="data"', 'shape="parallelogram" margin="0"')

    G = pgv.AGraph(string=new_dot)
    G.layout(prog='dot')
    if not os.path.isdir('figures'):
        os.makedirs('figures')
    G.draw(os.path.join('figures', filename))


def show_dataframe(df, **kwargs):
    print(tabulate(df, headers=df, tablefmt='latex', **kwargs))


def draw_sample_graph():
    content = read_compressed_json('../datasets/scraper/cache/20190501/films_tropes_20190501.json.bz2')
    reversed_content = reverse_dictionary(content)
    workflow = '''
    digraph {
        tvtropes[label="TVTropes\nwebsite" type="database"];
        scraper[label="Scraper\nprocess" type="process"];
        dataset1[label="Dataset\nFilm->(tropes)" type="data"];
        imdb[label="IMDB\ndatabases" type="database"];
        matcher[label="Film\nmatcher\nprocess" type="process"];
        dataset2[label="Dataset\nFilm->(tropes,\nrating, genres)" type="data"];
        recommender[label="Trope\nRecommender\nprocess" type="process"];
        user[label="User's\npre-selected\ntropes" type="data"];
        builder[label="Trope\nbuilder\nprocess" type="process"];
        trope_sequence[label="Optimal\ntrope\nsequence" type="data"]

        tvtropes -> scraper;
        scraper -> dataset1;
        dataset1 -> matcher;
        imdb -> matcher;
        matcher -> dataset2;
        dataset2 -> recommender;
        recommender -> builder
        user -> builder
        builder -> trope_sequence
    }'''
    draw_graphviz(workflow, "main_workflow2.pdf")


FILM_TROPES_JSON_BZ2_FILE = '../datasets/scraper/cache/20190501/films_tropes_20190501.json.bz2'
SCRAPER_LOG_FILE = '../logs/scrape_tvtropes_20190501_20190512_191015.log'


def summary_info():
    films_dictionary = read_compressed_json(FILM_TROPES_JSON_BZ2_FILE)
    tropes_dictionary = reverse_dictionary(films_dictionary)
    films_summary_dictionary = {}
    for key in films_dictionary:
        films_summary_dictionary[key] = {'tropes': len(films_dictionary[key])}
    films_summary_dataframe = pd.DataFrame(films_summary_dictionary)
    pass


def get_table_for_dataframe(df, **kwargs):
    return tabulate(df, headers=df, tablefmt='latex', **kwargs)

import textwrap

def get_experiment_execution_information(log_file_path):
    wrapper = textwrap.TextWrapper(width=50)

    with open(log_file_path, 'r') as scraper_log:
        lines = scraper_log.readlines()
        first_line = lines[0]
        last_line = lines[-1]

    parameters_as_text = first_line.split('Init script: ')[1]
    input_log = json.loads(parameters_as_text)
    processed_dictionary = dict(parameter=list(input_log.keys()),
                                value=list(input_log.values()))
    input_dataframe = DataFrame.from_dict(processed_dictionary)

    summary_as_text = last_line.split('Finish script: ')[1]
    output_log = json.loads(summary_as_text)
    processed_dictionary = dict(parameter=list(output_log.keys()),
                                value=list(output_log.values()))
    output_dataframe = DataFrame(processed_dictionary)
    return input_dataframe, output_dataframe


if __name__ == '__main__':
    input, output = get_experiment_execution_information(SCRAPER_LOG_FILE)
    latex_input = get_table_for_dataframe(input)
    latex_output = get_table_for_dataframe(output)
    pass

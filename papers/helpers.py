import bz2
import json
import pandas as pd
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

if __name__ == '__main__':
    films_dictionary = read_compressed_json(FILM_TROPES_JSON_BZ2_FILE)
    tropes_dictionary = reverse_dictionary(films_dictionary)
    films_summary_dictionary = {}
    for key in films_dictionary:
        films_summary_dictionary[key] = {'tropes': len(films_dictionary[key])}

    films_summary_dataframe = pd.DataFrame(films_summary_dictionary)
    pass
import json
import os
import re

import pandas as pd
import pygraphviz as pgv
from IPython.display import display, Latex
from scipy import stats

DBTROPES_GENERATED_FILE_PATH = '/Users/phd/Downloads/dbtropes/dbtropes-20160701.nt'
TROPESCRAPER_GENERATED_FILE_PATH = '/Users/phd/workspace/made/tropescraper/bin/tvtropes.json'

DBTROPES_DATE = '20160701'
TROPESCRAPER_DATE = '20190915'

BINS = 100
FIGURE_SIZE = [12, 5]


def draw_graphviz(dot, filename):
    G = pgv.AGraph()
    G = G.from_string(dot)
    G.layout(prog='dot')
    if not os.path.isdir('figures'):
        os.makedirs('figures')
    G.draw(os.path.join('figures', filename))


def reverse_mapping(mapping):
    reverse_map = {}
    for key in mapping.keys():
        for value in mapping[key]:
            if value not in reverse_map:
                reverse_map[value] = []
            reverse_map[value].append(key)
    return reverse_map


template = '^<http://dbtropes.org/resource/Film/([^>]+)> ' \
           + '<http://skipforward.net/skipforward/resource/seeder/skipinions/hasFeature> ' \
           + '<http://dbtropes.org/resource/Main/([^/]+)/[^>/]+>.*$'
dbtropes_dataset = {}
dbtropes_films = set()
dbtropes_tropes = set()

with open(DBTROPES_GENERATED_FILE_PATH, 'r') as bdtropes_file:
    line = bdtropes_file.readline()
    counter = 1
    while line:
        matches = re.match(template, line)
        if matches:
            film = matches.group(1)
            dbtropes_films.add(film)

            trope = matches.group(2)
            dbtropes_tropes.add(trope)

            if film not in dbtropes_dataset:
                dbtropes_dataset[film] = set()

            dbtropes_dataset[film].add(trope)

        line = bdtropes_file.readline()
        counter += 1

dbtropes_dataset_reversed = reverse_mapping(dbtropes_dataset)

tropescraper_films = set()
tropescraper_tropes = set()

with open(TROPESCRAPER_GENERATED_FILE_PATH, 'r') as tropescraper_file:
    tropescraper_dataset = json.load(tropescraper_file)

tropescraper_films = set(dbtropes_dataset.keys())
for key in tropescraper_films:
    tropescraper_tropes.update(dbtropes_dataset[key])

tropescraper_dataset_reversed = reverse_mapping(tropescraper_dataset)

dbtropes_dataset_count_by_film = {film: len(dbtropes_dataset[film])
                                  for film in dbtropes_dataset.keys()}
tropescraper_dataset_count_by_film = {film: len(tropescraper_dataset[film])
                                      for film in tropescraper_dataset.keys()}

dbtropes_values = list(dbtropes_dataset_count_by_film.values())
tropescraper_values = list(tropescraper_dataset_count_by_film.values())

dbtropes_dataset_count_by_trope = {trope: len(dbtropes_dataset_reversed[trope])
                                   for trope in dbtropes_dataset_reversed.keys()}
tropescraper_dataset_count_by_trope = {trope: len(tropescraper_dataset_reversed[trope])
                                       for trope in tropescraper_dataset_reversed.keys()}

dbtropes_values = list(dbtropes_dataset_count_by_trope.values())
tropescraper_values = list(tropescraper_dataset_count_by_trope.values())


def describe_tropes():
    dbtropes_stats = stats.describe(dbtropes_values)
    tropescraper_stats = stats.describe(tropescraper_values)
    dataframe = pd.DataFrame.from_dict({
        'min': [dbtropes_stats.minmax[0], tropescraper_stats.minmax[0]],
        'max': [dbtropes_stats.minmax[1], tropescraper_stats.minmax[1]],
        'nobs': [dbtropes_stats.nobs, tropescraper_stats.nobs],
        'mean': [dbtropes_stats.mean, tropescraper_stats.mean],
        'kurtosis': [dbtropes_stats.kurtosis, tropescraper_stats.kurtosis],
        'skewness': [dbtropes_stats.skewness, tropescraper_stats.skewness],
        'variance': [dbtropes_stats.variance, tropescraper_stats.variance]
    }, orient='index')
    dataframe.columns = [DBTROPES_DATE, TROPESCRAPER_DATE]
    display(Latex(dataframe.to_latex()))


def boxplot_tropes():
    values_concatenated = pd.DataFrame.from_dict({
        DBTROPES_DATE: dbtropes_values,
        TROPESCRAPER_DATE: tropescraper_values
    }, orient='index')
    values_concatenated.transpose().plot(kind='box', figsize=FIGURE_SIZE, logy=True)


def frequencies_tropes():
    dataframe = pd.DataFrame.from_dict({'values': dbtropes_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    ax = frequencies.plot.scatter(x='index', y='values', color='Blue', label=DBTROPES_DATE,
                                  logy=True)

    dataframe = pd.DataFrame.from_dict({'values': tropescraper_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    frequencies.plot.scatter(x='index', y='values', color='Orange', label=TROPESCRAPER_DATE,
                             ax=ax, logy=True)


def describe_films():
    dbtropes_stats = stats.describe(dbtropes_values)
    tropescraper_stats = stats.describe(tropescraper_values)
    dataframe = pd.DataFrame.from_dict({
        'min': [dbtropes_stats.minmax[0], tropescraper_stats.minmax[0]],
        'max': [dbtropes_stats.minmax[1], tropescraper_stats.minmax[1]],
        'nobs': [dbtropes_stats.nobs, tropescraper_stats.nobs],
        'mean': [dbtropes_stats.mean, tropescraper_stats.mean],
        'kurtosis': [dbtropes_stats.kurtosis, tropescraper_stats.kurtosis],
        'skewness': [dbtropes_stats.skewness, tropescraper_stats.skewness],
        'variance': [dbtropes_stats.variance, tropescraper_stats.variance]
    }, orient='index')
    dataframe.columns = [DBTROPES_DATE, TROPESCRAPER_DATE]
    display(Latex(dataframe.to_latex()))


def boxplot_films():
    values_concatenated = pd.DataFrame.from_dict({
        DBTROPES_DATE: dbtropes_values,
        TROPESCRAPER_DATE: tropescraper_values
    }, orient='index')
    values_concatenated.transpose().plot(kind='box', figsize=FIGURE_SIZE, logy=True)


def frequencies_films():
    dataframe = pd.DataFrame.from_dict({'values': dbtropes_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    ax = frequencies.plot.scatter(x='index', y='values', color='Blue', label=DBTROPES_DATE,
                                  logy=True)

    dataframe = pd.DataFrame.from_dict({'values': tropescraper_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    frequencies.plot.scatter(x='index', y='values', color='Orange', label=TROPESCRAPER_DATE,
                             ax=ax, logy=True)

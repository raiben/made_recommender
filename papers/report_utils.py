import json
import os
import re
from collections import OrderedDict

import pandas as pd
import pygraphviz as pgv
from IPython.display import display, Latex
from scipy import stats

DBTROPES_GENERATED_FILE_PATH = '/Users/phd/Downloads/dbtropes/dbtropes-20160701.nt'
TROPESCRAPER_GENERATED_FILE_PATH = '/Users/phd/workspace/made/tropescraper/bin/tvtropes.json'

DBTROPES_DATE = 'July 2016'
TROPESCRAPER_DATE = 'November 2019'

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

tropes_dbtropes_values = list(dbtropes_dataset_count_by_film.values())
tropes_tropescraper_values = list(tropescraper_dataset_count_by_film.values())


def describe_tropes():
    dbtropes_stats = stats.describe(tropes_dbtropes_values)
    tropescraper_stats = stats.describe(tropes_tropescraper_values)
    dataframe = pd.DataFrame.from_dict({
        'min': [round(dbtropes_stats.minmax[0], 3), round(tropescraper_stats.minmax[0], 3)],
        'max': [round(dbtropes_stats.minmax[1], 3), round(tropescraper_stats.minmax[1], 3)],
        'nobs': [round(dbtropes_stats.nobs, 3), round(tropescraper_stats.nobs, 3)],
        'mean': [round(dbtropes_stats.mean, 3), round(tropescraper_stats.mean, 3)],
        'kurtosis': [round(dbtropes_stats.kurtosis, 3), round(tropescraper_stats.kurtosis, 3)],
        'skewness': [round(dbtropes_stats.skewness, 3), round(tropescraper_stats.skewness, 3)],
        'variance': [round(dbtropes_stats.variance, 3), round(tropescraper_stats.variance, 3)]
    }, orient='index')
    dataframe.columns = [DBTROPES_DATE, TROPESCRAPER_DATE]
    display(Latex(dataframe.to_latex()))


def boxplot_tropes():
    dictionary = OrderedDict([(TROPESCRAPER_DATE, tropes_tropescraper_values), (DBTROPES_DATE, tropes_dbtropes_values)])
    values_concatenated = pd.DataFrame.from_dict(dictionary, orient='index')
    ax = values_concatenated.transpose().plot(kind='box', logx=True, vert=False)
    ax.set(xlabel='Number of tropes in films')


def frequencies_tropes():
    dataframe = pd.DataFrame.from_dict({'values': tropes_dbtropes_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    ax = frequencies.plot.scatter(x='index', y='values', color='Blue', alpha=0.5, s=25, label=DBTROPES_DATE,
                                  logy=True)

    dataframe = pd.DataFrame.from_dict({'values': tropes_tropescraper_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    frequencies.plot.scatter(x='index', y='values', color='Red', alpha=0.5, s=25, label=TROPESCRAPER_DATE,
                             ax=ax, logy=True, logx=True)
    ax.set(xlabel='Number of tropes by film', ylabel='Number of films')


def top_films_by_number_of_tropes(number_of_films):
    top_films_dbtropes = sorted(dbtropes_dataset_count_by_film.keys(), key=lambda x: dbtropes_dataset_count_by_film[x],
                                reverse=True)[:number_of_films]
    tropes_top_dbtropes = list(map(lambda x: dbtropes_dataset_count_by_film[x], top_films_dbtropes))
    top_films_tropescrapper = sorted(tropescraper_dataset_count_by_film.keys(),
                                     key=lambda x: tropescraper_dataset_count_by_film[x],
                                     reverse=True)[:number_of_films]
    tropes_top_tropescraper = list(map(lambda x: tropescraper_dataset_count_by_film[x], top_films_tropescrapper))

    common_tropes = set(top_films_dbtropes).intersection(set(top_films_tropescrapper))

    dataframe = pd.DataFrame.from_dict({
        'Film ({})'.format(DBTROPES_DATE): ['\\textbf{{{}}}'.format(name) if name in common_tropes else name
                                            for name in top_films_dbtropes],
        'Tropes': tropes_top_dbtropes,
        'Film ({})'.format(TROPESCRAPER_DATE): ['\\textbf{{{}}}'.format(name) if name in common_tropes else name
                                                for name in top_films_tropescrapper],
        'Tropes2': tropes_top_tropescraper
    })
    display(Latex(dataframe.to_latex(escape=False)))


dbtropes_dataset_count_by_trope = {trope: len(dbtropes_dataset_reversed[trope])
                                   for trope in dbtropes_dataset_reversed.keys()}
tropescraper_dataset_count_by_trope = {trope: len(tropescraper_dataset_reversed[trope])
                                       for trope in tropescraper_dataset_reversed.keys()}

films_dbtropes_values = list(dbtropes_dataset_count_by_trope.values())
films_tropescraper_values = list(tropescraper_dataset_count_by_trope.values())


def describe_films():
    dbtropes_stats = stats.describe(films_dbtropes_values)
    tropescraper_stats = stats.describe(films_tropescraper_values)
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
        DBTROPES_DATE: films_dbtropes_values,
        TROPESCRAPER_DATE: films_tropescraper_values
    }, orient='index')
    values_concatenated.transpose().plot(kind='box', figsize=FIGURE_SIZE, logy=True)


def frequencies_films():
    dataframe = pd.DataFrame.from_dict({'values': films_dbtropes_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    ax = frequencies.plot.scatter(x='index', y='values', color='Blue', label=DBTROPES_DATE,
                                  logy=True)

    dataframe = pd.DataFrame.from_dict({'values': films_tropescraper_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    frequencies.plot.scatter(x='index', y='values', color='Orange', label=TROPESCRAPER_DATE,
                             ax=ax, logy=True, logx=True)

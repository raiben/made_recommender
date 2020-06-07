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

DBTROPES_DATE = 'Jul. 2016'
TROPESCRAPER_DATE = 'April. 2020'

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


def describe(dbtropes_values, tropescrapper_values):
    dbtropes_stats = stats.describe(dbtropes_values)
    tropescraper_stats = stats.describe(tropescrapper_values)
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


def boxplot(dbtropes_values, tropescraper_values, xlabel):
    dictionary = OrderedDict([(TROPESCRAPER_DATE, tropescraper_values), (DBTROPES_DATE, dbtropes_values)])
    values_concatenated = pd.DataFrame.from_dict(dictionary, orient='index')
    ax = values_concatenated.transpose().plot(kind='box', logx=True, vert=False)
    ax.set(xlabel=xlabel)


def frequencies(dbtropes_values, tropescraper_values, xlabel, ylabel):
    dataframe = pd.DataFrame.from_dict({'values': dbtropes_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    ax = frequencies.plot.scatter(x='index', y='values', color='Blue', alpha=0.5, s=25, label=DBTROPES_DATE,
                                  logy=True)

    dataframe = pd.DataFrame.from_dict({'values': tropescraper_values})
    frequencies = pd.DataFrame([dataframe.iloc[:, 0].value_counts()]).transpose().reset_index()
    frequencies.plot.scatter(x='index', y='values', color='Red', alpha=0.5, s=25, label=TROPESCRAPER_DATE,
                             ax=ax, logy=True, logx=True)
    ax.set(xlabel=xlabel, ylabel=ylabel)

def _calculate_increment(film, dbtropes_count, tropescraper_count, changed_names):
    former_film = next((key for key,value in changed_names.items() if value == film), film)
    current_count = tropescraper_count[film]
    former_count = dbtropes_count.get(former_film, 0)
    if former_count == 0:
        return '--'

    increment = ((current_count - former_count) / former_count) * 100.0
    return '{:+,.1f}\\%'.format(increment, grouping=True)

def top(number_of_items, dbtropes_count, tropescraper_count, key_name, count_name, changed_names):
    top_films_dbtropes = sorted(dbtropes_count.keys(), key=lambda x: dbtropes_count[x],
                                reverse=True)[:number_of_items]
    tropes_top_dbtropes = list(map(lambda x: dbtropes_count[x], top_films_dbtropes))
    top_films_tropescrapper = sorted(tropescraper_count.keys(), key=lambda x: tropescraper_count[x],
                                     reverse=True)[:number_of_items]
    tropes_top_tropescraper = list(map(lambda x: tropescraper_count[x], top_films_tropescrapper))
    increment = list(map(lambda x: _calculate_increment(x, dbtropes_count, tropescraper_count, changed_names),
                         top_films_tropescrapper))

    common_tropes = set(top_films_dbtropes).intersection(set(top_films_tropescrapper))
    for key, value in changed_names.items():
        if key in top_films_dbtropes and value in top_films_tropescrapper:
            common_tropes.add(key)
            common_tropes.add(value)

    def format_normal(x):
        return '{}'.format(x)

    def format_color(x):
        return '\\textcolor{{blue}}{{{}}}'.format(x) if x in common_tropes else format_normal(x)

    dataframe = pd.DataFrame.from_dict(OrderedDict([
        ('Key1', top_films_dbtropes), ('Count1', tropes_top_dbtropes),
        ('Key2', top_films_tropescrapper), ('Count2', tropes_top_tropescraper), ('Increment', increment)
    ]))
    header = ['{} ({})'.format(key_name, DBTROPES_DATE), count_name, '{} ({})'.format(key_name, TROPESCRAPER_DATE),
              count_name, 'Increment']
    formatters = {'Key1': format_color, 'Key2': format_color}
    display(Latex(dataframe.to_latex(escape=False, header=header, formatters=formatters)))


dbtropes_dataset_count_by_film = {film: len(dbtropes_dataset[film])
                                  for film in dbtropes_dataset.keys()}
tropescraper_dataset_count_by_film = {film: len(tropescraper_dataset[film])
                                      for film in tropescraper_dataset.keys()}
tropes_dbtropes_values = list(dbtropes_dataset_count_by_film.values())
tropes_tropescraper_values = list(tropescraper_dataset_count_by_film.values())

dbtropes_dataset_count_by_trope = {trope: len(dbtropes_dataset_reversed[trope])
                                   for trope in dbtropes_dataset_reversed.keys()}
tropescraper_dataset_count_by_trope = {trope: len(tropescraper_dataset_reversed[trope])
                                       for trope in tropescraper_dataset_reversed.keys()}
films_dbtropes_values = list(dbtropes_dataset_count_by_trope.values())
films_tropescraper_values = list(tropescraper_dataset_count_by_trope.values())


def describe_tropes():
    return describe(tropes_dbtropes_values, tropes_tropescraper_values)


def describe_films():
    return describe(films_dbtropes_values, films_tropescraper_values)


def boxplot_tropes():
    return boxplot(tropes_dbtropes_values, tropes_tropescraper_values, 'Number of tropes used in a film')


def boxplot_films():
    return boxplot(films_dbtropes_values, films_tropescraper_values, 'Number of films that use a trope')


def frequencies_tropes():
    return frequencies(tropes_dbtropes_values, tropes_tropescraper_values, 'Number of tropes by film',
                       'Number of films')


def frequencies_films():
    return frequencies(films_dbtropes_values, films_tropescraper_values, 'Number of films by trope', 'Number of tropes')


def top_films_by_number_of_tropes(number_of_items):
    changed_names = {'TheAvengers': 'TheAvengers2012', 'StarTrek': 'StarTrek2009', 'AlienS': 'Aliens',
                     'Batman': 'Batman1989', 'XMen': 'XMenFilmSeries'}
    return top(number_of_items, dbtropes_dataset_count_by_film, tropescraper_dataset_count_by_film, 'Film', 'Tropes',
               changed_names)


def top_tropes_by_number_of_films(number_of_items):
    changed_names = {}
    return top(number_of_items, dbtropes_dataset_count_by_trope, tropescraper_dataset_count_by_trope, 'Trope', 'Films',
               changed_names)

# much code can be improved by using a datastructe.
SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
    # I'm checking for 10-20 because those are the digits that
    # don't follow the normal counting scheme.
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(num % 10, 'th')
    return '{:+,d}\\textsuperscript{{{}}}'.format(num, suffix)

def old_top_tropes_and_increment(number_of_items):
    def _calculate_increment_from_old(trope, dbtropes_count, tropescraper_count):
        if trope not in tropescraper_count:
            return '--'

        former_count = dbtropes_count[trope]
        current_count = tropescraper_count[trope]
        increment = ((current_count - former_count) / former_count) * 100.0
        return '{:+,.1f}\\%'.format(increment, grouping=True)

    def _calculate_current_position_from_old(trope, tropescraper_count, top_films_tropescrapper):
        if trope not in tropescraper_count:
            return '--'

        current_position = top_films_tropescrapper.index(trope)
        return ordinal(current_position)

    dbtropes_count = dbtropes_dataset_count_by_trope
    tropescraper_count = tropescraper_dataset_count_by_trope

    top_films_dbtropes = sorted(dbtropes_count.keys(), key=lambda x: dbtropes_count[x],
                                reverse=True)[:number_of_items]
    tropes_top_dbtropes = list(map(lambda x: dbtropes_count[x], top_films_dbtropes))
    tropes_top_count_tropescraper = list(map(lambda x: tropescraper_count[x] if x in tropescraper_count else 0,
                                             top_films_dbtropes))

    top_films_tropescrapper = sorted(tropescraper_count.keys(), key=lambda x: tropescraper_count[x],
                                     reverse=True)

    increment = list(map(lambda x: _calculate_increment_from_old(x, dbtropes_count, tropescraper_count),
                         top_films_dbtropes))
    positions = list(map(lambda x: _calculate_current_position_from_old(x, tropescraper_count, top_films_tropescrapper),
                         top_films_dbtropes))

    #def format_normal(x):
    #    return '{}'.format(x)

    #def format_color(x):
    #    return '\\textcolor{{red}}{{{}}}'.format(x) if x in common_tropes else format_normal(x)

    dataframe = pd.DataFrame.from_dict(OrderedDict([
        ('Key1', top_films_dbtropes), ('Count1', tropes_top_dbtropes), ('Count2', tropes_top_count_tropescraper),
        ('Increment', increment), ('CurrentPos', positions)
    ]))
    header = ['Trope', 'Films ({})'.format(DBTROPES_DATE), 'Films ({})'.format(TROPESCRAPER_DATE),
              'Increment', 'Moves to'.format(TROPESCRAPER_DATE)]
    formatters = {}
    display(Latex(dataframe.to_latex(escape=False, header=header, formatters=formatters)))



if __name__ == '__main__':
    old_top_tropes_and_increment(50)
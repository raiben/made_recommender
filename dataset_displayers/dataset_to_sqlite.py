import csv
import os
import sqlite3

from tabulate import tabulate

from common.base_script import BaseScript


class DatabaseBuilder(BaseScript):
    META_COLUMN_NAME = ['Id', 'NameTvTropes', 'NameIMDB', 'Votes', 'Year']
    RATING_COLUMN_NAME = 'Rating'
    INDEX_FIRST_TROPE = len(META_COLUMN_NAME) + 1

    def __init__(self, database_file, extended_information_csv_file):
        self.database_file = database_file
        self.extended_information_csv_file = extended_information_csv_file
        self.connection = None

    def build_database(self):
        self._remove_database()
        self._create_database()
        self._write_database_content()

    def display_statistics(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.database_file)

        self._show_query('Data imported', ['#different films '], 'SELECT count(*) FROM film')
        self._show_query('Data imported', ['#different tropes'], 'SELECT count(*) FROM trope')
        self._show_query('Data imported', ['#tropes in films '], 'SELECT count(*) FROM trope_by_film')

        self._show_query('Films by genre:', ['genre', '#films'],
                         'SELECT trope.name, count(*) '
                         'FROM trope,trope_by_film '
                         'where trope.name=trope_by_film.trope and trope.is_genre = "1" '
                         'group by trope', (), 0, 1000)

        self._show_query('Tropes by year:', ['year', '#tropes found'],
                         'SELECT year, count(*) '
                         'FROM film, trope, trope_by_film '
                         'where trope.name=trope_by_film.trope and film.name_tvtropes=trope_by_film.film '
                         'group by year', (), 0, 1000)

    def _write_database_content(self):
        with open(self.extended_information_csv_file) as file:
            self._track_step(u'Reading first line and extracting information')
            first_line = file.readline().replace('\n', '')

            columns = first_line.split(',')
            insert_trope_query = 'INSERT INTO trope(name, is_genre, column_index) VALUES(?, ?, ?)'
            trope_names = columns[self.INDEX_FIRST_TROPE:]
            for index, trope_name in enumerate(trope_names):
                is_genre = 1 if trope_name.startswith('genre_') else 0
                self.crud(insert_trope_query, (trope_name, is_genre, index))
                if index % 1000 == 0:
                    self._track_message('Inserting {} tropes'.format(index))

            insert_film_query = 'INSERT INTO film(name_tvtropes, id_imdb, name_imdb, votes, year, rating) ' \
                                'VALUES(?, ?, ?, ?, ?, ?)'
            insert_trope_by_film_query = 'INSERT INTO trope_by_film(film, trope) VALUES(?, ?)'

            line = file.readline()
            index = 0
            while line:
                line = line.replace('\n', '')
                items = list(csv.reader([line]))[0]
                id_imdb = items[0]
                name_tvtropes = items[1]
                name_imdb = items[2]
                if items[3] != '':
                    rating = float(items[3])
                    votes = int(float(items[4]))
                    year = int(float(items[5]))
                    # print(name_tvtropes)
                    self.crud(insert_film_query, (name_tvtropes, id_imdb, name_imdb, votes, year, rating))

                    indices = [i for i, x in enumerate(items[self.INDEX_FIRST_TROPE:]) if x == '1']
                    for trope_index in indices:
                        trope_name = trope_names[trope_index]
                        self.crud(insert_trope_by_film_query, (name_tvtropes, trope_name))

                line = file.readline()
                index += 1
                if index % 100 == 0:
                    self._track_message('Inserting {} films'.format(index))

            pass

    def _remove_database(self):
        self._track_step('Removing database')
        if os.path.exists(self.database_file):
            os.remove(self.database_file)
        else:
            self._track_message('No database found. Running the script for the first time...')

    def _create_database(self):
        self._track_step('Creating database')
        self.connection = sqlite3.connect(self.database_file)

        sql_create_film_table = '''CREATE TABLE IF NOT EXISTS film (
            name_tvtropes text PRIMARY KEY, id_imdb text NOT NULL, name_imdb text NOT NULL, rating real NOT NULL, 
            votes integer NOT NULL, year integer NOT_NULL);'''
        self.create_table(sql_create_film_table)

        sql_create_trope_table = '''CREATE TABLE IF NOT EXISTS trope (
            name text PRIMARY KEY, is_genre integer NOT NULL, column_index integer NOT NULL);'''
        self.create_table(sql_create_trope_table)

        sql_create_trope_by_film_table = '''CREATE TABLE IF NOT EXISTS trope_by_film (
                film text NOT NULL, trope text NOT NULL, 
                FOREIGN KEY (film) REFERENCES film(name_tvtropes), FOREIGN KEY (trope) REFERENCES trope(name));'''
        self.create_table(sql_create_trope_by_film_table)

        self._track_message('Database created')

    def create_table(self, create_table_sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
        except sqlite3.Error as exception:
            self._track_error(exception)

    def crud(self, sql, arguments):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, arguments)
            self.connection.commit()
        except sqlite3.Error as exception:
            self._track_error(exception)


if __name__ == "__main__":
    builder = DatabaseBuilder(
        '/Users/phd/workspace/made/made_recommender/datasets/films_and_tropes.db',
        '/Users/phd/workspace/made/made_recommender/datasets/film_extended_information_unique_values.csv')
    #builder.build_database()
    builder.display_statistics()

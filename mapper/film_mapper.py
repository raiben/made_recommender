import bz2
import csv
import difflib
import io
import json
import re
from collections import OrderedDict

from common.base_script import BaseScript


class MapperUtils(object):
    @staticmethod
    def normalize_name(name):
        name = re.sub('&', ' and ', name)
        name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1 \2', name).lower()
        name = re.sub('[^a-z0-9 ]+', '', name)
        name = re.sub('([^\\s])([0-9]+)', r'\1 \2', name)
        name = re.sub(' +', ' ', name)
        return name

    @staticmethod
    def similarity(source, target):
        seq = difflib.SequenceMatcher(None, source, target)
        return seq.ratio() * 100


class FilmInIMDB(object):
    def __init__(self, id, type, title, original_title, is_adult, start_year, end_year, minutes, genres):
        self.id = id
        self.type = type
        self.title = title
        self.original_title = original_title
        self.is_adult = is_adult
        self.start_year = start_year
        self.end_year = end_year
        self.minutes = minutes
        self.genres = self._split_genres(genres)
        self.normalized_title = MapperUtils.normalize_name(self.title)
        self.normalized_original_title = MapperUtils.normalize_name(self.original_title)
        self.votes = 0
        self.rating = 0

    @staticmethod
    def _split_genres(genres):
        if genres is None:
            return []
        return genres.replace('\n', '').split(',')


class FilmMapper(BaseScript):
    EXCLUDED_ENTRY_TYPES = ['tvEpisode', 'tvSeries', 'tvSpecial', 'tvShort', 'videoGame', 'tvMiniSeries',
                            'titleType']
    INCLUDE_FILMS_FROM_IMDB_WITHOUT_YEAR = False

    def __init__(self, tvtropes_films_file, imdb_titles_file, imdb_ratings_file, target_dataset, remove_ambiguities):
        parameters = dict(tvtropes_films_file_name=tvtropes_films_file, imdb_titles_file=imdb_titles_file,
                          imdb_ratings_file=imdb_ratings_file, target_dataset=target_dataset,
                          excluded_entry_types=self.EXCLUDED_ENTRY_TYPES,
                          include_films_from_imdb_without_year=self.INCLUDE_FILMS_FROM_IMDB_WITHOUT_YEAR,
                          remove_ambiguities=remove_ambiguities)

        BaseScript.__init__(self, parameters)

        self.tvtropes_films_file = tvtropes_films_file
        self.imdb_titles_file = imdb_titles_file
        self.imdb_ratings_file = imdb_ratings_file
        self.target_dataset_without_extension = target_dataset.split('.')[0]
        self.remove_ambiguities = remove_ambiguities

        self.film_list = []
        self.films_in_imdb = []
        self.films_in_imdb_hash = {}

    def run(self):
        self._load_information_from_imdb_dataset()
        self._load_information_from_tvtropes_dataset()
        self._map_films()
        self._write_dataset()
        self._finish_and_summary()

    def _load_information_from_imdb_dataset(self):
        self.films_in_imdb = []
        self.films_in_imdb_by_id = {}
        self.films_in_imdb_by_year = {}
        self.films_in_imdb_by_name = {}
        types = set()

        self._info(f'Loading basic information from IMDb dataset: {self.imdb_titles_file}')
        with open(self.imdb_titles_file, 'r', encoding='utf-8') as films_imdb_titles:
            imdb_lines_counter = 0
            for line in films_imdb_titles:
                try:
                    components = line.split('\t')
                    types.add(components[1])
                    if self._is_included_due_type(components) and self._is_included_due_start_year(components):
                        film_in_imdb = FilmInIMDB(*components)

                        self.films_in_imdb.append(film_in_imdb)

                        year = film_in_imdb.start_year
                        name = film_in_imdb.normalized_title
                        original_name = film_in_imdb.normalized_original_title

                        self.films_in_imdb_by_id[film_in_imdb.id] = film_in_imdb

                        if not year in self.films_in_imdb_by_year:
                            self.films_in_imdb_by_year[year] = {}
                        if not name in self.films_in_imdb_by_year[year]:
                            self.films_in_imdb_by_year[year][name] = []
                        self.films_in_imdb_by_year[year][name].append(film_in_imdb)
                        if not original_name in self.films_in_imdb_by_year[year]:
                            self.films_in_imdb_by_year[year][original_name] = []
                        if film_in_imdb not in self.films_in_imdb_by_year[year][original_name]:
                            self.films_in_imdb_by_year[year][original_name].append(film_in_imdb)

                        if not name in self.films_in_imdb_by_name:
                            self.films_in_imdb_by_name[name] = []
                        self.films_in_imdb_by_name[name].append(film_in_imdb)
                        if not original_name in self.films_in_imdb_by_name:
                            self.films_in_imdb_by_name[original_name] = []
                        if film_in_imdb not in self.films_in_imdb_by_name[original_name]:
                            self.films_in_imdb_by_name[original_name].append(film_in_imdb)

                        if len(self.films_in_imdb) % 50000 == 0:
                            self._info(f'{len(self.films_in_imdb)} films read')

                except Exception as exception:
                    self._track_error(f'Exception in line {line}. {exception}')
                finally:
                    imdb_lines_counter += 1

            self._add_to_summary('imdb_lines_counter', imdb_lines_counter)
            self._add_to_summary('imdb_films_considered', len(self.films_in_imdb))

        self._info(f'Adding ratings and votes from IMDb dataset: {self.imdb_ratings_file}')
        with open(self.imdb_ratings_file, 'r') as films_imdb_ratings:
            for line in films_imdb_ratings:
                try:
                    components = line.split('\t')
                    id = components[0]
                    rating = components[1]
                    votes = components[2]

                    if id in self.films_in_imdb_by_id:
                        self.films_in_imdb_by_id[id].rating = float(rating)
                        self.films_in_imdb_by_id[id].votes = float(votes)

                except Exception as exception:
                    self._track_error(f'Exception in line {line}. {exception}')

    def _is_included_due_type(self, components):
        return components[1] not in self.EXCLUDED_ENTRY_TYPES

    def _is_included_due_start_year(self, components):
        return self.INCLUDE_FILMS_FROM_IMDB_WITHOUT_YEAR or len(components[5]) == 4

    def _load_information_from_tvtropes_dataset(self):
        with open(self.tvtropes_films_file, 'r') as films_tvtropes:
            self.tropes_by_film = json.load(films_tvtropes)

    def _map_films(self):
        self.tvtropes_imdb_map = {}

        for film_name_tvtropes in self.tropes_by_film:
            self.tvtropes_imdb_map[film_name_tvtropes] = []

            if self._contains_year(film_name_tvtropes):
                year = film_name_tvtropes[-4:]
                name = MapperUtils.normalize_name(film_name_tvtropes[:-4])
                if year in self.films_in_imdb_by_year and name in self.films_in_imdb_by_year[year]:
                    self.tvtropes_imdb_map[film_name_tvtropes].extend(self.films_in_imdb_by_year[year][name])
            else:
                name = MapperUtils.normalize_name(film_name_tvtropes)
                if name in self.films_in_imdb_by_name:
                    self.tvtropes_imdb_map[film_name_tvtropes].extend(self.films_in_imdb_by_name[name])

        self._add_to_summary('Films matched times: 0', len(self._matches_equal(0)))
        self._add_to_summary('Films matched times: 1', len(self._matches_equal(1)))
        self._add_to_summary('Films matched times: 2', len(self._matches_equal(2)))
        self._add_to_summary('Films matched times: 3', len(self._matches_equal(3)))
        self._add_to_summary('Films matched times: 4+', len(self._matches_equal_or_higher(4)))

        if self.remove_ambiguities:
            self._info(f'Reducing ambiguities by selecting films with more popularity')
            for key in self.tvtropes_imdb_map:
                if len(self.tvtropes_imdb_map[key]):
                    sorted_films_by_popularity = sorted(self.tvtropes_imdb_map[key], key=lambda x: x.votes,
                                                        reverse=True)
                    self.tvtropes_imdb_map[key] = sorted_films_by_popularity[0:1]
            self._add_to_summary('Films matched times: 1 (remove ambiguity)', len(self._matches_equal(1)))

    def safe_division(self, x, y):
        if y == 0:
            return 0
        return x / y

    @staticmethod
    def _contains_year(film_name):
        return re.fullmatch('^.+[1,2][0-9]{3}$', film_name)

    def _matches_equal(self, occurrences):
        return [name for name in self.tvtropes_imdb_map if len(self.tvtropes_imdb_map[name]) == occurrences]

    def _matches_equal_or_higher(self, occurrences):
        return [name for name in self.tvtropes_imdb_map if len(self.tvtropes_imdb_map[name]) >= occurrences]

    def _write_dataset(self):
        films_matched = self._matches_equal(1)

        self._info('Writing to a JSON file')
        list_to_store = []
        for film_name in films_matched:
            film = self.tvtropes_imdb_map[film_name][0]
            film_tropes = self.tropes_by_film[film_name]

            film_dictionary = OrderedDict()
            film_dictionary['id'] = film.id
            film_dictionary['name'] = film_name
            film_dictionary['title'] = film.title
            film_dictionary['rating'] = film.rating
            film_dictionary['votes'] = film.votes
            film_dictionary['start_year'] = film.start_year
            film_dictionary['tropes'] = sorted(list(film_tropes))
            film_dictionary['genres'] = sorted(list(film.genres))
            list_to_store.append(film_dictionary)

        self.json_content = json.dumps(list_to_store)
        self._add_to_summary('uncompressed_generated_json_file_size_bytes', len(self.json_content))
        json_compressed_path = f'{self.target_dataset_without_extension}.json.bz2'
        self.json_compressed_content = bz2.compress(self.json_content.encode('UTF-8'))
        with open(json_compressed_path, 'wb') as compressed_file:
            compressed_file.write(self.json_compressed_content)

        self._add_to_summary('compressed_generated_json_file_path', json_compressed_path)
        self._add_to_summary('compressed_generated_json_file_size_bytes', len(self.json_compressed_content))


        self._info('Writing to a CSV file')
        all_tropes_in_order = sorted(set([trope for tropes in self.tropes_by_film.values() for trope in tropes]))
        all_genres_in_order = sorted(set([genre for films in self.tvtropes_imdb_map.values()
                                          if len(films) for genre in films[0].genres]))

        output = io.StringIO()
        writer = csv.writer(output)
        header = self.get_header(all_tropes_in_order, all_genres_in_order)
        writer.writerow(header)
        number_of_rows = 0
        for film in films_matched:
            row = self.get_row_for_film(film, all_tropes_in_order, all_genres_in_order)
            writer.writerow(row)
            number_of_rows += 1
            if number_of_rows % 500 == 0:
                self._info(f'{number_of_rows} rows written')

        self.uncompressed_content = output.getvalue()
        self._add_to_summary('uncompressed_generated_csv_file_size_bytes', len(self.uncompressed_content))

        compressed_path = f'{self.target_dataset_without_extension}.csv.bz2'
        self.compressed_content = bz2.compress(self.uncompressed_content.encode('UTF-8'))
        with open(compressed_path, 'wb') as compressed_file:
            compressed_file.write(self.compressed_content)

        self._add_to_summary('compressed_generated_csv_file_path', compressed_path)
        self._add_to_summary('compressed_generated_csv_file_size_bytes', len(self.compressed_content))


    def get_header(self, tropes, genres):
        row = ['Id', 'NameTvTropes', 'NameIMDB', 'Rating', 'Votes', 'Year']
        row.extend([trope for trope in tropes])
        row.extend([f'[GENRE]{genre}' for genre in genres])
        return row

    def get_row_for_film(self, film_name, all_tropes, all_genres):
        film = self.tvtropes_imdb_map[film_name][0]
        film_tropes = self.tropes_by_film[film_name]

        row = [film.id, film_name, film.title, film.rating, film.votes, film.start_year]
        row.extend([1 if trope in film_tropes else 0 for trope in all_tropes])
        row.extend([1 if genre in film.genres else 0 for genre in all_genres])
        return row

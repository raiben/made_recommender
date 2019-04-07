import csv
import difflib
import json
import re
import sys


class FilmRelevantInformation(object):
    def __init__(self, name_in_tvtropes=None, name_in_imdb=None, imdb_id=None, year=None, genres=None, tropes=None,
                 rating=None, votes=None, boxoffice=None, type=None, incidences=None):
        self.name_in_tvtropes = name_in_tvtropes
        self.name_in_imdb = name_in_imdb
        self.imdb_id = imdb_id
        self.year = year
        self.genres = genres
        self.tropes = tropes
        self.rating = rating
        self.votes = votes
        self.boxoffice = boxoffice
        self.type = type
        self.incidences = incidences


class FilmInIMDB(object):
    def __init__(self, id, type, title, original_title, is_adult, start_year, end_year, minutes, genres):
        self.id = id
        self.type = type
        self.title = title
        self.original_title = original_title
        self.start_year = start_year
        self.genres = split_genres(genres)
        self.normalized_title = convert(self.title)


def contains_year(film_name):
    return re.fullmatch('^.+[1,2][0-9]{3}$', film_name)


class FilmFeaturesGenerator(object):
    def __init__(self, tvtropes_films_file_name, imdb_basic_film_titles_file_name, imdb_film_ratings_file_name,
                 expected_films_in_imdb, target_dataset_unique_occurrences):
        self.tvtropes_films_file_name = tvtropes_films_file_name
        self.imdb_basic_film_titles_file_name = imdb_basic_film_titles_file_name
        self.imdb_film_ratings_file_name = imdb_film_ratings_file_name
        self.expected_films_in_imdb = expected_films_in_imdb
        self.target_dataset_unique_occurrences = target_dataset_unique_occurrences
        self.film_list = []

    def run(self):
        with open(self.tvtropes_films_file_name, "r") as tvtropes_films_file:
            tvtropes_films = json.load(tvtropes_films_file)

        for film_name in tvtropes_films:
            film_information = FilmRelevantInformation(name_in_tvtropes=film_name, tropes=tvtropes_films[film_name])
            self.film_list.append(film_information)

        del tvtropes_films

        films_in_imdb = []
        indexed_films_in_imdb = {}
        types = set()
        with open(self.imdb_basic_film_titles_file_name, 'r') as films_imdb_file_titles:
            for line in films_imdb_file_titles:
                try:
                    components = line.split('\t')
                    types.add(components[1])
                    if components[1] not in ['tvEpisode', 'video', 'tvSeries', 'tvSpecial', 'tvShort', 'videoGame',
                                             'tvMiniSeries', 'titleType']:
                        film_in_imdb = FilmInIMDB(*components)
                        indexed_films_in_imdb[film_in_imdb.id] = film_in_imdb
                        films_in_imdb.append(film_in_imdb)
                        if len(films_in_imdb) % 10000 == 0:
                            percent = 100 * len(films_in_imdb) / self.expected_films_in_imdb
                            sys.stdout.write("\r{}%".format(round(percent, 3)))
                except Exception as exception:
                    print('Exception in line {}. {}'.format(line, exception))
                    print("line:")

        print(types)

        films_in_imdb_hash = {}
        for film_in_imdb in films_in_imdb:
            if film_in_imdb.normalized_title not in films_in_imdb_hash:
                films_in_imdb_hash[film_in_imdb.normalized_title] = []
            films_in_imdb_hash[film_in_imdb.normalized_title].append(film_in_imdb)

        counter = 0
        for film in self.film_list:
            normalized_title = convert(film.name_in_tvtropes)

            matches = []
            if normalized_title in films_in_imdb_hash:
                for film_in_imdb in films_in_imdb_hash[normalized_title]:
                    film.name_in_imdb = film_in_imdb.title
                    film.imdb_id = film_in_imdb.id
                    film.year = film_in_imdb.start_year
                    film.genres = film_in_imdb.genres
                    film.type = film_in_imdb.type
                    matches.append(film.imdb_id)

            if len(matches) == 0:
                film.incidences = "No occurrences found"
            elif len(matches) > 1:
                film.incidences = "Multiple occurrences found: [{}]".format(", ".join(matches))

            print('#{} - {}'.format(counter, json.dumps(film.__dict__, sort_keys=True)))
            counter += 1

        unique_films = [film for film in self.film_list if film.incidences is None]
        films_not_found = [film for film in self.film_list if film.incidences == 'No occurrences found']
        multiple_films = [film for film in self.film_list if film.incidences is not None and
                          "Multiple occurrences found" in film.incidences]

        print('Summary: {} matched films, {} unmatched films, {} ambiguous film names'.format(
            len(unique_films), len(films_not_found), len(multiple_films)
        ))

        all_unique_titles_in_imdb = [film.name_in_imdb for film in unique_films]

        print("Handling years in name")

        for film in [film for film in films_not_found if contains_year(film.name_in_tvtropes)]:
            normalized_title = convert(film.name_in_tvtropes[:-4])
            year = film.name_in_tvtropes[-4:]

            matches = []
            if normalized_title in films_in_imdb_hash:
                for film_in_imdb in films_in_imdb_hash[normalized_title]:
                    if film_in_imdb.start_year == year:
                        film.name_in_imdb = film_in_imdb.title
                        film.imdb_id = film_in_imdb.id
                        film.year = film_in_imdb.start_year
                        film.genres = film_in_imdb.genres
                        film.type = film_in_imdb.type
                        matches.append(film.imdb_id)

                        if film.name_in_imdb in all_unique_titles_in_imdb:
                            print("CAREFUL with name {}".format(film.name_in_imdb))

            if len(matches) == 0:
                film.incidences = "No occurrences found"
            if len(matches) == 1:
                film.incidences = None
            elif len(matches) > 1:
                film.incidences = "Multiple occurrences found: [{}]".format(", ".join(matches))

            print('#{} - {}'.format(counter, json.dumps(film.__dict__, sort_keys=True)))
            counter += 1

        unique_films_with_year = [film for film in films_not_found if film.incidences is None]
        for film in unique_films_with_year:
            films_not_found.remove(film)
            unique_films.append(film)

        print('Summary: {} matched films, {} unmatched films, {} ambiguous film names'.format(
            len(unique_films), len(films_not_found), len(multiple_films)
        ))

        print("Adding rating...")

        imdb_ids_hash = {}
        for film in unique_films:
            imdb_ids_hash[film.imdb_id] = film

        with open(self.imdb_film_ratings_file_name, 'r') as imdb_film_ratings_file:
            for line in imdb_film_ratings_file:
                try:
                    components = line.split('\t')
                    id = components[0]
                    rating = components[1]
                    votes = components[2]

                    if id in imdb_ids_hash:
                        imdb_ids_hash[id].rating = float(rating)
                        imdb_ids_hash[id].votes = float(votes)

                except Exception as exception:
                    print('Exception in line {}. {}'.format(line, exception))
                    print("line:")

        print('Writing to CSV')

        tropes_in_unique_films_set = set()
        genres_in_unique_films_set = set()

        for film in unique_films:
            tropes_in_unique_films_set.update(film.tropes)
            genres_in_unique_films_set.update(film.genres)

        tropes_in_unique_films = sorted(list(tropes_in_unique_films_set))
        genres_in_unique_films = sorted(list(genres_in_unique_films_set))

        with open(self.target_dataset_unique_occurrences, 'w') as csvfile:
            writer = csv.writer(csvfile)
            header = self.get_header(tropes_in_unique_films, genres_in_unique_films)
            writer.writerow(header)
            for film in unique_films:
                row = self.get_row_for_film(film, tropes_in_unique_films, genres_in_unique_films)
                writer.writerow(row)

        # print('Trying to steal some films from the darkness...')
        # for film in films_not_found:
        #     normalized_title = convert(film.name_in_tvtropes)
        #
        #     matches = []
        #     best_matches = []
        #     best_ratio = 0
        #     for film_in_imdb in films_in_imdb:
        #         ratio = similarity(normalized_title, film_in_imdb.normalized_title)
        #         if ratio == best_ratio:
        #             best_matches.append(film_in_imdb)
        #
        #         if ratio > best_ratio:
        #             best_ratio = ratio
        #             best_matches = [film_in_imdb]
        #
        #     if len(best_matches == 1):
        #         film.name_in_imdb = best_matches[0].title
        #         film.imdb_id = best_matches[0].id
        #         film.year = best_matches[0].end_year
        #         film.genres = best_matches[0].genres
        #         film.type = best_matches[0].type
        #         matches.append(best_matches[0].imdb_id)
        #         film.incidences = 'Matching ratio = {}: {}'.format(best_ratio, best_matches[0].title)
        #     elif len(best_matches > 1):
        #         film.incidences = 'Multiple candidates for ratio = {}: {}'.format(
        #             best_ratio, ", ".join([match.name for match in best_matches]))
        #
        #     print('#{} - {}'.format(counter, json.dumps(film.__dict__, sort_keys=True)))
        #     counter += 1

    def get_row_for_film(self, film, tropes, genres):
        row = [film.imdb_id, film.name_in_tvtropes, film.name_in_imdb, film.rating, film.votes, film.year]
        row.extend([1 if trope in film.tropes else 0 for trope in tropes])
        row.extend([1 if genre in film.genres else 0 for genre in genres])
        return row

    def get_header(self, tropes, genres):
        row = ['Id', 'NameTvTropes', 'NameIMDB', 'Rating', 'Votes', 'Year']
        row.extend([trope for trope in tropes])
        row.extend(['genre_' + genre for genre in genres])
        return row


def split_genres(genres):
    if genres is None:
        return []
    return genres.replace('\n', '').split(',')


def convert(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1 \2', name).lower()
    name = re.sub(' +', ' ', name)
    name = re.sub('[^a-z0-9 ]+', '', name)
    return name


def similarity(source, target):
    seq = difflib.SequenceMatcher(None, source, target)
    return seq.ratio() * 100


if __name__ == "__main__":
    # tvtropes_films_file_name = './data/all_films_and_their_tropes.json'
    tvtropes_films_file_name = '/Users/phd/workspace/made/made_tropes/scripts/scrapping_cache/1/all_films_and_their_tropes_201902.json'
    matcher = FilmFeaturesGenerator(
        tvtropes_films_file_name=tvtropes_films_file_name,
        imdb_basic_film_titles_file_name='/Users/phd/Downloads/title.basics.tsv',
        imdb_film_ratings_file_name='/Users/phd/Downloads/title.ratings.tsv',
        expected_films_in_imdb=1711798,
        target_dataset_unique_occurrences='./data/film_extended_information_unique_values.csv'
    )

    matcher.run()

import sqlite3

from common.base_script import BaseScript


class Displayer(BaseScript):
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)

    def search_genres(self, search_query, page=0, results=10):
        search_query = 'genre_%{}%'.format(search_query)
        self._show_query('', ['genre'],
                         "SELECT DISTINCT name from trope "
                         "where name LIKE ? and is_genre='1' "
                         "order by name "
                         "COLLATE NOCASE",
                         (search_query,), page, results)

    def search_tropes(self, search_query, page=0, results=10):
        search_query = '%{}%'.format(search_query)

        query = '''
        -- filter tropes by name and sort by number of films and avg_rating
        SELECT trope_by_film.trope, count(trope_by_film.film) AS n_films, 
               avg(rating) AS avg_rating, group_concat(trope_by_film.film, ', ')
        FROM trope_by_film,
             trope,
             film
        WHERE trope_by_film.trope = trope.name
          AND trope_by_film.film = film.name_tvtropes
          AND trope_by_film.trope LIKE ? COLLATE NOCASE
        GROUP BY trope_by_film.trope
        ORDER BY avg_rating DESC, n_films DESC'''

        self._show_query('', ['trope', '# of films', 'AVG rating'],
                         query, (search_query,), page, results)



    def search_movies(self, search_query, page=0, results=10):
        search_query = '%{}%'.format(search_query)

        query = '''
        -- filter tropes by name and sort by number of films and avg_rating
        SELECT trope_by_film.film, film.name_imdb, count(trope_by_film.trope) AS n_tropes, 
               group_concat(trope_by_film.trope, ', ')
        FROM trope_by_film,
             trope,
             film
        WHERE trope_by_film.trope = trope.name
          AND trope_by_film.film = film.name_tvtropes
          AND (trope_by_film.film LIKE ? COLLATE NOCASE OR film.name_imdb LIKE ? COLLATE NOCASE)
        GROUP BY trope_by_film.film
        ORDER BY n_tropes DESC'''

        self._show_query('', ['Short name', 'Long Name', '# tropes', 'tropes'],
                         query, (search_query,search_query,), page, results)


if __name__ == "__main__":
    displayer = Displayer(
        '/Users/phd/workspace/made/made_recommender/datasets/films_and_tropes.db')
    displayer.search_genres(search_query='', page=0, results=50)
    displayer.search_tropes(search_query='AdaptationDistillation', page=0, results=7)
    displayer.search_movies(search_query='avengers', page=0, results=7)

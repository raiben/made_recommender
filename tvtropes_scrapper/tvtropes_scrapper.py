import base64
import json
import os
from collections import OrderedDict
from time import sleep

import requests
from lxml import html


class TVTropesScrapper(object):
    MAIN_SEARCH = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/Film'
    BASE_FILM_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Film/'
    BASE_MAIN_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/'

    def __init__(self, directory, session):
        self.directory_name = directory
        self.session = session
        self.films = None
        self.tropes = None
        self.tropes_by_film = OrderedDict()

    def run(self):
        self.extract_film_ids()
        self.extract_tropes()
        self.write_result()

    def extract_film_ids(self):
        self.films = set()
        main_url = self.MAIN_SEARCH
        category_ids = self.get_links_from_url(main_url, '/Main/')

        for category_id in category_ids:
            url = self.BASE_MAIN_URL + category_id
            film_ids = self.get_links_from_url(url, '/Film/')
            self.films.update(film_ids)

    def extract_tropes(self):
        self.tropes = set()
        self.tropes_by_film = OrderedDict()
        sorted_films = sorted(list(self.films))
        print('Found {} films'.format(len(sorted_films)))
        counter = 0
        for film in sorted_films:
            counter += 1
            print('Status: {}/{} films'.format(counter, len(sorted_films)))
            self.get_tropes_by_film(film)

    def get_tropes_by_film(self, film):
        url = self.BASE_FILM_URL + film
        trope_ids = self.get_links_from_url(url, '/Main/', only_article=True)
        print("Summary for film: {}".format(film))
        print("Tropes: {} items: {}".format(len(trope_ids), trope_ids))
        self.tropes.update(trope_ids)
        self.tropes_by_film[film] = sorted(trope_ids)

    def get_links_from_url(self, url, type, only_article=False):
        page = self.get_content_from_url(url)
        tree = html.fromstring(page)
        selector = '#main-article ul li a' if only_article else 'a'
        links = [element.get('href') for element in tree.cssselect('a') if element.get('href')]
        return [link.split('/')[-1] for link in links if type in link and 'action' not in link]

    def get_content_from_url(self, url):
        encoded_url = base64.b64encode(url.encode('utf-8')).decode('utf-8') + '.html'
        encoded_url = encoded_url.replace('/', '_')
        file_path = os.path.join(self.directory_name, self.session, encoded_url)

        if os.path.isfile(file_path):
            print('Retrieving URL from cache: {}'.format(url))
            with open(file_path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='ignore')

        print('Retrieving URL from tvtropes: {}'.format(url))
        sleep(0.5)
        page = requests.get(url)
        content = page.content
        with open(file_path, 'wb') as file:
            file.write(content)
            return content.decode('utf-8', errors='ignore')

    def write_result(self):
        file_path = os.path.join(self.directory_name, self.session, "all_films_and_their_tropes_201902.json")
        content = json.dumps(self.tropes_by_film, indent=2, sort_keys=True)
        with open(file_path, 'w') as file:
            file.write(content)


if __name__ == "__main__":
    scrapper = TVTropesScrapper(directory='/Users/phd/workspace/made/made_tropes/scripts/scrapping_cache', session='1')
    scrapper.run()

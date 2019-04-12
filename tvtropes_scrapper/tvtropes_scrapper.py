import base64
import datetime
import json
import os
from collections import OrderedDict
from time import sleep

import requests
from lxml import html

from common.base_script import BaseScript


class TVTropesScrapper(BaseScript):
    MAIN_SEARCH = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/Film'
    BASE_FILM_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Film/'
    BASE_MAIN_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/'
    TARGET_RESULT_FILE_TEMPLATE = 'all_films_and_their_tropes_{}.json'
    WAIT_TIME_BETWEEN_CALLS_IN_SECONDS = 0.5

    def __init__(self, directory, session):
        self.directory_name = directory
        self.session = session
        self._set_default_session_value_if_empty()
        self._build_required_directories()

        self.films = None
        self.tropes = None
        self.tropes_by_film = OrderedDict()

    def _build_required_directories(self):
        whole_path = os.path.join(self.directory_name, self.session)
        if not os.path.isdir(whole_path):
            self._track_step(f'Building directory: {whole_path}')
            os.makedirs(whole_path)

    def _set_default_session_value_if_empty(self):
        if not self.session:
            now = datetime.datetime.now()
            self.session = now.strftime('%Y%m%d_%H%M%S')

    def run(self):
        self._extract_film_ids()
        self._extract_tropes()
        self._write_result()

    def _extract_film_ids(self):
        self.films = set()
        main_url = self.MAIN_SEARCH
        category_ids = self.get_links_from_url(main_url, '/Main/')

        for category_id in category_ids:
            url = self.BASE_MAIN_URL + category_id
            film_ids = self.get_links_from_url(url, '/Film/')
            self.films.update(film_ids)

    def _extract_tropes(self):
        self.tropes = set()
        self.tropes_by_film = OrderedDict()
        sorted_films = sorted(list(self.films))
        self._track_step('Found {} films'.format(len(sorted_films)))
        counter = 0
        for film in sorted_films:
            counter += 1
            self._track_message('Status: {}/{} films'.format(counter, len(sorted_films)))
            self.get_tropes_by_film(film)

    def get_tropes_by_film(self, film):
        url = self.BASE_FILM_URL + film
        trope_ids = self.get_links_from_url(url, '/Main/', only_article=True)
        self._track_message("Summary for film: {}".format(film))
        self._track_message("Tropes: {} items: {}".format(len(trope_ids), trope_ids))
        self.tropes.update(trope_ids)
        self.tropes_by_film[film] = sorted(trope_ids)

    def get_links_from_url(self, url, type, only_article=False):
        page = self.get_content_from_url(url)
        tree = html.fromstring(page)
        selector = '#main-article ul li a' if only_article else 'a'
        links = [element.get('href') for element in tree.cssselect('a') if element.get('href')]
        return [link.split('/')[-1] for link in links if type in link and 'action' not in link]

    def get_content_from_url(self, url):
        encoded_url = self._build_encoded_url(url)
        file_path = os.path.join(self.directory_name, self.session, encoded_url)

        if os.path.isfile(file_path):
            print('Retrieving URL from cache: {}'.format(url))
            with open(file_path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='ignore')

        print('Retrieving URL from tvtropes: {}'.format(url))
        self._wait_between_calls_to_avoid_attacking()
        page = requests.get(url)
        content = page.content
        with open(file_path, 'wb') as file:
            file.write(content)
            return content.decode('utf-8', errors='ignore')

    @staticmethod
    def _build_encoded_url(url):
        encoded_url = base64.b64encode(url.encode('utf-8')).decode('utf-8') + '.html'
        encoded_url = encoded_url.replace('/', '_')
        return encoded_url

    def _wait_between_calls_to_avoid_attacking(self):
        sleep(self.WAIT_TIME_BETWEEN_CALLS_IN_SECONDS)

    def _write_result(self):
        target_file_name = self.TARGET_RESULT_FILE_TEMPLATE.format(self.session)
        file_path = os.path.join(self.directory_name, self.session, target_file_name)
        content = json.dumps(self.tropes_by_film, indent=2, sort_keys=True)
        with open(file_path, 'w') as file:
            file.write(content)


if __name__ == "__main__":
    scrapper = TVTropesScrapper(directory='/Users/phd/workspace/made/made_tropes/scripts/scrapping_cache', session='1')
    scrapper.run()

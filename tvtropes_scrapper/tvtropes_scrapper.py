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
    SESSION_DATETIME_FORMAT = '%Y%m%d_%H%M%S'

    MAIN_RESOURCE = '/Main/'
    FILM_RESOURCE = '/Film/'
    LINK_SELECTOR = 'a'
    LINK_SELECTOR_INSIDE_ARTICLE = '#main-article ul li a'
    LINK_ADDRESS_SELECTOR = 'href'
    EXTENSION = '.html'
    DEFAULT_ENCODING = 'utf-8'

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
            self.session = now.strftime(self.SESSION_DATETIME_FORMAT)

    def run(self):
        self._extract_film_ids()
        self._extract_tropes()
        self._write_result()

    def _extract_film_ids(self):
        self.films = set()
        main_url = self.MAIN_SEARCH
        category_ids = self.get_links_from_url(main_url, self.MAIN_RESOURCE)

        for category_id in category_ids:
            url = self.BASE_MAIN_URL + category_id
            film_ids = self.get_links_from_url(url, self.FILM_RESOURCE)
            self.films.update(film_ids)

    def _extract_tropes(self):
        self.tropes = set()
        self.tropes_by_film = OrderedDict()
        sorted_films = sorted(list(self.films))

        self._track_step('Found {} films'.format(len(sorted_films)))

        for counter, film in enumerate(sorted_films):
            self._track_message('Status: {}/{} films'.format(counter, len(sorted_films)))
            self._get_tropes_by_film(film)

    def _get_tropes_by_film(self, film):
        url = self.BASE_FILM_URL + film
        trope_ids = self.get_links_from_url(url, self.MAIN_RESOURCE, only_article=True)
        self._track_message("Summary for film: {}".format(film))
        self._track_message("Tropes: {} items: {}".format(len(trope_ids), trope_ids))
        self.tropes.update(trope_ids)
        self.tropes_by_film[film] = sorted(trope_ids)

    def get_links_from_url(self, url, type, only_article=False):
        page = self._get_content_from_url(url)
        tree = html.fromstring(page)
        selector = self.LINK_SELECTOR_INSIDE_ARTICLE if only_article else self.LINK_SELECTOR
        links = [element.get(self.LINK_ADDRESS_SELECTOR) for element in tree.cssselect(self.LINK_SELECTOR)
                 if element.get(self.LINK_ADDRESS_SELECTOR)]
        return [link.split('/')[-1] for link in links if type in link and 'action' not in link]

    def _get_content_from_url(self, url):
        encoded_url = self._build_encoded_url(url)
        file_path = os.path.join(self.directory_name, self.session, encoded_url)

        if os.path.isfile(file_path):
            self._track_message('Retrieving URL from cache: {}'.format(url))
            with open(file_path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='ignore')

        self._track_message('Retrieving URL from TVTropes: {}'.format(url))
        self._wait_between_calls_to_avoid_attacking()
        page = requests.get(url)
        content = page.content
        with open(file_path, 'wb') as file:
            file.write(content)
            return content.decode(self.DEFAULT_ENCODING, errors='ignore')

    def _build_encoded_url(self, url):
        encoded_url = base64.b64encode(url.encode(self.DEFAULT_ENCODING)).decode(self.DEFAULT_ENCODING) + self.EXTENSION
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
    sample_directory = '/Users/phd/workspace/made/made_tropes/scripts/scrapping_cache'
    sample_session = '1'

    scrapper = TVTropesScrapper(directory=sample_directory, session=sample_session)
    scrapper.run()

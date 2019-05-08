import base64
import bz2
import datetime
import json
import os
from collections import OrderedDict
from time import sleep

import requests
from lxml import html

from common.base_script import BaseScript


class TVTropesScraper(BaseScript):
    MAIN_SEARCH = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/Film'
    BASE_FILM_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Film/'
    BASE_MAIN_URL = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/'
    TARGET_RESULT_FILE_TEMPLATE = 'films_tropes_{}.json'

    WAIT_TIME_BETWEEN_CALLS_IN_SECONDS = 0.5
    SESSION_DATETIME_FORMAT = '%Y%m%d_%H%M%S'

    MAIN_RESOURCE = '/Main/'
    FILM_RESOURCE = '/Film/'
    LINK_SELECTOR = 'a'
    LINK_SELECTOR_INSIDE_ARTICLE = '#main-article ul li a'
    LINK_ADDRESS_SELECTOR = 'href'
    EXTENSION = '.html'
    COMPRESSED_EXTENSION = '.bz2'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, directory, session):
        self.directory_name = directory
        self.session = session
        self._set_default_session_value_if_empty()
        self._build_required_directories()

        self.films = None
        self.tropes = None
        self.tropes_by_film = OrderedDict()

    def _set_default_session_value_if_empty(self):
        if not self.session:
            now = datetime.datetime.now()
            self.session = now.strftime(self.SESSION_DATETIME_FORMAT)

    def _build_required_directories(self):
        whole_path = os.path.join(self.directory_name, self.session)
        if not os.path.isdir(whole_path):
            self._step(f'Building directory: {whole_path}')
            os.makedirs(whole_path)

    def run(self):
        self._extract_film_ids()
        self._extract_tropes()
        self._write_result()

    def _extract_film_ids(self):
        self.films = set()
        main_url = self.MAIN_SEARCH
        category_ids = self._get_links_from_url(main_url, self.MAIN_RESOURCE)

        for category_id in category_ids:
            url = self.BASE_MAIN_URL + category_id
            film_ids = self._get_links_from_url(url, self.FILM_RESOURCE)
            self.films.update(film_ids)

    def _extract_tropes(self):
        self.tropes = set()
        self.tropes_by_film = OrderedDict()
        sorted_films = sorted(list(self.films))

        self._step(f'Found {len(sorted_films)} films')

        for counter, film in enumerate(sorted_films):
            self._info(f'Status: {counter}/{len(sorted_films)} films')
            self._get_tropes_by_film(film)

    def _get_tropes_by_film(self, film):
        url = self.BASE_FILM_URL + film
        trope_ids = self._get_links_from_url(url, self.MAIN_RESOURCE, only_article=True)

        self._info(f'Film {film} ({len(trope_ids)} tropes): {trope_ids}')

        self.tropes.update(trope_ids)
        self.tropes_by_film[film] = sorted(trope_ids)

    def _get_links_from_url(self, url, link_type, only_article=False):
        page = self._get_content_from_url(url)
        tree = html.fromstring(page)
        selector = self.LINK_SELECTOR_INSIDE_ARTICLE if only_article else self.LINK_SELECTOR
        links = [element.get(self.LINK_ADDRESS_SELECTOR) for element in tree.cssselect(selector)
                 if element.get(self.LINK_ADDRESS_SELECTOR)]
        return [link.split('/')[-1] for link in links if link_type in link and 'action' not in link]

    def _get_content_from_url(self, url):
        encoded_url = self._build_encoded_url(url)
        file_path = os.path.join(self.directory_name, self.session, encoded_url)

        if self._file_exists(file_path):
            self._info(f'Retrieving URL from cache: {url}')
            content = self._read_file(file_path)
            return self._read_content_safely(content)

        self._info(f'Retrieving URL from TVTropes and storing in cache: {url}')
        self._wait_between_calls_to_avoid_attacking()
        page = requests.get(url)
        content = page.content
        self._write_file(content, file_path)
        return self._read_content_safely(content)

    @classmethod
    def _file_exists(cls, file_path):
        compressed_path = f'{file_path}{cls.COMPRESSED_EXTENSION}'
        return os.path.isfile(compressed_path)

    @classmethod
    def _read_file(cls, file_path):
        compressed_path = f'{file_path}{cls.COMPRESSED_EXTENSION}'
        with open(compressed_path, 'rb') as file:
            content = file.read()
        return bz2.decompress(content)

    @classmethod
    def _write_file(cls, content, file_path):
        compressed_path = f'{file_path}{cls.COMPRESSED_EXTENSION}'
        compressed_content = bz2.compress(content)
        with open(compressed_path, 'wb') as file:
            file.write(compressed_content)

    def _read_content_safely(self, content):
        return content.decode(self.DEFAULT_ENCODING, errors='ignore')

    def _build_encoded_url(self, url):
        encoded_url = base64.b64encode(url.encode(self.DEFAULT_ENCODING)).decode(self.DEFAULT_ENCODING) + self.EXTENSION
        return encoded_url.replace('/', '_')

    def _wait_between_calls_to_avoid_attacking(self):
        sleep(self.WAIT_TIME_BETWEEN_CALLS_IN_SECONDS)

    def _write_result(self):
        target_file_name = self.TARGET_RESULT_FILE_TEMPLATE.format(self.session)
        file_path = os.path.join(self.directory_name, self.session, target_file_name)
        self.step(f'Saving tropes by film into {file_path}')
        content = json.dumps(self.tropes_by_film, indent=2, sort_keys=True)
        byte_content = content.encode(self.DEFAULT_ENCODING)
        self._write_file(byte_content, file_path)

import bz2
import gzip
import os
from collections import namedtuple
from io import StringIO
from operator import attrgetter

import pandas as pd
from pandas._libs import json

TropesSimilarityEntity = namedtuple('TropesSimilarityEntity', 'name rating n_tropes overlap jaccard common_tropes')


class TropesSimilarityChecker(object):
    def __init__(self):
        self.extended_dataframe = None
        self.films = None

    def load_extended_dataset_csv(self, source_extended_dataset):
        self.source_extended_dataset = source_extended_dataset
        self._load_dataframe()

    def _load_dataframe(self):
        self.extended_dataframe = None
        hdf_name = self.source_extended_dataset.replace('.csv.bz2', '.h5')
        if os.path.isfile(hdf_name):
            self.extended_dataframe = pd.read_hdf(hdf_name)
        else:
            with open(self.source_extended_dataset, 'rb') as file:
                compressed_content = file.read()
            csv_content = bz2.decompress(compressed_content)
            self.extended_dataframe = pd.read_csv(StringIO(csv_content.decode('utf-8')))

    def load_extended_dataset_json(self, source_extended_dataset):
        self.source_extended_dataset = source_extended_dataset
        self._build_from_json()

    def _build_from_json(self):

        with bz2.open(self.source_extended_dataset, "rb") as f:
            content = f.read()
        json_bytes = content.decode('utf-8')
        self.films = json.loads(json_bytes)


    def get_top_films_by_simmilarity(self, trope_list, number_of_results, ignore_genres=False):
        original_trope_set = set(trope_list)
        if ignore_genres:
            original_trope_set = set([trope for trope in original_trope_set if '[GENRE]' not in trope])

        films = []

        if self.films is not None:
            for film_dictionary in self.films:
                compared_trope_set = film_dictionary['tropes']
                if ignore_genres:
                    compared_trope_set = set([trope for trope in compared_trope_set if '[GENRE]' not in trope])

                overlap = self.get_overlap_similarity(original_trope_set, compared_trope_set)
                jaccard = self.get_jaccard_similarity(original_trope_set, compared_trope_set)
                film = TropesSimilarityEntity(film_dictionary['name'], film_dictionary['rating'],
                                              len(compared_trope_set), overlap, jaccard,
                                              original_trope_set.intersection(compared_trope_set))
                films.append(film)
                #if len(films) % 100 == 0:
                #    print(len(films))

            top_overlap = sorted(films, key=attrgetter('overlap', 'rating'), reverse=True)[0:number_of_results]
            overlap_dataframe = pd.DataFrame([{'Similarity (Overlap)': "{:.2f}".format(film.overlap * 100) + '%',
                                               'Film': film.name, 'Rating': film.rating, 'N. tropes': film.n_tropes,
                                               'Common tropes': ', '.join(list(film.common_tropes))}
                                              for film in top_overlap])

            top_jaccard = sorted(films, key=attrgetter('jaccard', 'rating'), reverse=True)[0:number_of_results]
            jaccard_dataframe = pd.DataFrame([{'Similarity (Jaccard)': "{:.2f}".format(film.jaccard * 100) + '%',
                                               'Film': film.name, 'Rating': film.rating, 'N. tropes': film.n_tropes,
                                               'Common tropes': ', '.join(list(film.common_tropes))}
                                              for film in top_jaccard])
            return overlap_dataframe, jaccard_dataframe

        all_tropes = list(self.extended_dataframe.columns)[6:]
        for record in self.extended_dataframe.itertuples():
            compared_trope_set = set([trope for index, trope in enumerate(all_tropes) if record[index+7]==1])
            overlap = self.get_overlap_similarity(original_trope_set, compared_trope_set)
            jaccard = self.get_jaccard_similarity(original_trope_set, compared_trope_set)
            film = TropesSimilarityEntity(record[3], record[4], len(compared_trope_set), overlap, jaccard,
                                          original_trope_set.intersection(compared_trope_set))
            films.append(film)
            if len(films)%100==0:
                print(len(films))
        top_overlap = sorted(films, key=attrgetter('overlap','rating'), reverse=True)[0:number_of_results]
        overlap_dataframe = pd.DataFrame([{'Similarity (Overlap)': "{:.2f}".format(film.overlap*100) + '%',
                                           'Film': film.name, 'Rating': film.rating, 'N. tropes': film.n_tropes,
                                           'Common tropes': ', '.join(list(film.common_tropes))}
                                          for film in top_overlap])

        top_jaccard = sorted(films, key=attrgetter('jaccard','rating'), reverse=True)[0:number_of_results]
        jaccard_dataframe = pd.DataFrame([{'Similarity (Jaccard)': "{:.2f}".format(film.jaccard*100) + '%',
                                           'Film': film.name, 'Rating': film.rating, 'N. tropes': film.n_tropes,
                                           'Common tropes': ', '.join(list(film.common_tropes))}
                                          for film in top_jaccard])
        return overlap_dataframe, jaccard_dataframe

    def get_overlap_similarity(self, first_set, second_set):
        if len(first_set)==0 or len(second_set)==0:
            return 0
        return len(first_set.intersection(second_set))/min(len(first_set), len(second_set))

    def get_jaccard_similarity(self, first_set, second_set):
        if len(first_set)==0 or len(second_set)==0:
            return 0
        return len(first_set.intersection(second_set))/len(first_set.union(second_set))

    def build_dictionary(self, output_file):
        film_list = []
        for row in self.extended_dataframe.iterrows():
            element = row[1].to_dict()
            tropes = list(element.keys())[6:]
            filtered_tropes = [key for key in tropes if element[key] == 1]
            film = {'name': element['NameIMDB'], 'rating':element['Rating'], 'tropes':filtered_tropes}
            film_list.append(film)
            #if len(film_list)%100==0:
            #    print(len(film_list))

        json_str = json.dumps(film_list) + "\n"
        json_bytes = json_str.encode('utf-8')

        with bz2.open(output_file, "wb") as f:
            f.write(json_bytes)
        pass

#if __name__ == '__main__':
#    checker = TropesSimilarityChecker('/Users/phd/workspace/made/made_recommender/datasets/extended_dataset.csv.bz2')
#    checker.build_dictionary('/Users/phd/workspace/made/made_recommender/datasets/extended_dataset.json.bz2')


if __name__ == '__main__':
    checker = TropesSimilarityChecker()
    checker.load_extended_dataset_json('/Users/phd/workspace/made/made_recommender/datasets/extended_dataset.json.bz2')
    tropes_list = ['ActionHeroBabysitter', 'DeathByFlashback', 'DisneyVillainDeath', 'DuelToTheDeath',
                   'EarlyBirdCameo', 'FightingFromTheInside', 'HandsOffParenting', 'Homage', 'ImNotAfraidOfYou',
                   'JumpCut', 'MouthingTheProfanity', 'NoSympathy', 'OminousFog', 'OneHeadTaller',
                   'PoorMansSubstitute', 'PragmaticAdaptation', 'RichIdiotWithNoDayJob', 'SomeoneToRememberHimBy',
                   'SpitefulSpit', 'TalkingHeads', 'TitledAfterTheSong', 'WeaponOfXSlaying', '[GENRE]Animation',
                   '[GENRE]Documentary', '[GENRE]Drama', '[GENRE]History', '[GENRE]Mystery', '[GENRE]Romance',
                   '[GENRE]War', '[GENRE]Western']
    films = checker.get_top_films_by_simmilarity(tropes_list, 10)

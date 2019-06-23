from __future__ import print_function

import bz2
import logging
import math
import os
from io import StringIO

import joblib
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedKFold
from sklearn.neural_network import MLPRegressor

from common.base_script import BaseScript
from common.log_stdout_through_logger import write_stdout_through_logger


# see https://datascience.stackexchange.com/questions/36049/how-to-adjust-the-hyperparameters-of-mlp-classifier-to-get-more-perfect-performa


class EvaluatorHyperparametersTester(BaseScript):
    EVERYTHING_BUT_TROPES = ['Id', 'NameTvTropes', 'NameIMDB', 'Rating', 'Votes', 'Year']

    def __init__(self, source_extended_dataset):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M:%m', )

        self.source_extended_dataset = source_extended_dataset

        parameters = dict(source_extended_dataset=source_extended_dataset)
        BaseScript.__init__(self, parameters)

        self.parameter_space = {}
        self.extended_dataframe = None
        self.trope_names = None
        self.layer_sizes = []
        self.clf = None

    def run(self):
        self._load_dataframe()
        self._build_parameter_space()

        self.trope_names = [key for key in self.extended_dataframe.keys() if key not in self.EVERYTHING_BUT_TROPES]
        inputs = self.extended_dataframe.loc[:][self.trope_names].values
        outputs = self.extended_dataframe.loc[:]['Rating'].values

        self._calculate_layer_sizes()
        mlp = MLPRegressor(verbose=100, early_stopping=True)

        cv = RepeatedKFold(n_splits=3, n_repeats=1)
        self.clf = GridSearchCV(mlp, self.parameter_space, n_jobs=6, cv=cv)  # n_jobs=-1
        with write_stdout_through_logger(self._logger):
            self.clf.fit(inputs, outputs)

        self._log_grid_results()

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

    def _build_parameter_space(self):
        self.parameter_space = {
            'hidden_layer_sizes': [tuple(layers[1:-1]) for layers in self.layer_sizes],
            'activation': ['tanh', 'relu'],
            'solver': ['sgd', 'adam'],
            'alpha': [0.0001],
            'max_iter': [100],
            'learning_rate': ['constant', 'adaptive'],
            'early_stopping': [False]
        }
        for key, value in self.parameter_space.items():
            self._add_to_summary(key, value)

    def _calculate_layer_sizes(self):
        self.layer_sizes = []

        tropes_count = len(self.trope_names)
        self.layer_sizes.append([tropes_count, int(math.sqrt(tropes_count)), 1])
        self.layer_sizes.append([tropes_count, int(math.sqrt(tropes_count * (tropes_count ** (1 / 3)))),
                                 int(tropes_count ** (1 / 3)), 1])

        self._add_to_summary('Layer sizes', self.layer_sizes)

    def _log_grid_results(self):
        means = self.clf.cv_results_['mean_test_score']
        stds = self.clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, self.clf.cv_results_['params']):
            params['mean'] = mean
            params['std'] = std
            self._info(f'Result: {mean} (+/-{std}) for {params}')

    def pickle(self, target_folder):
        file_name = f'evaluator_hyperparameters.sav'
        file_path = os.path.join(target_folder, file_name)

        return_data = {'inputs': self.trope_names, 'evaluator': self.clf}
        joblib.dump(return_data, file_path, compress=False)
        self._add_to_summary('Pickled evaluator path', file_path)

    def finish(self):
        self._finish_and_summary()

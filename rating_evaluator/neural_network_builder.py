import logging
from collections import OrderedDict
from random import Random

import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor

# see https://medium.com/@joshua_e_k/predicting-popular-tweets-with-python-and-neural-networks-on-a-raspberry-pi-71b63616c2f4
# see https://medium.com/dunder-data/selecting-subsets-of-data-in-pandas-6fcd0170be9c
# see https://medium.com/dunder-data/selecting-subsets-of-data-in-pandas-part-4-c4216f84d388
# see https://towardsdatascience.com/beginners-ask-how-many-hidden-layers-neurons-to-use-in-artificial-neural-networks-51466afa0d3e
# see https://scikit-learn.org/stable/modules/neural_networks_supervised.html
# see https://towardsdatascience.com/feature-selection-with-pandas-e3690ad8504b
# see https://scikit-learn.org/stable/modules/feature_selection.html
# see https://www.slideshare.net/recsysfr/using-neural-networks-to-predict-user-ratings
# see https://stackoverflow.com/questions/34251980/a-progress-bar-for-scikit-learn

class NeuralNetworkTropes(object):
    META_COLUMN_NAME = ['Id', 'NameTvTropes', 'NameIMDB', 'Votes', 'Year']
    RATING_COLUMN_NAME = 'Rating'
    INDEX_FIRST_TROPE = len(META_COLUMN_NAME) + 1

    _logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%m', )

    def __init__(self, filename, seed=0):
        self.filename = filename
        self.all_data = None
        self.training_data = None
        self.testing_data = None
        self.random = Random()
        self.random.seed(seed)

    def run(self):
        self._track_step(u'Running...')
        self._read_csv_in_an_optimized_way()
        self._get_training_and_testing_datasets()
        self._train_neural_network()

    def _read_csv_in_an_optimized_way(self):
        self._track_step(u'Reading first line and setting column types')
        with open(self.filename) as file:
            first_line = file.readline()

        columns = first_line.split(',')
        column_types = OrderedDict(Id=np.str, NameTvTropes=np.str, NameIMDB=np.str, Votes=np.str,
                                   Year=np.str, Rating=np.float128)

        for column in columns[self.INDEX_FIRST_TROPE]:
            column_types[column] = np.bool

        self._track_step(u'Reading CSV in an optimized way')
        self.all_data = pd.read_csv(self.filename, dtype=column_types)
        self.tropes_column_names = list(self.all_data.columns[self.INDEX_FIRST_TROPE:])
        self._track_step('Data shape {}'.format(self.all_data.shape))

        self._track_step('Cleaning up rows with NaN rating')
        self.all_data = self.all_data[np.isfinite(self.all_data[self.RATING_COLUMN_NAME])]
        self._track_step('New data shape {}'.format(self.all_data.shape))

        self.number_of_rows = self.all_data.shape[0]

    def _track_step(self, message):
        try:
            self.counter += 1
        except AttributeError:
            self.counter = 1

        self._logger.info(u'Step {}.- {}'.format(self.counter, message))

    def _get_training_and_testing_datasets(self):
        self._track_step(u'Splitting data into training and testing datasets')
        indexes = list(range(0, self.number_of_rows))
        self.random.shuffle(indexes)
        split_index = int(len(indexes) * 0.8)
        indexes_training = indexes[0:split_index]
        indexes_testing = indexes[split_index:]

        self.training_data = self.all_data.iloc[indexes_training]
        self.testing_data = self.all_data.iloc[indexes_testing]
        self._track_step('Extracted training data ({}) and testing Data ({})'.format(
            self.training_data.shape, self.testing_data.shape))

    def _train_neural_network(self):
        self._track_step(u'Extracting inputs and outputs')

        number_of_variables = len(self.tropes_column_names)

        inputs = self.training_data.loc[:][self.tropes_column_names].values
        outputs = self.training_data.loc[:][self.RATING_COLUMN_NAME].values

        self._track_step(u'Training Neural Network')
        #nnet = MLPRegressor(activation='relu', alpha=0.0001,
        #                    hidden_layer_sizes=(int(number_of_variables * 0.5), int(number_of_variables * 0.25)),
        #                    solver='adam', max_iter=400, verbose=True)

        #inputs = self.training_data.loc[:][self.tropes_column_names].values
        #outputs = self.training_data.loc[:][self.RATING_COLUMN_NAME].values

        nnet = MLPRegressor(activation='relu', alpha=0.0001,
                            hidden_layer_sizes=(3120, 100),
                            solver='adam', max_iter=400, verbose=True)
        nnet.fit(inputs, outputs)

        # Iteration 1, loss = 2.92579125
        # Iteration 2, loss = 0.70745726
        # Iteration 3, loss = 0.33878600
        # Iteration 4, loss = 0.19716564
        # Iteration 5, loss = 0.12395414
        # Iteration 6, loss = 0.07992301
        # Iteration 7, loss = 0.05652974
        # Iteration 8, loss = 0.04699543
        # Iteration 9, loss = 0.04135735
        # Iteration 10, loss = 0.05113443
        # Iteration 11, loss = 0.06082659
        # Iteration 12, loss = 0.05839890
        # Iteration 13, loss = 0.04938492
        # Iteration 14, loss = 0.03715774
        # Iteration 15, loss = 0.03601589
        # Iteration 16, loss = 0.03061723
        # Iteration 17, loss = 0.02470007
        # Iteration 18, loss = 0.03402184
        # Iteration 19, loss = 0.03407629
        # Iteration 20, loss = 0.01972088
        # Iteration 21, loss = 0.01662889
        # Iteration 22, loss = 0.02383086
        # Iteration 23, loss = 0.02369421
        # Iteration 24, loss = 0.01466736
        # Iteration 25, loss = 0.01146385
        # Iteration 26, loss = 0.00941772
        # Iteration 27, loss = 0.01421350
        # Iteration 28, loss = 0.00833665
        # Iteration 29, loss = 0.00799861
        # Iteration 30, loss = 0.02221183
        # Iteration 31, loss = 0.02350082
        # Iteration 32, loss = 0.09171731
        # Iteration 33, loss = 0.05842234
        # Iteration 34, loss = 0.04244361
        # Iteration 35, loss = 0.02962524
        # Iteration 36, loss = 0.02659141
        # Iteration 37, loss = 0.02649174
        # Iteration 38, loss = 0.01785229
        # Iteration 39, loss = 0.00999016
        # Iteration 40, loss = 0.01927843

        joblib.dump(nnet, 'MLPRegressor_relu_3120_100_adam.sav')

        self.training_data.to_csv('training_data.csv')
        self.testing_data.to_csv('testing_data.csv')

        # loaded_model = joblib.load(filename)

        pass

        testing_inputs = self.testing_data.loc[:][self.tropes_column_names].values
        testing_outputs = self.testing_data.loc[:][self.RATING_COLUMN_NAME].values
        nnet.score(testing_inputs, testing_outputs)



        # 0.34097441815522556

if __name__ == "__main__":
    file_name = u'/Users/phd/workspace/made/made_tropes/scripts/data/film_extended_information_unique_values.csv'
    pca_tropes = NeuralNetworkTropes(file_name)
    pca_tropes.run()

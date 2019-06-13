import math
import os

import pandas as pd
from sklearn.externals import joblib
from sklearn.neural_network import MLPRegressor

from common.base_script import BaseScript

# Number of hidden nodes: There is no magic formula for selecting the optimum number of hidden neurons.
# However, some thumb rules are available for calculating the number of hidden neurons.
# A rough approximation can be obtained by the geometric pyramid rule proposed by Masters (1993).
# For a three layer network with n input and m output neurons, the hidden layer would have 𝑛∗𝑚‾‾‾‾‾√ neurons.
# Ref:
# 1 Masters, Timothy. Practical neural network recipes in C++. Morgan Kaufmann, 1993.
# [2] http://www.iitbhu.ac.in/faculty/min/rajesh-rai/NMEICT-Slope/lecture/c14/l1.html


class EvaluatorBuilder(BaseScript):
    EVERYTHING_BUT_TROPES = ['Id', 'NameTvTropes', 'NameIMDB', 'Rating', 'Votes', 'Year']

    def __init__(self, source_extended_dataset):
        # log initial
        self.source_extended_dataset = source_extended_dataset
        parameters = dict(source_extended_dataset=source_extended_dataset)
        BaseScript.__init__(self, parameters)

    def run(self):
        extended_dataframe = None

        hdf_name = self.source_extended_dataset.replace('.csv.bz2', '.h5')
        if os.path.isfile(hdf_name):
            self.extended_dataframe = pd.read_hdf(hdf_name)
        else:
            pass
            # open the file
            # uncompress it
            # load_csv in pandas

        self.trope_names = [key for key in self.extended_dataframe.keys() if key not in self.EVERYTHING_BUT_TROPES]

        inputs = self.extended_dataframe.loc[:][self.trope_names].values
        outputs = self.extended_dataframe.loc[:]['Rating'].values

        tropes_count = len(self.trope_names)
        self.layer_sizes = [tropes_count, int(math.sqrt(tropes_count * (tropes_count ** (1 / 3)))),
                            int(tropes_count ** (1 / 3)), 1]
        self._add_to_summary('Layer sizes', self.layer_sizes)

        self.neural_network = MLPRegressor(activation='relu', alpha=0.0001,
                                           hidden_layer_sizes=(self.layer_sizes[1], self.layer_sizes[2]),
                                           solver='adam', max_iter=400, verbose=True)
        self.neural_network.fit(inputs, outputs)

    def pickle(self, target_folder):
        file_name = f'evaluator_{"_".join([str(value) for value in self.layer_sizes])}.sav'
        file_path = os.path.join(target_folder, file_name)

        return_data = {'inputs':self.trope_names, 'evaluator':self.neural_network}
        joblib.dump(return_data, file_path, compress=False)
        self._add_to_summary('Pickled evaluator path', file_path)

    def finish(self):
        self._finish_and_summary()
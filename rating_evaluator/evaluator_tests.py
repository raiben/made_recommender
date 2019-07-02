import bz2
import json
import statistics
import pandas as pd
import matplotlib.pyplot as plt

from rating_evaluator.neural_network_tropes_evaluator import NeuralNetworkTropesEvaluator


class EvaluatorTests(object):

    def __init__(self, evaluator_file=None, extended_dataset_file=None):
        self.evaluator_file = evaluator_file
        self.extended_dataset_file = extended_dataset_file
        self.test_results = {}

    def init_from_file(self, serialized_data_file):
        with bz2.open(serialized_data_file, "rb") as f:
            content = f.read()
        json_bytes = content.decode('utf-8')
        self.test_results = json.loads(json_bytes)

    def run_tests(self):
        evaluator = NeuralNetworkTropesEvaluator(self.evaluator_file)

        with bz2.open(self.extended_dataset_file, "rb") as f:
            content = f.read()
        json_bytes = content.decode('utf-8')
        films = json.loads(json_bytes)

        for film in films:
            film['evaluation'] = evaluator.evaluate_just_rating(film['tropes'])[0]
        all_errors = [abs(film['rating'] - film['evaluation']) for film in films]

        self.test_results['error_general_stats'] = {}
        self.test_results['error_general_stats']['avg'] = statistics.mean(all_errors)
        self.test_results['error_general_stats']['std'] = statistics.pstdev(all_errors)

        self.test_results['errors_by_tropes'] = []
        errors_by_tropes = {}
        for film in films:
            key = len(film['tropes'])
            if key not in errors_by_tropes:
                errors_by_tropes[key] = []
            error = film['rating'] - film['evaluation']
            abserror = abs(error)
            errors_by_tropes[key].append(abserror)
            self.test_results['errors_by_tropes'].append({'Number of Tropes':key, 'Error':error, 'AbsError':abserror})

        self.test_results['errors_by_tropes_stats'] = []
        for key, values in errors_by_tropes.items():
            item = {'Number of Tropes': key, 'Average': statistics.mean(values),
                    'Standard Deviation': statistics.pstdev(values)}
            self.test_results['errors_by_tropes_stats'].append(item)

        genres = [trope for trope in evaluator.tropes if '[GENRE]' in trope]
        genres_evaluation = [{'Genre': genre, 'Estimated rating': evaluator.evaluate_just_rating(genre)[0]}
                             for genre in genres]
        self.test_results['evaluations_1_genre'] = genres_evaluation

    def store_json(self, output_file):
        json_str = json.dumps(self.test_results) + "\n"
        json_bytes = json_str.encode('utf-8')

        with bz2.open(output_file, "wb") as f:
            f.write(json_bytes)

if __name__ == "__main__":
    test = EvaluatorTests(
        evaluator_file=u'../datasets/evaluator_[26273, 162, 1].sav',
        extended_dataset_file='../datasets/extended_dataset.json.bz2')
    test.run_tests()
    test.store_json('../datasets/evaluator_tests.json.bz2')

    info_file = '../datasets/evaluator_tests.json.bz2'
    test = EvaluatorTests()
    test.init_from_file(info_file)

    errors_by_tropes = pd.DataFrame(test.test_results['errors_by_tropes'])
    errors_by_tropes.plot.hexbin(x='Number of Tropes', y='Error', gridsize=25, cmap="Blues", bins="log")
    plt.show()

    errors_by_tropes = pd.DataFrame(test.test_results['errors_by_tropes'])
    errors_by_tropes.plot.hexbin(x='Number of Tropes', y='AbsError', gridsize=25, cmap="Blues", bins="log")
    plt.show()

    pass

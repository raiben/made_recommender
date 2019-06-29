import itertools
import os
from multiprocessing import Pool

from invoke import task, run

from mapper.film_mapper import FilmMapper
from rating_evaluator.evaluator_builder import EvaluatorBuilder
from rating_evaluator.evaluator_hyperparameters_tester import EvaluatorHyperparametersTester
from trope_recommender.trope_recommender import TropeRecommender
from tvtropes_scraper.tvtropes_scraper import TVTropesScraper


@task
def scrape_tvtropes(context, cache_directory=None, session=None):
    """
    Scrape tropes by film in TvTropes.org

    :param cache_directory: The folder that all the downloaded pages are going to be written into.
    :param session: (Optional) Name of the cache folder. If not provided, then it will use the current date/time.
    """
    if cache_directory is None:
        print('Please, add the missing parameters!!')

    TVTropesScraper.set_logger_file_id('scrape_tvtropes', session)
    scraper = TVTropesScraper(directory=cache_directory, session=session)
    scraper.run()


@task
def map_films(context, tvtropes_films_file, imdb_titles_file, imdb_ratings_file,
              target_dataset='datasets/extended_dataset.csv', remove_ambiguities=False):
    """
    Map scraped films from TvTropes.org to IMDB.com

    :type tvtropes_films_file: path to the scraped file 'film_tropes_<datetime>.json.bz2'.
    :type imdb_titles_file: path to the file 'title.basics.tsv'
    :type imdb_ratings_file: path to the file 'title.ratings.tsv'
    :type target_dataset: path to the target file (csv)
    :type remove_ambiguities: Remove ambiguity by selecting the most popular film when different films from IMDb match
    the film in TVTropes
    """

    _check_file_exists('tvtropes_films_file', tvtropes_films_file)
    _check_file_exists('imdb_titles_file', imdb_titles_file)
    _check_file_exists('imdb_ratings_file', imdb_ratings_file)

    FilmMapper.set_logger_file_id('map_films')
    mapper = FilmMapper(tvtropes_films_file=tvtropes_films_file, imdb_titles_file=imdb_titles_file,
                        imdb_ratings_file=imdb_ratings_file, target_dataset=target_dataset,
                        remove_ambiguities=remove_ambiguities)
    mapper.run()


def _check_file_exists(parameter, file_name):
    if not os.path.isfile(file_name):
        print(f'Please, provide a valid path for {parameter}')
        exit(1)


@task
def build_evaluator(context, extended_dataset, target_folder='datasets/', random_seed=0):
    """
    Builds an evaluator using a Neural Network trained with the extended dataset.
    The inputs of the evaluator are the tropes of the film and the output is the rating.

    :type extended_dataset: path of the csv/h5 file that contains the extended information from the films
    :type target_file: file that will keep the pickled evaluator, so it can be loaded and used later on
    :type random_seed: a number to use as random seed (executions with the same seed give the same results)

    """
    FilmMapper.set_logger_file_id('build_evaluator')

    evaluator = EvaluatorBuilder(extended_dataset, random_seed=int(random_seed))
    evaluator.run()
    evaluator.pickle(target_folder)
    evaluator.finish()


@task
def test_evaluator_hyperparameters(context, extended_dataset, target_folder='datasets/'):
    """
    Builds an evaluator using a Neural Network trained with the extended dataset.
    The inputs of the evaluator are the tropes of the film and the output is the rating.

    :type extended_dataset: path of the csv/h5 file that contains the extended information from the films
    :type target_file: file that will keep the pickled evaluator, so it can be loaded and used later on
    :type random_seed: a number to use as random seed (executions with the same seed give the same results)

    """
    FilmMapper.set_logger_file_id('build_evaluator_hyperparameters')

    tester = EvaluatorHyperparametersTester(extended_dataset)
    tester.run()
    # tester.pickle(target_folder)
    tester.finish()

@task
def show_genres(search_query, page=0, results=10):
    print('TODO!')


@task
def show_tropes(search_query, page=1, results=10):
    print('TODO!')


@task
def show_films(search_query, page=2, results=10):
    print('TODO!')


@task
def test_recommender(context, neural_network_file):
    TropeRecommender.set_logger_file_id('trope_recommender')

    executions = range(20,30) #range(15,20) #range(12, 15)  # range(11,12) #range(10,11) #range(0, 10)
    solution_length_alternatives = [30]
    max_evaluations_alternatives = [30000]
    mutation_probability_alternatives = [2 / 30, 1 / 30, 0.5 / 30]
    crossover_probability_alternatives = [0.25, 0.5, 0.75]
    population_size_alternatives = [50, 100, 200]
    no_better_results_during_evaluations_alternatives = [10000]

    general_summary = u'logs/recommender_summary.log'
    details_file_name = u'logs/recommender_details.log'

    list_of_parameters = [executions, solution_length_alternatives, max_evaluations_alternatives,
                          mutation_probability_alternatives, crossover_probability_alternatives,
                          population_size_alternatives, no_better_results_during_evaluations_alternatives]
    combinations = list(itertools.product(*list_of_parameters))

    seed = 0
    combinations = [list(combination) for combination in combinations]
    for combination in combinations:
        combination.extend([seed, neural_network_file, general_summary, details_file_name])
        seed += 1

    pool = Pool(processes=7)  # start 4 worker processes
    for combination in combinations:
        pool.apply_async(run_recommender, combination)  # evaluate "f(10)" asynchronously
    pool.close()
    pool.join()


def run_recommender(execution, solution_length, max_evaluations, mutation_probability, crossover_probability,
                    population_size, no_better_results_during_evaluations, seed, neural_network_file, general_summary,
                    details_file_name):
    name_components = [execution, solution_length, max_evaluations, mutation_probability, crossover_probability,
                       population_size, no_better_results_during_evaluations, seed]
    execution_name = ','.join([str(component) for component in name_components])

    recommender = TropeRecommender(neural_network_file, general_summary)
    recommender.optimize(
        seed=seed, list_of_constrained_tropes=[], solution_length=solution_length,
        max_evaluations=max_evaluations, mutation_probability=mutation_probability,
        crossover_probability=crossover_probability, population_size=population_size,
        details_file_name=details_file_name, execution_name=execution_name,
        no_better_results_during_evaluations=no_better_results_during_evaluations)
    recommender.finish()


@task
def clean_paper(context, documentation_mode=False):
    print("Cleaning ...")
    patterns = ['papers/_*', 'papers/*.aux', 'papers/*.log', 'papers/*.out',
                'papers/*.tex', 'papers/*.pdf', 'papers/*.pyc', 'papers/*.bbl', 'papers/*.blg']
    if not documentation_mode:
        patterns.append('papers/figures')

    for pattern in patterns:
        context.run(f'rm -rf {pattern}')


@task
def build_paper_latex(context):
    print("Building latex file and figures through pweave ...")
    command = 'cd papers && pweave -f texminted report.texw'
    run(command, hide=False, warn=True)


@task
def build_paper_pdf(context):
    print("Building pdf through pdflatex ...")
    command = 'cd papers ' \
              '&& pdflatex -shell-escape report.tex ' \
              '&& bibtex report.aux ' \
              '&& pdflatex -shell-escape report.tex ' \
              '&& pdflatex -shell-escape report.tex'
    run(command, hide=False, warn=True)


@task
def open_paper(context):
    command = 'cd paper && open paper.pdf'
    run(command, hide=True, warn=True)


@task
def build_paper(context):
    """
    Cleans and build the paper using pweave, pdflatex and bibtex.
    Output file: report.pdf
    """
    clean_paper(context)
    build_paper_latex(context)
    build_paper_pdf(context)


@task
def build_paper_latex_expert_systems_2019(context, documentation_mode=False):
    print("Building latex file and figures through pweave ...")
    command = 'cd papers && pweave -f texminted paper_expert_systems_2019.texw'

    if documentation_mode:
        command = command + ' -d'

    run(command, hide=False, warn=True)


@task
def build_paper_pdf_expert_systems_2019(context):
    print("Building pdf through pdflatex ...")
    command = 'cd papers ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex ' \
              '&& bibtex paper_expert_systems_2019.aux ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex' \
              '&& cp papers/paper_expert_systems_2019.pdf '
    run(command, hide=False, warn=True)


@task
def build_paper_expert_systems_2019(context, documentation_mode=False):
    """
    Cleans and build the paper using pweave, pdflatex and bibtex.
    Output file: report.pdf
    """
    clean_paper(context, documentation_mode)
    build_paper_latex_expert_systems_2019(context, documentation_mode)
    build_paper_pdf_expert_systems_2019(context)


if __name__ == "__main__":
    import sys
    from invoke import Program
    from invoke.collection import Collection

    collection = Collection()
    program = Program()
    program.run(sys.argv)

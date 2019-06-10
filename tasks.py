import os

from invoke import task, run

from mapper.film_mapper import FilmMapper
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
def show_genres(search_query, page=0, results=10):
    print('TODO!')


@task
def show_tropes(search_query, page=1, results=10):
    print('TODO!')


@task
def show_films(search_query, page=2, results=10):
    print('TODO!')


@task
def recommend(genres_to_include='', tropes_to_include='', length=40):
    print('TODO!')


@task
def clean_paper(context):
    print("Cleaning ...")
    patterns = ['papers/_*', 'papers/figures', 'papers/*.aux', 'papers/*.log', 'papers/*.out',
                'papers/*.tex', 'papers/*.pdf', 'papers/*.pyc', 'papers/*.bbl', 'papers/*.blg']
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
def build_paper_latex_expert_systems_2019(context):
    print("Building latex file and figures through pweave ...")
    command = 'cd papers && pweave -f texminted paper_expert_systems_2019.texw'
    run(command, hide=False, warn=True)


@task
def build_paper_pdf_expert_systems_2019(context):
    print("Building pdf through pdflatex ...")
    command = 'cd papers ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex ' \
              '&& bibtex paper_expert_systems_2019.aux ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex ' \
              '&& pdflatex -shell-escape paper_expert_systems_2019.tex'
    run(command, hide=False, warn=True)


@task
def build_paper_expert_systems_2019(context):
    """
    Cleans and build the paper using pweave, pdflatex and bibtex.
    Output file: report.pdf
    """
    clean_paper(context)
    build_paper_latex_expert_systems_2019(context)
    build_paper_pdf_expert_systems_2019(context)

if __name__ == "__main__":
    import sys
    from invoke import Program
    from invoke.collection import Collection

    collection = Collection()
    program = Program()
    program.run(sys.argv)

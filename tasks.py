from invoke import task

from common.base_script import BaseScript
from tvtropes_scrapper.tvtropes_scrapper import TVTropesScrapper


@task
def scrap_tvtropes(context, cache_directory=None, session=None):
    """
    Scrap tropes by film in TvTropes.org

    :param cache_directory: The folder that all the downloaded pages are going to be written into.
    :param session: (Optional) Name of the cache folder. If not provided, then it will use the current date/time.
    """
    if cache_directory is None:
        print('Please, add the missing parameters!!')

    BaseScript.set_logger_file_id('scrap_tvtropes', session)
    scrapper = TVTropesScrapper(directory=cache_directory, session=session)
    scrapper.run()


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


if __name__ == "__main__":
    import sys
    from invoke import Program
    from invoke.collection import Collection

    collection = Collection()
    program = Program()
    program.run(sys.argv)

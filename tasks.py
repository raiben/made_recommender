from invoke import task

@task
def show_genres(search_query, page=0, results= 10):
    print('TODO!')

@task
def show_tropes(search_query, page=1, results=10):
    print('TODO!')

@task
def show_films(search_query, page=2, results=10):
    print('TODO!')

@task
def recommend(genres_to_include='',tropes_to_include='', length=40):
    print('TODO!')


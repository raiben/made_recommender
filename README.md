# About the project

**made_recommender** is a **deep-learning** **bio-inspired** 
**film-oriented** trope recommender that relies on TVTropes 
and IMDB.

# Requirements

The project uses **python3** compliant code and the libraries
listed in the [requirements.txt](requirements.txt) file.

Are you using python3? You can run this command and check it:
```console
python3 --version
```
If you get and answer that looks like ```Python 3.X.X``` then
you are done.

If you don't, please follow the tutorial form realpython:
[Python 3 Installation and Setup Guide](https://realpython.com/installing-python/).

To install the requirements, please use:
```console
pip intall -r requirements.txt
``` 

If you make changes and need to rebuild the requirements.txt, 
do it  through ```pireqs```.

```console
pip3 install pipreqs
pipreqs . --force
```

You are ready to reproduce science. The different scripts and
classes can be run from the command line through ```ìnvoke```.

To get a list of commands and 
```console
invoke --list
```

# Content

## TVTropes scrapper

**Module**: [tvtropes_scrapper](tvtropes_scrapper)

Script to download all the films information from TVTropes and 
extract the tropes inside them:

```console
invoke scrap-tvtropes --help
```
```console
Usage: inv[oke] [--core-opts] scrap-tvtropes [--options] [other tasks here ...]

Docstring:
  Scrap tropes by film in TvTropes.org

  :param cache_directory: The folder that all the downloaded pages are going to be written into.
  :param session: (Optional) Name of the cache folder. If not provided, then it will use the current date/time.

Options:
  -c STRING, --cache-directory=STRING
  -s STRING, --session=STRING
```

Example:
```console
invoke scrap-tvtropes --cache-directory "datasets/scrapper_cache"
```

```console
Building directory: datasets/scrapper_cache/20190412_104715
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Film
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/BewareTheSillyOnes
Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Film
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/SpinOff
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/TheMovie
Retrieving URL from tvtropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/CameraTricks
...
```

The output file ```all_films_and_their_tropes_{self.session}.json```
will be available in the ```cache-directory``` provided

## imdb_matcher

Scripts to merge information from the
scrapped data (from TVTropes) and IMDB databases, by name 
of the film and year.

## dataset_displayers

Scripts to:

1. convert the generated file into a database that you
can query
2. search for films and get their information.
3. search for tropes and get their information.

## rating_evaluator

Scripts to build artifacts from the datasets that are able to 
evalate a set of tropes and return a predicted rating.

## trope_recommender

Scripts to generate a set of tropes constrained by the user
that maximize the predicted rating.


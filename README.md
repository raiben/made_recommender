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

### Features

- The scrapper **extracts all the categories** from the main categories page: 
https://tvtropes.org/pmwiki/pmwiki.php/Main/Film . 
Then, for each category page, it extracts **all the film identifiers** assigned to it. 
Finally, for every film page, it extracts **all the trope identifiers**. 
As result, it builds a **dictionary of films and tropes**.
- The process **can be stopped and re-launched at any moment** because the pages.
are permanently stored in the local cache, so it will continue from the last page processed.
- The files in cache and the final output file are **compressed using bzip2** with a block size of 900k 
(the highest compression available).
- The file names are **encoded in base64** to avoid special characters.
The character '-' is replaced by '_'.
- The code avoids slowing down TVTropes servers by **waiting between each download**.


### Usage

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

### Output

The task generates a file called ```film_tropes_<session>.json.bz2```
will be available in the ```<cache-directory>``` provided.

**Format**:
<TODO>

### Example

Example:
```console
invoke scrap-tvtropes --cache-directory "datasets/scrapper_cache"
```

```console
04-12 17:04:04 common.base_script INFO     Step 1.- Building directory: datasets/scrapper_cache/20190412_170435
04-12 17:04:04 common.base_script INFO     Retrieving URL from TVTropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Film
04-12 17:04:04 common.base_script INFO     Retrieving URL from TVTropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
04-12 17:04:04 common.base_script INFO     Retrieving URL from TVTropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
04-12 17:04:04 common.base_script INFO     Retrieving URL from TVTropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/BewareTheSillyOnes
04-12 17:04:04 common.base_script INFO     Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
04-12 17:04:04 common.base_script INFO     Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
04-12 17:04:04 common.base_script INFO     Retrieving URL from cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Film
04-12 17:04:04 common.base_script INFO     Retrieving URL from TVTropes: https://tvtropes.org/pmwiki/pmwiki.php/Main/SpinOff
...
```

### Troubleshooting

- **To re-cache**, please remove the cache folder. The class will auto generate it again in the next execution, 
re-downloading the pages.


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


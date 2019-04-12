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

You are ready to reproduce my science...

# Content

## tvtropes_scrapper

Scripts to download all the films
information from TVTropes and extract the tropes inside them.  

## imdb_matcher

Scripts to merge information from the
scrapped data (from TVTropes) and IMDB databases, by name 
of the film and year.

## rating_evaluator

Scripts to build artifacts from the datasets that are able to 
evalate a set of tropes and return a predicted rating.

## trope_recommender

Scripts to generate a set of tropes constrained by the user
that maximize the predicted rating.


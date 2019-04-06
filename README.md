# About the project

made_recommender is a **deep-learning** **bio-inspired** 
**film-oriented** trope recommender that relies on TVTropes 
and IMDB.

# Requirements

The project uses **python3** compliant code and the libraries
listed in the [requirements.txt](requirements.txt) file.

To install the requirements, please use:
```console
pip intall -r requirements.txt
``` 

If you need to rebuild the requirements.txt, 
do it  through ```pireqs```.

```console
pip3 install pipreqs
pipreqs . --force
```

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


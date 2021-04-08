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
pip install -r requirements.txt
``` 

or

```shell
pip install inspyred cachetools invoke pweave
```

If you make changes and need to rebuild the requirements.txt, 
do it  through ```pipreqs```.

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

# Logging

All the executions are logged in the console and in different files under ```./logs/<identifier>_<timestamp>.log```.
That will make it easier to trace the different experiments and executions.  

# Content

## TVTropes scraper

**Module**: [tvtropes_scraper](tvtropes_scraper)

Script to download all the films information from TVTropes and 
extract the tropes inside them:

### Features

- The scraper **extracts all the categories** from the main categories page: 
https://tvtropes.org/pmwiki/pmwiki.php/Main/Film . 
Then, for each category page, it extracts **all the film identifiers** assigned to it. 
Finally, for every film page, it extracts **all the trope identifiers**. 
As result, it builds a **dictionary of films and tropes**.
- The process **can be stopped and re-launched at any moment** because the pages.
are permanently stored in the local cache, so it will continue from the last page processed.
- The files in cache and the final output file are **compressed using bzip2** with a block size of 900k 
(the highest compression available).
- The file names are **encoded in base64** to avoid using special characters.
The character '-' is replaced by '_'.
- The code avoids slowing down TVTropes servers by **waiting between each download**.
- The execution when no page is cached takes around 3~4 hours. When pages are cached it takes ~2 minutes.
It can retrieve around 12K pages. 

### Usage

```console
invoke scrape-tvtropes --help
```
```console
Usage: inv[oke] [--core-opts] scrape-tvtropes [--options] [other tasks here ...]

Docstring:
  Scrape tropes by film in TvTropes.org

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
```json
{
  "<film_identifier>": [
    "<trope_identifier>", 
    "..."
  ],
  "...": [
    "..." 
  ]
}
```

### Example

Example:
```console
invoke scrape-tvtropes --cache-directory ./datasets/scraper/cache/ --session 20190501
```

```console
05-01 22:56:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
05-01 22:56:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
05-01 22:56:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/FatGirl
05-01 22:56:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Tropes
05-01 22:56:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Main/Media
...
05-01 23:02:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Film/Absurd
05-01 23:02:05 common.base_script INFO     Film Absurd (41 tropes): ['AnAxeToGrind', 'AsLongAsItSoundsForeign', 'BigBad', 'ImplacableMan', 'BigDamnHeroes', 'CarFu', 'ChekhovsGun', 'DecapitationPresentation', 'DolledUpInstallment', 'Eagleland', 'EyeScream', 'FacialHorror', 'Gorn', 'GrossUpCloseUp', 'HealingFactor', 'HorrorDoesntSettleForSimpleTuesday', 'ImpaledWithExtremePrejudice', 'ImpromptuTracheotomy', 'ImprovisedWeapon', 'MyCarHatesMe', 'NeverFoundTheBody', 'NoNameGiven', 'NoodleIncident', 'HealingFactor', 'OffWithHisHead', 'OneWordTitle', 'PeekABooCorpse', 'PowerfulPick', 'RagTagBunchOfMisfits', 'RedShirt', 'RemovingTheHeadOrDestroyingTheBrain', 'ShirtlessScene', 'SlasherSmile', 'SpiritualSuccessor', 'TheStoic', 'ThingsThatGoBumpInTheNight', 'ThrowingOffTheDisability', 'ThisIsADrill', 'TitleDrop', 'WithGreatPowerComesGreatInsanity', 'ZombieGait']
05-01 23:02:05 common.base_script INFO     Status: 222/11846 films
05-01 23:02:05 common.base_script INFO     Retrieving URL from TVTropes and storing in cache: https://tvtropes.org/pmwiki/pmwiki.php/Film/Accepted
05-01 23:02:05 common.base_script INFO     Film Accepted (82 tropes): ['AbandonedHospital', 'AloneInACrowd', 'ArtisticLicenseUniversityAdmissions', 'ReadingsAreOffTheScale', 'ArtisticLicenseEngineering', 'AttentionDeficitOohShiny', 'AnnoyingYoungerSibling', 'BecomingTheMask', 'BigStore', 'BookDumb', 'BrickJoke', 'PsychicPowers', 'BrilliantButLazy', 'ButtMonkey', 'CalvinBall', 'TheCon', 'BigStore', 'ClusterFBomb', 'CoolLoser', 'CoolUncle', 'CripplingOverspecialization', 'DeadpanSnarker', 'DeanBitterman', 'DumbassHasAPoint', 'StrawmanHasAPoint', 'TroublingUnchildlikeBehaviour', 'EpicFail', 'FakeRealTurn', 'ForTheEvulz', 'FunWithAcronyms', 'LampshadeHanging', 'BringMyBrownPants', 'GeniusDitz', 'HighSchoolHustler', 'ImpossiblyDeliciousFood', 'MessOnAPlate', 'IndyPloy', 'OhCrap', 'OhCrap', 'InitiationCeremony', 'IvyLeagueForEveryone', 'KavorkaMan', 'KickTheDog', 'LargeHam', 'MadeOfExplodium', 'MessOnAPlate', 'MostWritersAreWriters', 'StrawmanPolitical', 'JustifiedTrope', 'NeverRecycleABuilding', 'NoodleIncident', 'OnlySaneMan', 'OddFriendship', 'CloudCuckoolander', 'PeekABooCorpse', 'HilarityEnsues', 'PrecisionFStrike', 'AluminumChristmasTrees', 'BleepDammit', 'PrisonRape', 'ProfessionalSlacker', 'ProperlyParanoid', 'PsychicPowers', 'ReadingsAreOffTheScale', 'ScreamsLikeALittleGirl', 'SettingUpdate', 'ShoutOut', 'ActorAllusion', 'SlobsVersusSnobs', 'SmugSnake', 'SoundEffectBleep', 'StartMyOwn', 'StealthPun', 'SupremeChef', 'MessOnAPlate', 'TelepathicSprinklers', 'TheDogBitesBack', 'ThisIsWhatTheBuildingWillLookLike', 'TruthInTelevision', 'ParanoiaFuel', 'VerbedTitle', 'WillingSuspensionOfDisbelief']
05-01 23:02:05 common.base_script INFO     Status: 223/11846 films
...
```

Output file content:
```json
{
  "ABCsOfDeath2": [
    "AbusiveParents",
    "AirVentPassageway",
    ...
  ],
  "ABeautifulDayInTheNeighborhood": [
    "IncorruptiblePurePureness",
    "LooselyBasedOnATrueStory"
  ],
  "ABeautifulMind": [
    "AdultFear",
    "AllThereIsToKnowAboutTheCryingGame",
    ...
  ],
  ...
}
```

A valid compressed sample file [films_tropes_20190501.json.bz2](https://github.com/raiben/made_recommender/blob/master/datasets/scraper/cache/20190501/films_tropes_20190501.json.bz2) 
can be found in the datasets folder of the project.

### Troubleshooting

- **To re-cache**, please remove the cache folder or use another session. 
The class will auto generate it again in the next execution, 
re-downloading the pages.


## imdb_matcher

Scripts to merge information from the
scrapped data (from TVTropes) and IMDB databases, by name 
of the film and year.

### Before starting 📎

IMDb Datasets are a compendium of information that IMDb offers fpr personal and 
non-commercial use. Both conditions of use and dataset descriptions are explained in
https://www.imdb.com/interfaces/. 

MADE Recommender makes use of these datasets to extend the film information from TVTropes.

Please, **download the files** `title.basics.tsv.gz` and `title.ratings.tsv.gz`
from https://datasets.imdbws.com/, **unzip** them and store ths tsv files into the 
`datasets` folder.

- title.basics.tsv: contains metadata from the films such as the title, the year, the genres
and the duration.
- title.ratings.tsv: contains the rating and the number of votes.

### Features
- 


## dataset_displayers

Scripts to:

1. convert the generated file into a database that you
can query
2. search for films and get their information.
3. search for tropes and get their information.

## rating_evaluator

Scripts to build artifacts from the datasets that are able to 
evaluate a set of tropes and return a predicted rating.

## trope_recommender

Scripts to generate a set of tropes constrained by the user
that maximize the predicted rating.

# Report generation

The directory ```/papers``` contains latex reports in Pweave language.
Pweave is a scientific report generator and a literate programming tool for Python. 
For more information, please visit the website of the 
[project](http://mpastell.com/pweave/).

### Usage

```console
invoke build-paper --help
```

```console
Usage: inv[oke] [--core-opts] build-paper [other tasks here ...]

Docstring:
  Cleans and build the paper using pweave, pdflatex and bibtex.
  Output file: report.pdf

Options:
  none
```

### Building new paper

You have to do these in turn:

    invoke build-paper-latex-expert-systems-2019
    invoke build-paper-pdf-expert-systems-2019
    
If you have an old version of graphviz, this will issue some warnings
which will be embedded in the final PDF. Just put

    PYTHONWARNINGS="ignore" 
    
in front of the first command.

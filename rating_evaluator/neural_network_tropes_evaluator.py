import logging

from sklearn.externals import joblib

from common.base_script import BaseScript
from common.string_utils import humanize_list


class NeuralNetworkTropesEvaluator(BaseScript):
    _logger = logging.getLogger(__name__)

    def __init__(self, neural_network_dumped_file: str, films_extended_information_file: str):
        self._load_neural_network(neural_network_dumped_file)
        self._load_tropes_and_trope_indexes(films_extended_information_file)
        self._track_step('Ready to evaluate')

    def _load_neural_network(self, neural_network_dumped_file):
        self._track_step('Loading neural network')
        self.neural_network = joblib.load(neural_network_dumped_file)

    def _load_tropes_and_trope_indexes(self, films_extended_information_file):
        self._track_step('Loading tropes and trope indexes')

        meta_column_names = ['Id', 'NameTvTropes', 'NameIMDB', 'Votes', 'Year']
        rating_column_name = 'Rating'
        index_first_trope = len(meta_column_names) + 1

        with open(films_extended_information_file) as file:
            first_line = file.readline()

        columns = first_line.split(',')
        self.tropes = columns[index_first_trope:]
        self.tropes_reverse_index = {}
        for index, trope in enumerate(self.tropes):
            self.tropes_reverse_index[trope] = index

        self.base_empty_input = [0 for index in range(0, len(self.tropes))]

    def evaluate(self, list_of_tropes: list):
        self._track_message(f'Evaluating {list_of_tropes}')
        trope_indexes = self._build_list_of_trope_indexes(list_of_tropes)
        input = self._build_input(trope_indexes)
        predicted_rating = self.neural_network.predict([input])

        evaluation_tropes = [EvaluationTrope(name=self.tropes[index], index=index) for index in trope_indexes]
        evaluation = Evaluation(tropes=evaluation_tropes, rating=predicted_rating)
        return evaluation

    def evaluate_just_rating(self, list_of_tropes: list):
        #self._track_message(f'Evaluating just the rating {list_of_tropes}')
        trope_indexes = self._build_list_of_trope_indexes(list_of_tropes)
        input = self._build_input(trope_indexes)
        return self.neural_network.predict([input])

    def _build_input(self, trope_indexes):
        input = self.base_empty_input.copy()
        for index in trope_indexes:
            input[index] = 1
        return input

    def _build_list_of_trope_indexes(self, list_of_tropes):
        return [element if isinstance(element, int) else self.tropes_reverse_index[element]
                for element in list_of_tropes]


class Evaluation(object):
    def __init__(self, tropes, rating: float):
        self.tropes = tropes
        self.rating = rating

    def __str__(self):
        return f'Evaluation [{humanize_list(self.tropes)}]->{self.rating}'


class EvaluationTrope(object):
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index

    def __str__(self):
        return f'{self.name}:{self.index}'


if __name__ == "__main__":
    neural_network_file = u'/Users/phd/workspace/made/made_recommender/datasets/MLPRegressor_relu_3120_100_adam.sav'
    films_file = u'/Users/phd/workspace/made/made_recommender/datasets/film_extended_information_unique_values.csv'
    evaluator = NeuralNetworkTropesEvaluator(neural_network_file, films_file)
    evaluation = evaluator.evaluate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(evaluation)

    the_avengers_2012_tropes = 'AMatchMadeInStockholm,ActionAdventureTropes,ActionGenre,Administrivia,AnimationTropes,Anime,AppliedPhlebotinum,AssassinOutclassin,AvengersAssemble,BadPresent,BetrayalTropes,BigBad,BritishTellyTropes,CensorshipTropes,CharacterizationTropes,Characters,CharactersAsDevice,CombatTropes,ComedyTropes,ComicBookMoviesDontUseCodenames,ComicBookTropes,CommercialsTropes,CreatorSpeak,Creators,CrimeAndPunishmentTropes,DeathTropes,DerivativeWorks,Dialogue,DramaTropes,DysfunctionJunction,FamilyTropes,FanFic,FateAndProphecyTropes,Film,FilmsOfThe2010sFranchises,FishOutOfTemporalWater,FoodTropes,GameTropes,GreaterScopeVillain,HolidayTropes,HorrorTropes,HulkingOut,LanguageTropes,LawsAndFormulas,Literature,LiveActionAdaptation,LoveTropes,Media,MemoryTropes,MoneyTropes,MoralityTropes,Motifs,MusicAndSoundEffects,NarrativeDevices,NewMediaTropes,NewsTropes,Paratext,PhysicalGod,PlotDevice,Plots,PoliticsTropes,PowerArmor,PrintMediaTropes,ProfessionalWrestling,Pun,Radio,ReligionTropes,RideTheRainbow,RiffTraxMovies,SaveTheWorld,SchoolTropes,SequentialArt,Settings,ShowBusiness,Spectacle,SpeculativeFictionTropes,SplitPersonalityTropes,SportsStoryTropes,StockRoom,SuperTeam,Superhero,TabletopGames,Tagline,TakeOverTheWorld,TheContributors,Theater,TropeOverdosed,TropeTropes,Tropes,TruthAndLies,TruthInTelevision,UniversalTropes,VideogameTropes,WarTropes,Webcomics,genre_Action,genre_Adventure,genre_Sci-Fi'
    evaluation = evaluator.evaluate(the_avengers_2012_tropes.split(','))
    print(evaluation)

    pulp_fiction_tropes = 'AFIS100Years100Movies,AFIS100Years100Movies10THAnniversaryEdition,AFIS100Years100Thrills,ActionAdventureTropes,ActorAllusion,AddedAlliterativeAppeal,Administrivia,AdultFear,AffablyEvil,AfroAsskicker,AlasPoorVillain,AllThereInTheScript,AlliterativeName,AloneWithThePsycho,AnAesop,AnachronicOrder,AndStarring,AnimationTropes,Anime,AnthologyFilm,AntiHero,AppliedPhlebotinum,ArtisticLicenseGunSafety,ArtisticLicenseMedicine,AsHimself,AsLongAsItSoundsForeign,AsTheGoodBookSays,AsianStoreOwner,AssShove,AssholeVictim,AudibleSharpness,AuthorAppeal,AvertedTrope,BadassBack,BadassBoast,BadassCreed,BaldBlackLeaderGuy,BatterUp,BeamMeUpScotty,BeautyIsNeverTarnished,BerserkButton,BetrayalTropes,BigBad,BigNo,BigShutUp,BlackAndGrayMorality,BlackComedy,BlackComedyRape,BlahBlahBlah,BlatantLies,BloodyHilarious,BlownAcrossTheRoom,BookEnds,BoundAndGagged,Bowdlerise,BreakThemByTalking,BreakUpMakeUpScenario,BrickJoke,BritishTellyTropes,BumblingSidekick,CIA,CainAndAbel,CallingYourBathroomBreaks,CampingACrapper,CasualtyInTheRing,CatapultNightmare,CatchPhrase,CavalierConsumption,CensorshipTropes,CentralTheme,ChainsawGood,ChanceMeetingBetweenAntagonists,CharacterizationTropes,Characters,CharactersAsDevice,CleanupCrew,ClicheStorm,Cloudcuckoolander,ClusterFBomb,ColdBloodedTorture,CombatTropes,ComedyTropes,ComicBookTropes,CommercialsTropes,ConscienceMakesYouGoBack,ContrivedCoincidence,CoolCar,CreatorCameo,CreatorSpeak,Creators,CreditsGag,CrimeAndPunishmentTropes,CriminalProcedural,CultSoundtrack,CutHisHeartOutWithASpoon,DeathTropes,DeconstructiveParody,DecoyProtagonist,DepravedHomosexual,DerivativeWorks,DestinationDefenestration,DiagonalCut,Dialogue,DictionaryOpening,DiesWideOpen,DirtyCop,Discussed,DisposingOfABody,DisproportionateRetribution,DivineIntervention,DoesNotLikeShoes,DoubleSubverted,DoubleTake,DramaTropes,DramaticGunCock,DrivesLikeCrazy,DrivingADesk,DropTheHammer,DroppedABridgeOnHim,DrugsAreBad,EarnYourHappyEnding,EnemyEatsYourLunch,EnemyMine,EnsembleCast,EpicFail,EqualOpportunityEvil,EvenEvilHasLovedOnes,EvenEvilHasStandards,EvilIsHammy,ExactWords,FamilyTropes,FamousLastWords,FanDisservice,FanFic,FateAndProphecyTropes,FateWorseThanDeath,FauxAffablyEvil,Film,FilmsOf19901994,FiveManBand,FlatEarthAtheist,FoodTropes,ForWantOfANail,Foreshadowing,FreestateAmsterdam,FunnyBackgroundEvent,GameTropes,GeniusDitz,Gorn,GoryDiscretionShot,GroinAttack,HalfwayPlotSwitch,HallwayFight,HandCannon,HashHouseLingo,HatesSmallTalk,HeelFaithTurn,HeelRealization,HeldGaze,HolidayTropes,HollywoodSilencer,HolyHitman,HorrorTropes,HypercompetentSidekick,HyperlinkStory,HypocriticalHumor,IJustShotMarvinInTheFace,IceCreamKoan,ImOkay,ImagineSpot,ImperialStormtrooperMarksmanshipAcademy,ImpliedTrope,InTheNameOfTheMoon,InUniverse,InformedAttractiveness,InsistentTerminology,IntercourseWithYou,IronicEcho,Irony,ItHasOnlyJustBegun,Jerkass,JiveTurkey,JustForPun,KarmaHoudini,KatanasAreJustBetter,LanguageTropes,LargeHam,LaserGuidedKarma,LawsAndFormulas,LeftTheBackgroundMusicOn,LeftYourLifesaverBehind,LetUsNeverSpeakOfThisAgain,LethallyExpensive,LethallyStupid,LiteralMinded,Literature,LoveTropes,MacGuffin,MagicBullets,MaltShop,ManicPixieDreamGirl,MarilynManeuver,MaybeMagicMaybeMundane,MeaningfulBackgroundEvent,MeaningfulName,Media,MementoMacGuffin,MemeticMutation,MemoryTropes,MessyPig,MexicanStandoff,MoneyTropes,MoodWhiplash,MoralDilemma,MoralityTropes,Motifs,MuggingTheMonster,MusicAndSoundEffects,NWordPrivileges,NarrativeDevices,NewMediaTropes,NewsTropes,NobodyPoops,NoodleImplements,NoodleIncident,NotableQuotables,OddCouple,OffscreenMomentOfAwesome,OhCrap,OneLinerNameOneLiner,OnlyAFleshWound,OnlyKnownByTheirNickname,OutlawCouple,PackagedAsOtherMedium,PantsPositiveSafety,Paratext,PayEvilUntoEvil,PedalToTheMetalShot,PersonaNonGrata,PinkMist,PlayedForLaughs,Plots,PoliticallyIncorrectVillain,PoliticsTropes,PornStache,PreAsskickingOneLiner,PreMortemOneLiner,PrecisionFStrike,PrettyLittleHeadshots,Pride,PrintMediaTropes,ProfessionalWrestling,PulpMagazine,PunctuatedForEmphasis,PunkInTheTrunk,Radio,RandomEventsPlot,RapeAsDrama,RapeIsASpecialKindOfEvil,RapePortrayedAsRedemption,ReCut,RealMenTakeItBlack,RealityEnsues,ReferenceOverdosed,RefugeInAudacity,ReligionTropes,RetiredMonster,RetroUniverse,RiddleForTheAges,RogerEbertGreatMoviesList,RuleOfCool,RuleOfThree,RunningGag,ScaryBlackMan,SceneryPorn,SchoolStudyMedia,SchoolTropes,SeanConneryIsAboutToShootYou,SeinfeldianConversation,SequentialArt,SerialKiller,SeriousBusiness,Settings,ShareTheMalePain,SharedUniverse,SheIsNotMyGirlfriend,ShipTease,ShotToTheHeart,ShoutOut,ShowBusiness,ShownTheirWork,SickeningSweethearts,SignatureStyle,SignsOfDisrepair,SmokingIsCool,SoulBrotha,SoundtrackDissonance,Spectacle,SpeculativeFictionTropes,SpeechImpediment,SpiritualSuccessor,SplitPersonalityTropes,SportsStoryTropes,StockRoom,StopSayingThat,StrayShotsStrikeNothing,StupidCrooks,StylisticSuck,SurfRock,TabletopGames,TakeOurWordForIt,TheAtoner,TheCameo,TheContributors,TheFifties,TheKnightsWhoSaySquee,TheLoad,TheMenInBlack,TheMole,TheNineties,ThePreciousPreciousCar,ThePublicDomainChannel,TheReveal,TheSomethingForce,TheThemeParkVersion,Theater,ThereAreNoPolice,ThereIsNoKillLikeOverkill,ThirdPersonFlashback,ThoseTwoBadGuys,ThrowingTheFight,ToThePain,TooDumbToLive,TortureCellar,TragicKeepsake,TranslationByVolume,TreasureChestCavity,TropeCodifier,TropeNamers,TropeTropes,Tropes,TrunkShot,TruthAndLies,TruthInTelevision,UnderdressedForTheOccasion,Unishment,UniversalTropes,UnusuallyUninterestingSight,UpToEleven,VerbalBusinessCard,VictimizedBystander,VideogameTropes,VillainEatsYourLunch,VillainProtagonist,VillainsOutShopping,VisualPun,VitriolicBestBuds,WackyCravings,WalkingTheEarth,WarTropes,WaxingLyrical,Webcomics,WhamLine,WhatAnIdiot,WhatHappenedToTheMouse,WhatYouAreInTheDark,WolverinePublicity,WordOfGod,WorstAid,genre_Crime,genre_Drama'
    evaluation = evaluator.evaluate(pulp_fiction_tropes.split(','))
    print(evaluation)

    alone_in_the_dark_tropes = 'AbandonedHospital,AbandonedMine,AccentUponTheWrongSyllable,ActionAdventureTropes,Administrivia,AnimationTropes,Anime,AppliedPhlebotinum,ArtisticLicenseMartialArts,BMovie,BetrayalTropes,BizarreAndImprobableBallistics,BritishTellyTropes,CaptainErsatz,CensorshipTropes,CharacterizationTropes,Characters,CharactersAsDevice,ChewingTheScenery,CoitusEnsues,ColorCodedSecretIdentity,CombatTropes,ComedyTropes,ComicBookTropes,CommercialsTropes,CreatorSpeak,Creators,CrimeAndPunishmentTropes,DeathTropes,DerivativeWorks,Dialogue,DramaTropes,EasyAmnesia,EveryBulletIsATracer,FamilyTropes,FanFic,FateAndProphecyTropes,Film,FilmsOf20052009,FlippingTheTable,FoodTropes,GameTropes,HolidayTropes,HorrorFilms,HorrorTropes,HotScientist,InNameOnly,JumpCut,LanguageTropes,LawsAndFormulas,Literature,LoveTropes,MadScientist,Media,MemoryTropes,MoneyTropes,MoralityTropes,Motifs,MusicAndSoundEffects,NarrativeDevices,NeverMyFault,NewMediaTropes,NewsTropes,NippleAndDimed,OpeningScroll,Paratext,PlayingAgainstType,PlotHole,Plots,PoliticsTropes,Precursors,PrintMediaTropes,ProfessionalWrestling,ProlongedPrologue,PromotedToLoveInterest,Radio,ReligionTropes,RetCanon,RuleOfCool,SchoolTropes,SealedEvilInACan,SequelHook,SequentialArt,Settings,ShakyPOVCam,ShowBusiness,SlapSlapKiss,SoundtrackDissonance,Spectacle,SpeculativeFictionTropes,SplitPersonalityTropes,SportsStoryTropes,StockRoom,SurvivalHorror,TabletopGames,TheContributors,TheLivingDead,Theater,ThereWasADoor,TropeMaker,TropeTropes,Tropes,TruthAndLies,TruthInTelevision,UniversalTropes,ValuesDissonance,VideoGameMovies,VideogameTropes,WallOfText,WarTropes,Webcomics,WhatCouldHaveBeen,genre_Action,genre_Horror,genre_Sci-Fi'
    evaluation = evaluator.evaluate(alone_in_the_dark_tropes.split(','))
    print(evaluation)

    print(evaluator.evaluate_just_rating(alone_in_the_dark_tropes.split(',')))

import logging
import time
from random import Random

import cachetools
import inspyred
from inspyred.ec.analysis import fitness_statistics

from common.base_script import BaseScript
from rating_evaluator.neural_network_tropes_evaluator import NeuralNetworkTropesEvaluator


class Solution(object):
    def __init__(self, trope_list, fitness):
        self.trope_list = trope_list
        self.fitness = fitness


class TropeRecommender(BaseScript):
    def __init__(self, neural_network_file: str, films_file: str, summary_file_name: str):
        self.summary_file_name = summary_file_name

        self.seed = 0
        self.list_of_constrained_tropes = []
        self.solution_length = 0
        self.max_evaluations = 0
        self.mutation_probability = 0
        self.crossover_probability = 0
        self.population_size = 0
        self.details_file_name = ''
        self.execution_name = ''
        self.no_better_results_during_evaluations = 0
        self.best_fitness_ever = None
        self.best_candidate_ever = None
        self.last_evaluation_that_improved = 0

        self.evaluator = NeuralNetworkTropesEvaluator(neural_network_file, films_file)
        self.tropes = self.evaluator.tropes
        self.tropes_indexes = list(range(0, len(self.tropes)))
        self.cache = cachetools.LRUCache(5000, missing=None, getsizeof=None)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M:%m', )

    def _init_execution_parameters(self, crossover_probability, details_file_name, execution_name,
                                   list_of_constrained_tropes, max_evaluations, mutation_probability,
                                   no_better_results_during_evaluations, population_size, seed, solution_length):
        self.seed = seed
        self.list_of_constrained_tropes = list_of_constrained_tropes
        self.solution_length = solution_length
        self.max_evaluations = max_evaluations
        self.mutation_probability = mutation_probability
        self.crossover_probability = crossover_probability
        self.population_size = population_size
        self.details_file_name = details_file_name
        self.execution_name = execution_name
        self.no_better_results_during_evaluations = no_better_results_during_evaluations

        self.best_fitness_ever = None
        self.best_candidate_ever = None
        self.last_evaluation_that_improved = 0
        self.random = Random(self.seed)

    def optimize(self, seed: int, list_of_constrained_tropes: list, solution_length: int, max_evaluations: int,
                 mutation_probability: float, crossover_probability: float, population_size: int,
                 details_file_name: str, execution_name: str,
                 no_better_results_during_evaluations: int):
        self._init_execution_parameters(crossover_probability, details_file_name, execution_name,
                                        list_of_constrained_tropes, max_evaluations, mutation_probability,
                                        no_better_results_during_evaluations, population_size, seed, solution_length)

        start = time.time()

        ea = inspyred.ec.GA(self.random)
        ea.selector = inspyred.ec.selectors.tournament_selection
        ea.terminator = self.build_terminator()
        ea.variator = [self.build_mutator(), inspyred.ec.variators.crossover(self.build_crossover_as_subset_operator())]
        ea.observer = self.build_observer()
        ea.evaluator = self.build_evaluator()
        final_pop = ea.evolve(generator=self.build_generator(), evaluator=ea.evaluator,
                              max_evaluations=self.max_evaluations, pop_size=self.population_size)

        trope_list = sorted([self.tropes[index] for index in self.best_candidate_ever])

        seconds = time.time() - start

        summary = ", ".join(
            [self.execution_name, str(self.best_fitness_ever), str(int(seconds))] + trope_list)
        self.log_summary_line(summary)

        return Solution(trope_list, self.best_fitness_ever)

    def build_terminator(self):
        def terminator(population, num_generations, num_evaluations, args):
            # stats = fitness_statistics(population)
            # best_fitness_in_population = stats['best'][0]
            # if self.best_fitness_ever is None or self.best_fitness_ever < best_fitness_in_population:
            #    self.best_fitness_ever = best_fitness_in_population
            #    self.best_candidate_ever = max(population)
            #    self.last_evaluation_that_improved = num_evaluations

            evaluation_is_above_max = num_evaluations >= self.max_evaluations
            evaluations_without_improvement = num_evaluations - self.last_evaluation_that_improved
            max_did_not_change_enough = evaluations_without_improvement >= self.no_better_results_during_evaluations

            print("Evaluations " + str(num_evaluations) + ", max_evaluations " + str(self.max_evaluations)
                  + ", last_evaluation_that_improved " + str(self.last_evaluation_that_improved)
                  + ", best_ind " + str(self.best_fitness_ever))

            if evaluation_is_above_max and max_did_not_change_enough:
                return True

            return False

        return terminator

    def build_mutator(self):
        def mutator(random, candidates, args):
            mutants = []
            for candidate in candidates:

                mutant = candidate.copy()
                unused_tropes = set(set(self.tropes_indexes) - set(candidate))

                for index in range(0, len(candidate)):
                    if self.should_mutate(random):
                        new_trope = random.choice(list(unused_tropes))

                        unused_tropes.remove(new_trope)
                        unused_tropes.add(mutant[index])

                        mutant[index] = new_trope
                mutants.append(mutant)
            return mutants

        return mutator

    def should_mutate(self, random):
        return random.random() <= self.mutation_probability

    def build_crossover_as_subset_operator(self):
        def crossover(random, mom, dad, args):
            if self.should_crossover(random):
                superset = set(mom).union(set(dad))
                all_candidates = list(superset)
                random.shuffle(all_candidates)
                first_child = all_candidates[0:self.solution_length]
                first_child.sort()

                random.shuffle(all_candidates)
                second_child = all_candidates[0:self.solution_length]
                second_child.sort()

                return [first_child, second_child]
            else:
                return [mom, dad]

        return crossover

    def should_crossover(self, random):
        return random.random() <= self.crossover_probability

    def build_observer(self):
        def observer(population, num_generations, num_evaluations, args):
            stats = fitness_statistics(population)
            best_fitness_in_population = stats['best'][0]
            if self.best_fitness_ever is None or self.best_fitness_ever < best_fitness_in_population:
                self.best_fitness_ever = best_fitness_in_population
                self.best_candidate_ever = max(population).candidate
                self.last_evaluation_that_improved = num_evaluations

            # stats = fitness_statistics(population)
            # best_individual = max(population, key=lambda x: x.fitness)

            log = [num_generations, self.best_fitness_ever, stats['best'][0], stats['worst'][0], stats['mean'],
                   stats['median'], stats['std']]
            # log += sorted(best_individual.candidate)
            log += sorted(self.best_candidate_ever)
            log = [str(round(value, 3)) if value is not None else '0' for value in log]
            log.insert(0, self.execution_name)
            self.log_detail_line(",".join(log))

            # print ("Geneneration={!s}. Best fitness={!s}".format(num_generations, best_individual.fitness))

        return observer

    def build_evaluator(self):
        parent = self

        def evaluator(candidates, args):
            fitnesses = []
            for candidate in candidates:
                fitness = parent._calculate_fitness(candidate)
                fitnesses.append(fitness)
            return fitnesses

        return evaluator

    def _calculate_fitness(self, candidate):
        cache_key, cached_fitness = self.try_get_cached_fitness(candidate)
        if cached_fitness is not None:
            return cached_fitness

        fitness = self.evaluator.evaluate_just_rating(candidate)
        self.cache.__setitem__(cache_key, fitness)
        return fitness

    def try_get_cached_fitness(self, candidate):
        cache_key = ",".join([str(element) for element in sorted(candidate)])
        cached_fitness = self.cache.get(cache_key, None)
        return cache_key, cached_fitness

    def build_generator(self):
        def generator(random, args):
            return random.sample(self.tropes_indexes, self.solution_length)

        return generator

    def log_detail_line(self, content):
        self.log_line(content, self.details_file_name)

    def log_summary_line(self, content):
        self.log_line(content, self.summary_file_name)

    def log_line(self, content, file_name):
        if file_name is None:
            print(content)
        else:
            with open(file_name, "a") as file:
                file.write(content + "\n")


if __name__ == "__main__":
    neural_network_file = u'/Users/phd/workspace/made/made_recommender/datasets/evaluator_[26273, 162, 1].sav'
    films_file = u'/Users/phd/workspace/made/made_recommender/datasets/extended_dataset.csv.bz2'
    general_summary = u'/Users/phd/workspace/made/made_recommender/datasets/recommender_logs/general_2.log'

    details_file_name = u'/Users/phd/workspace/made/made_recommender/datasets/recommender_logs/details_2.log'
    recommender = TropeRecommender(neural_network_file, films_file, general_summary)
    now = time.time()
    recommender.optimize(seed=1, list_of_constrained_tropes=[], solution_length=42, max_evaluations=30000,
                         mutation_probability=0.0116, crossover_probability=0.5, population_size=50,
                         details_file_name=details_file_name, execution_name=f'sample_{now}',
                         no_better_results_during_evaluations=30000)
    exit(0)

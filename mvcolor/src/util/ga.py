#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import random
from copy import copy

from deap.algorithms import varAnd
from deap import base
from deap import creator
from deap import tools

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from deap.algorithms import varAnd

def ga(fitness_function, _range, genome_length, pop_size, iterations, cxpb, mutpb):
    # modified Deap.algorithm.eaSimple
    def eaSimple(population, toolbox, cxpb, mutpb, ngen, stats=None, halloffame=None, verbose=__debug__):
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals', 'best'] + (stats.fields if stats else [])
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats else {}
        logbook.record(gen=0, nevals=len(invalid_ind), best=fitness_function(halloffame[0])[0], **record)
        if verbose:
            print(logbook.stream)

        # Begin the generational process
        for gen in range(1, ngen + 1):
            # Select the next generation individuals
            offspring = toolbox.select(population, len(population))

            # Vary the pool of individuals
            offspring = varAnd(offspring, toolbox, cxpb, mutpb)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Replace the current population by the offspring
            population[:] = offspring

            # Append the current generation statistics to the logbook
            record = stats.compile(population) if stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), best=fitness_function(halloffame[0])[0], **record)
            if verbose:
                print(logbook.stream)

        return population, logbook
    
    # Customize initial population
    def load_individuals(creator, n):
        individuals = []
        population = np.zeros(shape=(0, genome_length), dtype=np.int32)
        for iteration in range(n):
            genome = copy(_range)

            while True:
                random.shuffle(genome)
                # check if genome exists in pop
                if any(np.equal(population, genome[:genome_length]).all(1)): continue
                population = np.append(population, np.array([copy(genome[:genome_length])]), axis=0)
                individual = copy(genome)
                individual = creator(individual)
                individuals.append(individual)
                break
            
        return individuals
        
    def customize_population_config(creator, toolbox):
        toolbox.register("population", load_individuals,  creator.Individual)

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

    # Define toolbox
    toolbox = base.Toolbox()
    customize_population_config(creator, toolbox)

    toolbox.register("evaluate", fitness_function)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selRoulette)

    # ========== Start Genetic Algorithm =========
    random.seed(64)
    # Initialize population
    pop = toolbox.population(n=pop_size)
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    hof = tools.HallOfFame(1, similar=np.array_equal)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    pop, logbook = eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, 
                                   ngen=iterations, stats=stats, halloffame=hof, verbose=False)
    
    # Pick fittest
    fittest_individual, max_fitness = hof[0].tolist(), fitness_function(hof[0])[0]

    # # plotting Generations vs Min to see convergence for each generation
    # plt.figure(figsize=(20, 10))

    # # # using select method in logbook object to extract the argument/key as list
    # plt.plot(logbook.select('gen'), logbook.select('best'))

    # plt.xlabel("Generations",fontsize=18,fontweight='bold')
    # plt.ylabel("Value of Fitness Function",fontsize=18,fontweight='bold')
    # plt.xticks(fontweight='bold')
    # plt.yticks(fontweight='bold')

    # plt.savefig("convergence.jpg")

    return fittest_individual
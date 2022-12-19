import json
import pygad
import numpy
from constants import sinnoh_pokemon

data = {}
toggleable_trainers = []
leftover_pokes = []

def cmpfunc(pokemonHave):
    return lambda team1: len([i for i in team_of_trainer(team1) if not(i in pokemonHave)])

def team_of_trainer(trainer):
    global data
    return set([i for i in data["trainers"][trainer]["pokemon"] if i!="-" and i in sinnoh_pokemon])

def team_of_trainers(trainers):
    teams = set()
    for x in trainers:
        teams = teams | team_of_trainer(x)
    return teams

def team_length(trainer):
    global data
    return len([i for i in data["trainers"][trainer]["pokemon"] if i!="-"])

def at_or_default(list, index, default):
    return list[index] if 0 <= index < len(list) else default

def filter_trainers(available, partner, rematch, starter):
    global data
    filtered_set = {x["id"] for x in data["trainers"]}
    filtered_set = {x for x in filtered_set if data["trainers"][x]["available"] in available}
    filtered_set = {x for x in filtered_set if data["trainers"][x]["partner"] in partner}
    filtered_set = {x for x in filtered_set if data["trainers"][x]["rematch"] in rematch}
    filtered_set = {x for x in filtered_set if data["trainers"][x]["starter"] in starter}
    return filtered_set

def load_trainers(trainers_file):
    global data
    with open(trainers_file, encoding='utf8') as trainer_json:
        data = json.load(trainer_json)

def occurence_counts(trainers_file, out_file, available_values, partner_values, rematch_values, starter_values):
    global data
    load_trainers(trainers_file)
    filtered_data = filter_trainers(available_values, partner_values, rematch_values, starter_values)
    
    counts = {x:0 for x in sinnoh_pokemon}
    for trainer in filtered_data:
        for pokemon in data["trainers"][trainer]["pokemon"]:
            if pokemon in counts:
                counts[pokemon] = counts[pokemon] + 1

    with open(out_file, 'w', encoding='utf8') as out_json:
        json.dump(counts, out_json, ensure_ascii=False, indent=4)

def dn_greedy(trainers_file, out_file, available_values, partner_values, rematch_values, starter_values):
    global data
    unnecessary = set()

    load_trainers(trainers_file)
    filtered_data = filter_trainers(available_values, partner_values, rematch_values, starter_values)

    search_trainer = filtered_data

    for i in search_trainer:
        for j in search_trainer:
            if i==j:continue
            if len(team_of_trainer(j))>len(team_of_trainer(i)) and team_of_trainer(i).issubset(team_of_trainer(j)):
                unnecessary.add(i)
                break
    search_trainer = search_trainer - unnecessary
    
    counts = {x:0 for x in sinnoh_pokemon}
    for trainer in search_trainer:
        for pokemon in data["trainers"][trainer]["pokemon"]:
            if pokemon in counts:
                counts[pokemon] = counts[pokemon] + 1
    #can the entire dex be made with only disjoint subsets?
    #pick the trainer with the most distinct pokemon

    covered = []
    candidates = search_trainer
    mustBattle = []
    counts2 = {x:0 for x in sinnoh_pokemon}
    
    while counts!=counts2 and len(candidates) > 0:
        candidates = sorted(candidates, key=cmpfunc(covered),reverse=True)
        for t in team_of_trainer(candidates[0]):
            counts2[t]=1
        covered = list(covered) + list(team_of_trainer(candidates[0]))
        covered = set(covered)
        mustBattle += [candidates[0]]
        candidates = candidates[1::]
    
    test = set()

    output = {
        "impossible_pokemon": [i for i,x in counts2.items() if x == 0],
        "trainers": [data["trainers"][x] for x in mustBattle]
    }
    
    with open(out_file, 'w', encoding='utf8') as out_json:
        json.dump(output, out_json, ensure_ascii=False, indent=4)

def remove_from_search(search_pokemon, search_trainer, trainers_to_remove):
    search_pokemon = search_pokemon - team_of_trainers(trainers_to_remove)
    search_trainer = search_trainer - trainers_to_remove
    search_trainer = search_trainer - {x for x in search_trainer if not (team_of_trainer(x) & search_pokemon)}
    return search_pokemon, search_trainer

def find_single_instances(search_pokemon, search_trainer):
    unavailable_pokes = set()
    mandatory_trainers = set()
    mandatory_pokemon = set()
    for pokemon in search_pokemon:
        trainers_with_poke = set()
        for trainer in search_trainer:
            if pokemon in team_of_trainer(trainer):
                trainers_with_poke.add(trainer)
            if len(trainers_with_poke) > 1:
                break
        if len(trainers_with_poke) == 0:
            unavailable_pokes.add(pokemon)
            mandatory_pokemon.add(pokemon)
        elif len(trainers_with_poke) == 1:
            mandatory_trainers = mandatory_trainers | trainers_with_poke
            mandatory_pokemon.add(pokemon)
    return unavailable_pokes, mandatory_pokemon, mandatory_trainers

def update_results_from_single_instances(result_pokes, result_trainers, search_pokemon, search_trainer):
    # Find Pokémon with only one trainer
    unavailable_pokes, mandatory_pokemon, mandatory_trainers = find_single_instances(search_pokemon, search_trainer)
    
    # Add mandatory trainers and impossible pokes
    result_pokes = result_pokes | unavailable_pokes
    result_trainers = result_trainers | mandatory_trainers
    
    # Remove extra stuff from search lists
    search_pokemon = search_pokemon - mandatory_pokemon
    search_pokemon, search_trainer = remove_from_search(search_pokemon, search_trainer, mandatory_trainers)

    return result_pokes, result_trainers, search_pokemon, search_trainer

def mandatory_trainer_calcs(trainers_file, out_file, available_values, partner_values, rematch_values, starter_values, forced_trainers, impossible_trainers):
    global data
    load_trainers(trainers_file)
    filtered_data = filter_trainers(available_values, partner_values, rematch_values, starter_values)

    search_pokemon = set(sinnoh_pokemon)
    search_trainer = filtered_data

    result_trainers = set()
    result_pokes = set()


    # Add passed forced trainers to result set
    forced_added = {x for x in search_trainer if x in forced_trainers}
    result_trainers = result_trainers | forced_added

    # Remove extra stuff from search lists
    search_pokemon, search_trainer = remove_from_search(search_pokemon, search_trainer, forced_added)


    # Remove passed impossible trainers from search lists
    forced_removed = {x for x in search_trainer if x in impossible_trainers}
    search_trainer = search_trainer - forced_removed


    # Update results by removing pokes on a single trainer
    result_pokes, result_trainers, search_pokemon, search_trainer = update_results_from_single_instances(result_pokes, result_trainers, search_pokemon, search_trainer)


    # Remove longer/same teams and subsets
    trainer_similar = set()
    count = 0
    for i in search_trainer:
        for j in search_trainer:
            if i == j: continue
            if team_length(i) < team_length(j) and team_of_trainer(i) == team_of_trainer(j):
                if not(i in trainer_similar): trainer_similar.add(j)
                break
    search_trainer = search_trainer - trainer_similar
    trainer_subset = set()
    count = 0
    for i in search_trainer:
        for j in search_trainer:
            if i == j: continue
            if len(team_of_trainer(i)) > len(team_of_trainer(j)) and team_of_trainer(j).issubset(team_of_trainer(i)):
                trainer_subset.add(j)
                break
    search_trainer = search_trainer - trainer_subset

    # Update results by removing pokes on a single trainer
    result_pokes, result_trainers, search_pokemon, search_trainer = update_results_from_single_instances(result_pokes, result_trainers, search_pokemon, search_trainer)

    return result_pokes, result_trainers, search_pokemon, search_trainer

def check_leftover_pokes(solution):
    global toggleable_trainers
    global leftover_pokes
    trainers = [x for i,x in enumerate(toggleable_trainers) if solution[i] == 1]
    missing_pokes = leftover_pokes - team_of_trainers(trainers)
    return len(missing_pokes)

def fitness_func(solution, solution_idx):
    missing_pokes = check_leftover_pokes(solution)
    if missing_pokes > 0:
        return -missing_pokes
    else:
        trainers = [data["trainers"][x] for i,x in enumerate(toggleable_trainers) if solution[i] == 1]
        locations = set([x["location"] for x in trainers])
        pokes = team_of_trainers([x for i,x in enumerate(toggleable_trainers) if solution[i] == 1])
        fitness = 1.0 / (len(locations) * 8 + len(trainers) * 2 + len(pokes) * 1)
        return fitness

def on_fitness(ga_instance, population_fitness):
    print("Generation {gen}, Fitness {fitness}".format(gen=ga_instance.generations_completed,fitness=population_fitness))

def genetic_algo(trainers_file, out_file, available_values, partner_values, rematch_values, starter_values, forced_trainers, impossible_trainers):
    result_pokes, result_trainers, search_pokemon, search_trainer = mandatory_trainer_calcs(trainers_file, out_file, available_values, partner_values, rematch_values, starter_values, forced_trainers, impossible_trainers)

    # Keep toggleable trainers and leftover pokes in memory
    global toggleable_trainers
    global leftover_pokes
    toggleable_trainers = list(search_trainer)
    leftover_pokes = search_pokemon

    # PyGAD params
    fitness_function = fitness_func
    num_generations = 50
    num_parents_mating = 4
    sol_per_pop = 8
    num_genes = len(toggleable_trainers)
    parent_selection_type = "sss"
    keep_parents = 1
    crossover_type = "single_point"
    mutation_type = "random"
    mutation_percent_genes = 5
    gene_space = [0, 1]
    
    # Run GA
    ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_space=gene_space,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_percent_genes=mutation_percent_genes,
                       on_fitness=on_fitness)
    ga_instance.run()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    prediction = {x for i,x in enumerate(toggleable_trainers) if solution[i] == 1} | result_trainers
    print("Best solution : {prediction}".format(prediction=prediction))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    ga_instance.plot_fitness()

    output = {
        "impossible_pokemon": [x for x in result_pokes],
        "trainers": [data["trainers"][x] for x in prediction]
    }
    
    with open(out_file, 'w', encoding='utf8') as out_json:
        json.dump(output, out_json, ensure_ascii=False, indent=4)
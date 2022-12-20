import json
import numpy
from constants import sinnoh_pokemon
from optimization_algorithm import load_trainers, team_of_trainers, team_length

def verify_solution(solution_file, trainers_file):
    with open(solution_file, encoding='utf8') as trainer_json:
        load_trainers(trainers_file)

        json_data = json.load(trainer_json)

        trainers = len(json_data["trainers"])
        pokes = numpy.sum([team_length(x["id"]) for x in json_data["trainers"]])

        handled_pokes = team_of_trainers([x["id"] for x in json_data["trainers"]])
        unhandled_pokes = set(sinnoh_pokemon) - set(json_data["impossible_pokemon"])
        missing_pokes = unhandled_pokes - handled_pokes

        print("This solution fights {trainers} trainers owning {pokes} Pokémon in total.".format(trainers=trainers,pokes=pokes))
        print("Unhandled Pokémon mentioned by solution: {unhandled_pokes}".format(unhandled_pokes=json_data["impossible_pokemon"]))
        if (len(missing_pokes) > 0):
            print("Pokémon completely missing from solution: {missing_pokes}".format(missing_pokes=missing_pokes))
        else:
            print("All Pokémon accounted for!")
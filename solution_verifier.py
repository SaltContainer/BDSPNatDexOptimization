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

def group_solution_by_location(solution_file, trainers_file, out_file):
    with open(solution_file, encoding='utf8') as trainer_json:
        load_trainers(trainers_file)

        json_data = json.load(trainer_json)
        locations = {x["location"] for x in json_data["trainers"]}

        with open(out_file, 'w', encoding='utf8') as out:
            print("Trainers sorted by location")
            out.write("Trainers sorted by location\n")
            print("===========================")
            out.write("===========================\n")
            for location in locations:
                trainers = [x for x in json_data["trainers"] if x["location"] == location]
                print("{location}:".format(location=location))
                out.write("{location}:\n".format(location=location))
                for trainer in trainers:
                    pokes = [x for x in trainer["pokemon"] if x != "-"]
                    print("\t{id} ({name}) for {pokes}".format(id=trainer["id"],name=trainer["name"],pokes=", ".join(pokes)))
                    out.write("\t{id} ({name}) for {pokes}\n".format(id=trainer["id"],name=trainer["name"],pokes=", ".join(pokes)))
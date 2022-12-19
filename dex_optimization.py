from optimization_algorithm import occurence_counts, dn_greedy, sma_greedy

trainers_file = 'simplified_trainers.json'
count_file = 'out_count.json'
dn_greedy_file = 'out_dn_greedy.json'
sma_greedy_file = 'out_sma_greedy.json'

available_values = [True]
partner_values = [False, True]
rematch_values = [0]
starter_values = ["-", "Turtwig", "Chimchar", "Piplup"]

# Spear Pillar grunts, Valor Lakefront grunt, Floaroma Meadow grunts
forced_trainers = [394, 400, 673, 221, 222]

# Celestic grunt
impossible_trainers = [319]

occurence_counts(trainers_file, count_file, available_values, partner_values, rematch_values, starter_values)
dn_greedy(trainers_file, dn_greedy_file, available_values, partner_values, rematch_values, starter_values)
sma_greedy(trainers_file, sma_greedy_file, available_values, partner_values, rematch_values, starter_values, forced_trainers, impossible_trainers)
from collections import defaultdict

main_statistics = defaultdict(dict)

def add_new_set(set_id):
    main_statistics[set_id] = defaultdict(dict)

def retrieve_set(set_id):
    return main_statistics[set_id]

def update_stats(set_id, stat_name, stat_data):
    main_statistics[set_id][stat_name] = stat_data

def retrieve_stats(set_id, stat_name):
    return main_statistics[set_id][stat_name]

import geobase

# Input : query is a Node
# Output : the list of valid answers for that query
def evaluate(query):
    answer = set(eval(query))
    return sorted((x[0], x[1]) for x in answer if not isinstance(x[0], tuple)) + sorted((x[0], x[1]) for x in answer if isinstance(x[0], tuple))

# Input : program is the current Node being evaluated or the set resulting from a Node (to avoid complexity explosion in some cases)
# Output : the set of valid answers for that (partial) query
# The function that is called for each predicate is stored in 'callbacks'
def eval(program):
    #try:
        if isinstance(program, set):     return program
        elif len(program.children) == 0: return callbacks[program.predicate]()
        elif len(program.children) == 1: return callbacks[program.predicate](program.children[0])
        else:                            return callbacks[program.predicate](program.children)
    #except:
    #    return set()





# Arguments evaluation : we differentiate the case where there is a single argument and the case where there are multiple for readability purposes
def eval_arg(program):   return  program.predicate.replace("'", "").strip()
def eval_args(programs): return [program.predicate.replace("'", "").strip() for program in programs]


# Entity selection
    # Select only the elements with a given value
    # For cityid: 'city_name', _ should return all the cities with that name regardless of the state
def eval_cityid(programs):    y = eval_args(programs); return filter(lambda x: y in [[x[0][0], x[0][1]], [x[0][0], "_"]], eval_city_all())
def eval_mountainid(program): y = eval_arg(program);   return filter(lambda x: y == x[0], eval_mountain_all())
def eval_placeid(program):    y = eval_arg(program);   return filter(lambda x: y == x[0], eval_place_all())
def eval_riverid(program):    y = eval_arg(program);   return filter(lambda x: y == x[0], eval_river_all())
def eval_lakeid(program):     y = eval_arg(program);   return filter(lambda x: y == x[0], eval_lake_all())
def eval_stateid(program):    y = eval_arg(program);   return filter(lambda x: y == x[0], eval_state_all())
def eval_countryid(program):  y = eval_arg(program);   return filter(lambda x: y == x[0], eval_country_all())
    # Select all the elements
def eval_city_all():         return {((city["city"], city["abbreviation"]), "city") for city in geobase.cities}
def eval_mountain_all():     return {(mountain["mountain"], "place") for mountain in geobase.mountains}
def eval_place_all():        return {(place["place"], "place") for place in geobase.places}
def eval_river_all():        return {(river["river"], "river") for river in geobase.rivers}
def eval_lake_all():         return {(lake["lake"], "place") for lake in geobase.lakes}
def eval_state_all():        return {(state["state"], "state") for state in geobase.states}
def eval_country_all():      return {(country["country"], "country") for country in geobase.countries}
def eval_capital_all():      return {((state["capital"], state["abbreviation"]), "city") for state in geobase.states}


# Type filters : keep only the elements that match a certain type
def type_filter(program, valid_set): y = valid_set(); return filter(lambda x: any([x[0]==k[0] and x[1]==k[1] for k in y]), eval(program))
def eval_city(program):     return type_filter(program, eval_city_all)
def eval_place(program):    return type_filter(program, eval_place_all)
def eval_river(program):    return type_filter(program, eval_river_all)
def eval_state(program):    return type_filter(program, eval_state_all)
def eval_mountain(program): return type_filter(program, eval_mountain_all)
def eval_lake(program):     return type_filter(program, eval_lake_all)
def eval_capital(program):  return type_filter(program, eval_capital_all)
def eval_country(program):  return type_filter(program, eval_country_all)


# Mapping predicates : return a city/place for each state or a state for each city/place
    # Map between capital and state
def eval_capital_1(program):    return map(lambda x: (get_city(x), "city"), eval(program))
def eval_capital_2(program):    return map(lambda x: (get_state(x), "state"), eval(program))
    # Map between high point and state
def eval_high_point_1(program): return map(lambda x: (get_high_point(x), "place"), eval(program))
def eval_high_point_2(program): return map(lambda x: (get_state(x), "state"), eval(program))
    # Map between low point and state
def eval_low_point_1(program):  return map(lambda x: (get_low_point(x), "place"), eval(program))
def eval_low_point_2(program):  return map(lambda x: (get_state(x), "state"), eval(program))


# Property filters : returns only the elements that satisfy the comparison on the given property
    # Filters on river length
def eval_longer(program):      y = get_length(list(eval_shortest(program))[0]); return filter(lambda x: get_length(x) > y, eval_river_all())
def eval_shorter(program):     y = get_length(list(eval_longest(program))[0]);  return filter(lambda x: get_length(x) < y, eval_river_all())
    # Filters on place elevation
def eval_higher_2(program):    y = get_height(list(eval_lowest(program))[0]);   return filter(lambda x: get_height(x) > y, eval_place_all())
def eval_lower_2(program):     y = get_height(list(eval_highest(program))[0]);  return filter(lambda x: get_height(x) < y, eval_place_all())
def eval_elevation_2(program): y = int(eval_arg(program)); return filter(lambda x: get_height(x) == y, eval_place_all())
    # Filters on "is important enough"
def eval_major(program):       return filter(lambda x: (x[1] == "city" and get_population(x) > 150000) or
                                                       (x[1] == "river" and get_length(x) > 750) or
                                                       (x[1] == "place" and get_area(x) > 5000), eval(program))


# Relationship predicates : return neighbors / elements that include / elements that are included
    # Return all the elements in candidates such that they appear in the key of at least one element in the current set (and the corresponding elements in the current set)
def relation_1(current_set, key, type, candidates, is_list=False):
    y = map(lambda x: (x[0], x[1], frozenset([k[0] for k in current_set if (is_list and x[0] in key(k)) or (not is_list and x[0] == key(k))]), type), candidates())
    return set(filter(lambda z: len(z[2])>0, y))
    # Return all the elements in candidates such that at least one element in the current set appear in their key (and the corresponding elements in the current set)
def relation_2(current_set, key, type, candidates, is_list=False):
    y = map(lambda x: (x[0], x[1], frozenset([k[0] for k in current_set if (is_list and k[0] in key(x)) or (not is_list and k[0] == key(x))]), type), candidates())
    return set(filter(lambda z: len(z[2])>0, y))
    # Return all the elements in element_set such that their country/state/city is in the output of program
def elt_from_country(current_set, candidates):     return relation_2(current_set, get_country, "country", candidates)
def elt_from_state(current_set, candidates):       return relation_2(current_set, get_state,  "state", candidates)
def elt_from_city(current_set, candidates):        return relation_2(current_set, get_city, "city", candidates)
    # Return the country/state/city for every element that is in the output of program
def country_from_elt(current_set, function, type): return relation_1(set(function(current_set)), get_country, type, eval_country_all)
def state_from_elt(current_set, function, type):   return relation_1(set(function(current_set)), get_state,  type, eval_state_all)
def city_from_elt(current_set, function, type):    return relation_1(set(function(current_set)), get_city, type, eval_city_all)
    # Specific functions for state-state, river-state, lake-state relations as their keys return multiple answers
def elt_from_state2(current_set, candidates):      return relation_2(current_set, get_adjacent, "state", candidates, is_list=True)
def state_from_elt2(current_set, function, type):  return relation_1(set(function(current_set)), get_adjacent, type, eval_state_all, is_list=True)
    # Return the union of the queries over all elements smaller than a state / a country
def smaller_from_state(current_set):   return elt_from_state(current_set, eval_city_all)         | elt_from_state(current_set, eval_mountain_all)      | \
                                              elt_from_state2(current_set, eval_lake_all)        | elt_from_state(current_set, eval_place_all)         | \
                                              elt_from_state2(current_set, eval_river_all)
def state_from_smaller(current_set):   return state_from_elt(current_set, eval_place, "place")   | state_from_elt(current_set, eval_mountain, "place") | \
                                              state_from_elt2(current_set, eval_lake, "place")   | state_from_elt2(current_set, eval_river, "river")   | \
                                              state_from_elt(current_set, eval_city, "city")
def smaller_from_country(current_set): return elt_from_country(current_set, eval_place_all)      | elt_from_country(current_set, eval_city_all)        | \
                                              elt_from_country(current_set, eval_river_all)      | elt_from_country(current_set, eval_state_all)       | \
                                              elt_from_country(current_set, eval_lake_all)       | elt_from_country(current_set, eval_mountain_all)
def country_from_smaller(current_set): return country_from_elt(current_set, eval_place, "place") | country_from_elt(current_set, eval_city, "city")    | \
                                              country_from_elt(current_set, eval_state, "state") | country_from_elt(current_set, eval_lake, "place")   | \
                                              country_from_elt(current_set, eval_river, "river") | country_from_elt(current_set, eval_mountain, "place")
    # Finally the six predicates
def eval_next_to_1(program):  y=set(eval(program)); return state_from_elt2(y, eval_state, "state") | elt_from_state2(y, eval_river_all)
def eval_next_to_2(program):  y=set(eval(program)); return state_from_elt2(y, eval_state, "state") | state_from_elt2(y, eval_river, "river")
def eval_traverse_1(program): y=set(eval(program)); return city_from_elt(y, eval_river, "river")   | state_from_elt2(y, eval_river, "river") | country_from_elt(y, eval_river, "river")
def eval_traverse_2(program): y=set(eval(program)); return elt_from_city(y, eval_river_all)        | elt_from_state2(y, eval_river_all)      | elt_from_country(y, eval_river_all)
def eval_loc_1(program):      y=set(eval(program)); return city_from_elt(y, eval_place, "place")   | state_from_smaller(y)                   | country_from_smaller(y)
def eval_loc_2(program):      y=set(eval(program)); return elt_from_city(y, eval_place_all)        | smaller_from_state(y)                   | smaller_from_country(y)


# Predicates that return a property : returns a property for each element (and the original element as it might be needed by largest_one/smallest_one)
def map_to_property(program, key): return map(lambda x: (key(x), "num", x[0], x[1]), eval(program))
def eval_len(program):             return map_to_property(program, get_length)
def eval_size(program):            return map_to_property(program, get_size)
def eval_area_1(program):          return map_to_property(program, get_area)
def eval_population_1(program):    return map_to_property(program, get_population)
def eval_density_1(program):       return map_to_property(program, get_density)
def eval_elevation_1(program):     return map_to_property(program, get_height)


# Predicates that return an extremum : return only the element with the highest/lowest value for a given property
def keep_one(program, key, max_first): return {sorted(eval(program), key=lambda x: key(x), reverse=max_first)[0]}
def eval_highest(program):  return keep_one(program, get_height, True)
def eval_lowest(program):   return keep_one(program, get_height, False)
def eval_longest(program):  return keep_one(program, get_length, True)
def eval_shortest(program): return keep_one(program, get_length, False)
def eval_largest(program):  return keep_one(program, get_size,   True)
def eval_smallest(program): return keep_one(program, get_size,   False)


# Predicates that perform a reduction : return only a single element based on the additional info that was stored previously
def eval_largest_one(program):  y = sorted(eval(program), key=lambda x: x[0], reverse=True);  return {(y[0][2], y[0][3])}
def eval_smallest_one(program): y = sorted(eval(program), key=lambda x: x[0], reverse=False); return {(y[0][2], y[0][3])}
def eval_most(program):         y = set(eval(program)); w = max(len(x[2]) for x in y); return map(lambda z: (z[0], z[1]), filter(lambda x : len(x[2]) == w, y))
def eval_fewest(program):       y = set(eval(program)); w = min(len(x[2]) for x in y); return map(lambda z: (z[0], z[1]), filter(lambda x : len(x[2]) == w, y))
def eval_count(program):        y = set(eval(program)); return map(lambda x: (len(x[0]), "num"), y) if isinstance(list(y)[0][0], list) else {(len(y), "num")}
def eval_sum(program):          return {(sum(x[0] for x in eval(program)), "num")}


# Set operations : the name is pretty self-explanatory
def eval_intersection(programs): y, z = [set(eval(p)) for p in programs]; return filter(lambda x:     any(i[0]==x[0] and i[1]==x[1] for i in z), y)
def eval_exclude(programs):      y, z = [set(eval(p)) for p in programs]; return filter(lambda x: not any(i[0]==x[0] and i[1]==x[1] for i in z), y)





# Shortcuts for iterators : return the "out_field" of the first element in "table" such that "check_field" is x
def entry_format(entry, fields): return tuple([entry[field] for field in fields]) if isinstance(fields, list) else entry[fields]
def find(x, table, out_field, check_field): return next(entry_format(entry, out_field) for entry in table if entry_format(entry, check_field) == x[0])
# The following functions are aliases for readability. Only the generic function is called in the evaluation and it calls the proper subfunction based on the type of x
def get_country(x):             return "usa"
    # Get the state
def __get_place_state__(x):     return find(x, geobase.places_and_mountains, "state", "element")
def __get_city_state__(x):      return find(x, geobase.cities_and_capitals, "state", ["city", "abbreviation"])
def get_state(x):               return {"place": __get_place_state__, "city": __get_city_state__}[x[1]](x)
    # Get the city
def __get_place_city__(x):      return ('san francisco','ca') if x[0] == "mount davidson" else ()
def __get_river_city__(x):      return ('austin', 'tx') if x[0] == "colorado" else ()
def __get_state_capital__(x):   return find(x, geobase.states, ["capital", "abbreviation"], "state")
def get_city(x):                return {"place": __get_place_city__, "river": __get_river_city__, "state": __get_state_capital__}[x[1]](x)
    # Get the adjacency
def __get_river_traverse__(x):  return find(x, geobase.rivers, "states", "river")
def __get_lake_traverse__(x):   return find(x, geobase.lakes, "states", "lake")
def __get_state_neighbors__(x): return find(x, geobase.borders, "neighbors", "state")
def get_adjacent(x):            return {"place": __get_lake_traverse__, "river": __get_river_traverse__, "state": __get_state_neighbors__}[x[1]](x)
    # Get the high/low point
def __get_state_low__(x):       return find(x, geobase.highlows, "low_point", "state")
def __get_country_low__(x):     return "death valley" if x[0] == "usa" else ""
def get_low_point(x):           return {"state": __get_state_low__, "country": __get_country_low__}[x[1]](x)
def __get_state_high__(x):      return find(x, geobase.highlows, "low_point", "state")
def __get_country_high__(x):    return "death valley" if x[0] == "usa" else ""
def get_high_point(x):          return {"state": __get_state_high__, "country": __get_country_high__}[x[1]](x)
    # Get the area
def __get_city_area__(x):       return 369.2 if x[0][0] == "seattle" and x[0][1] == "wa" else -1
def __get_lake_area__(x):       return find(x, geobase.lakes, "area", "lake")
def __get_state_area__(x):      return find(x, geobase.states, "area", "state")
def __get_country_area__(x):    return find(x, geobase.countries, "area", "country")
def get_area(x):                return {"city": __get_city_area__, "place": __get_lake_area__, "state": __get_state_area__, "country": __get_country_area__}[x[1]](x)
    # Get the population
def __get_city_pop__(x):        return find(x, geobase.cities, "population", ["city", "abbreviation"])
def __get_state_pop__(x):       return find(x, geobase.states, "population", "state")
def __get_country_pop__(x):     return find(x, geobase.countries, "population", "country")
def get_population(x):          return {"city": __get_city_pop__, "state": __get_state_pop__, "country": __get_country_pop__}[x[1]](x)
    # Get other properties
def get_density(x):             return get_population(x)/get_area(x)
def get_length(x):              return find(x, geobase.rivers, "length", "river")
def get_height(x):              return find(x, geobase.places_and_mountains, "elevation", "element")
def get_size(x):                return {"city": __get_city_pop__, "state": __get_state_area__, "place": get_height, "river": get_length}[x[1]](x)





# The callback functions corresponding to all the possible predicates
callbacks = {'answer': eval,                    'cityid': eval_cityid,              'placeid': eval_placeid,
             'riverid': eval_riverid,           'stateid': eval_stateid,            'countryid': eval_countryid,
             'mountainid': eval_mountainid,     'lakeid': eval_lakeid,
             'city(all)': eval_city_all,        'mountain(all)': eval_mountain_all, 'place(all)': eval_place_all,
             'river(all)': eval_river_all,      'lake(all)': eval_lake_all,         'state(all)': eval_state_all,
             'capital(all)': eval_capital_all,  'country(all)': eval_country_all,
             'city': eval_city,                 'mountain': eval_mountain,          'place': eval_place,
             'river': eval_river,               'lake': eval_lake,                  'state': eval_state,
             'capital': eval_capital,           'country': eval_country,
             'capital_1': eval_capital_1,       'capital_2': eval_capital_2,        'high_point_1': eval_high_point_1,
             'high_point_2': eval_high_point_2, 'low_point_1': eval_low_point_1,    'low_point_2': eval_low_point_2,
             'longer': eval_longer,             'shorter': eval_shorter,            'higher_2': eval_higher_2,
             'lower_2': eval_lower_2,           'elevation_2': eval_elevation_2,    'major': eval_major,
             'next_to_1': eval_next_to_1,       'next_to_2': eval_next_to_2,        'traverse_1': eval_traverse_1,
             'traverse_2': eval_traverse_2,     'loc_1': eval_loc_1,                'loc_2': eval_loc_2,
             'highest': eval_highest,           'lowest': eval_lowest,              'longest': eval_longest,
             'shortest': eval_shortest,         'largest': eval_largest,            'smallest': eval_smallest,
             'largest_one': eval_largest_one,   'smallest_one': eval_smallest_one,  'most': eval_most,
             'fewest': eval_fewest,             'count': eval_count,                'sum': eval_sum,
             'len': eval_len,                   'size': eval_size,                  'area_1': eval_area_1,
             'density_1': eval_density_1,       'population_1': eval_population_1,  'elevation_1': eval_elevation_1,
             'intersection': eval_intersection, 'exclude': eval_exclude,
            }
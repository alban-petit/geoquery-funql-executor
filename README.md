# wip_geoquery_executor

## How to use

- Write the program in its string representation in evaluator.py and run it or call evaluator.execute() with the program as an argument.  
- parse.parse() transforms it into an AST.  
- geoquery.evaluate() evaluates the tree and returns the list of answers.  

## Issues

We encounter three kind of issues in the GeoQuery executor:  
- Issues where the executor does not handle a case as it should and yields a wrong answer.
- Issues where the database does not contain information that is queried in the database and yields an empty answer.
- Issues where the correct answer is an empty set which can lead to sketchy evaluation.

Note that the examples chosen to illustrate the issues were not made up but are actual queries or subqueries found in the GeoQuery dataset.

### Executor issues

- Lakes are not returned by "loc_1" or "loc_2".  
Example : answer(lake(loc_2(stateid('california')))) --> [ ]  
- "traverse" does not work on a country.  
Example : answer(longest(river(traverse_2(countryid('usa'))))) --> [ ]  
- "population", "area" and "density" do not work on a country.  
Example : answer(population_1(countryid('usa'))) --> [ ]  
- Only one city is returned when using "city(cityid(...))" with "_" as a state abbreviation.  
Example : answer(city(cityid('springfield', _))) --> ['cityid(springfield, il)']  
- "elevation_2" is not handled by the executor.  
Example : answer(place(elevation_2(0))) --> [ ]
- "most" and "fewest" invert keys and values, i.e. if we expect type_a with the most/fewest type_b, it returns the type_b with the most/fewest type_a instead.  
Example : "The river that traverses the most states" yields answer(most(river(traverse_2(state(all))))) --> ['stateid(colorado)']  
- "major" is not defined for all elements, only cities and rivers.
Example : answer(major(lake(all))) --> [ ]
- "next_to_1" and "next_to_2" are not defined for states/rivers.  
Example : answer(state(next_to_2(river(riverid('mississippi'))))) --> [ ]

### Database issues

- Area (and density) are not defined for cities.  
Example : answer(area_1(cityid('seattle', _))) --> [ ]
- Some state capitals do not appear in the city list.  
Example : answer(capital(city(loc_2(largest(state(all)))))) --> [ ]
- Cities do not contain places.  
Example : answer(highest(place(loc_2(cityid('san francisco', _))))) --> [ ]  
- Rivers do not contain the cities they traverse.  
Example : answer(river(traverse_2(cityid('austin', 'tx')))) --> [ ]

### Empty answer issues
- Some states do not have any major city or river.  
Example : answer(major(city(loc_2(stateid('montana'))))) --> [ ]
- Some states do not have any rivers or neighboring states.  
Example : answer(state(next_to_2(stateid('alaska')))) --> [ ]
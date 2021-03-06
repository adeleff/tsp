import pandas as pd
import random
from collections import namedtuple
from .city import City


Output = namedtuple('Output', ['time_left', 'total', 'path'])


def convert_to_dict(df_cities: pd.DataFrame, df_paths: pd.DataFrame) -> dict:
    """
    Converts data frames of cities and paths to a dictionary
    {city: {neighbour : time_to_neighbour}}.

    :param df_cities: pandas.read_csv("cities.csv")
    :param df_paths: pandas.read_csv("paths.csv")
    :return: dictionary {city: {neighbour : time_to_neighbour}}
    """

    dict_paths = {}
    for city in df_cities['name']:
        # get lists of neighbours of the city
        neighbours_keys = list(df_paths[df_paths['city_from'] == city]['city_to']) + \
                          list(df_paths[df_paths['city_to'] == city]['city_from'])
        # get list of times needed to travel to each of them
        neighbours_values = list(df_paths[df_paths['city_from'] == city]['time']) + \
                            list(df_paths[df_paths['city_to'] == city]['time'])
        # then merge them
        dict_paths[city] = {key: value for key, value in zip(neighbours_keys, neighbours_values)}

    return dict_paths


def find_random_path(cities_list: dict, starting_city: City, time_left: int) -> Output:
    """ Generates a list containing: time, total and random path. """

    path = []
    tmp_time = time_left
    total = 0
    curr_city = cities_list[starting_city]

    while tmp_time > 0:
        time_left = tmp_time

        #TODO
        # change this to:
        # for city in cities:
        #   c_copy = cities_list.copy()
        if curr_city not in path:
            # city value is added only once
            total += curr_city.value

        # add city to a path
        path.append(curr_city)

        # select random neighbour
        next_city = random.choice(list(curr_city.neighbours.keys()))

        # subtract the travel time from available time
        tmp_time -= curr_city.neighbours[next_city]

        # set city we travelled to as a current city
        curr_city = cities_list[next_city]

    return Output(time_left, total, path)


def find_best_of_random_paths(cities_dict: dict, working_time: int, n=50) -> Output:
    """
    Returns list [time_left, sum, path] for the best of paths found in random walk.
    :param d: dictionary {name : {neighbour1 : travel_time1, neighbour2 : travel_time2}}
    :param working_time:
    :param n: number of trials for each vertex in random walk
    """

    best_paths = []
    for starting_city in cities_dict.keys():
        lst = []

        # for better performance define
        add = lst.append
        for i in range(n):
            add(find_random_path(cities_dict, starting_city, working_time))

        # sort list [time_left, total, path] by total, descending
        lst.sort(key=lambda x: x[1], reverse=True)
        best_paths.append(lst[0])

    best_paths.sort(key=lambda x: x[1], reverse=True)

    return best_paths[0]


def convert_to_edges_list(paths: list):
    path = [(cf.name, ct.name)
            for cf, ct in zip(paths[:-1], paths[1:])]
    return path


# solver
def solve(cities: pd.DataFrame, edges: pd.DataFrame, info: pd.DataFrame):
    assert isinstance(cities, pd.DataFrame), 'Wrong data format!'
    assert isinstance(edges, pd.DataFrame), 'Wrong data format!'
    assert isinstance(info, pd.DataFrame), 'Wrong data format!'

    # build a dictionary {city : {neighbour1 : travel_time1, neighbour2 : travel_time2}}
    d = convert_to_dict(cities, edges)

    # build a dict {city_name : City object}
    cities_dict = {}

    for k in d.keys():
        # get: name, x, y, quantity
        vec = cities[cities['name'] == k].values[0]
        c = City(k, vec[1], vec[2], vec[3])
        c.set_neighbours(d)
        cities_dict[k] = c

    # get working time from the data frame
    working_time = info['time'].values[0]

    #TODO
    # data validation

    # compute the best path
    solution = find_best_of_random_paths(cities_dict, working_time, 50)

    return solution, convert_to_edges_list(solution.path)

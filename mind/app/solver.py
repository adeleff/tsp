import numpy as np
import pandas as pd
import random
from typing import List, Tuple, NewType


class City:
    """ This class defines how city is represented. """

    #TODO
    """
    - metoda sprawdzająca, czy miasta są sąsiadami (może przeciążenie operatora)
    - poprawić docstringi (: pd.DataFrame)
    - type annotation
    """

    def __init__(self, name: str, x: int, y: int, value: int = 0) -> None:
        """ Initializes attributes. """
        self.name = name
        self.x = x
        self.y = y
        self.value = value
        self.neighbours = {}
        self.visited = False

    def set_coords(self, df_cities: pd.DataFrame) -> None:
        self.x = df_cities.loc[df_cities['name']]

    def set_neighbours(self, d: dict = dict()) -> None:
        self.neighbours = d.get(self.name, {})   # get the dictionary of pairs {neighbour:travel_time}

    def __str__(self) -> str:
        """ Defines how print(object_name) is displayed. """
        return f"City: {self.name}\n" + \
               f"Coord: ({self.x}, {self.y})\n" + \
               f"Value: {self.value}\n" + \
               f"Ngbrs: {self.neighbours}\n"


# Define new types for typing
#TODO
# doesn't work :<
"""
City = NewType('City', City)
CitiesDict = NewType('CitiesDict', dict)
Output = NewType('Output', Tuple[int, int, List[City]])
"""

def convert_to_dict(df_cities: pd.DataFrame, df_paths: pd.DataFrame): # -> CitiesDict:
    """
    Converts data frames of cities and paths to a dictionary {city: {neighbour : time_to_neighbour}}.
    :param df_cities: pandas.read_csv("cities.csv")
    :param df_paths: pandas.read_csv("paths.csv")
    :return: dictionary {city: {neighbour : time_to_neighbour}}
    """

    #TODO
    # pokminić z listami, czy nie da się tego prościej

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


def find_random_path(cities_list: dict, starting_city: City, time_left: int): # -> Output:
    """ Generates a list containing: time, total and random path. """

    path = []
    tmp_time = time_left
    total = 0
    curr_city = cities_list[starting_city]

    while tmp_time > 0:
        time_left = tmp_time
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
    #TODO
    # spróbować to zwracać jako tuple return time_left, sum, path
    return time_left, total, path


def find_best_of_random_paths(d: dict, working_time: int, n=50): # -> Output:
    """
    Returns list [time_left, sum, path] for the best of paths found in random walk.
    :param d: dictionary {name : {neighbour1 : travel_time1, neighbour2 : travel_time2}}
    :param working_time:
    :param n: number of trials for each vertex in random walk
    """

    best_paths = []
    for starting_city in list(d.keys()):
        lst = []
        for i in range(n):
            lst.append(find_random_path(d, starting_city, working_time))

        # sort list [time_left, total, path] by total, descending
        lst.sort(key=lambda x: x[1], reverse=True)
        best_paths.append(lst[0])

    best_paths.sort(key=lambda x: x[1], reverse=True)

    return best_paths[0]


# tsp solver
def tsp(cities: pd.DataFrame, edges: pd.DataFrame, info: pd.DataFrame):
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
    time_left, total, pth = find_best_of_random_paths(cities_dict, working_time)

    print(f'Time left: {time_left}')
    print(f'Earned:    {total}')
    print("Best found path:")

    for item in pth:
        print(item)

# Test

main_path = ""

cities = pd.read_csv(main_path + "cities.csv")
edges = pd.read_csv(main_path + "paths.csv")
work_time = pd.read_csv(main_path + "time.csv")


tsp(cities, edges, work_time)

import numpy as np
import json


# All necessary configuration before running:

# Folder name of gtfs-data.
gtfs_folder = "paris"

# Transit types to include in the map. (values are based on gtfs-data-format)
transit_types = [1]
# Paris tunnelbana: [1]
# SL spårtrafik: [401, 900, 100]

#Preferred station name should come first in every list.
manually_connected_stations = [["T-Centralen", "Stockholm City", "Stockholms central"], 
                               ["Odenplan", "Stockholm Odenplan"],
                               ["Sundbyberg", "Sundbybergs centrum", "Sundbybergs torg", "Sundbyberg station"],
                               ["Spånga station", "Spånga", "Spånga centrum"],
                               ["Solna", "Solna station"], # Solna Centrum är inte samma sak som Solna station/Solna
                               ["Tekniska högskolan", "Stockholms östra", "Östra station"]
                               ]

# Controls how many trips of a specific route to be checked. Higher values lead to more accurate results.
iteration_value = 10 # 50 is quite high and takes a while. Paris metro with value 10 took multiple hours.

# Filepaths

# Matrix output file:
output_path = f"../generated_matrices/{gtfs_folder}_matrix.json"

stops_file = f"../../{gtfs_folder}/stops.txt"
stop_times_file = f"../../{gtfs_folder}/stop_times.txt"
#transfers_file = f"../../{gtfs_folder}/transfers.txt"
routes_file = f"../../{gtfs_folder}/routes.txt"
trips_file = f"../../{gtfs_folder}/trips.txt"

# End of configuration



# Required functions:

# Assumes that a gtfs file includes specifications for what order the data comes in on each line.
# Returns a dictionary with the indexes of every value (stop_id, headsign etc.).
def indexes_of(input):
    line_ending_index = 5 # Starts at 5 to accomodate new lines at beginning of file.
    while True:
        if (input[line_ending_index] == "\n"):
            break
        line_ending_index += 1

    line = input[0 : line_ending_index].strip().split(',')

    indexes = {}
    for index, key in enumerate(line):
        indexes[key] = index
    
    return indexes

# Returns a list with all the values on a specific line 
# + the index at which the substring was found as last element.
def entry_containing(input, substring, search_start_index = 0):
    index = input.find(substring, search_start_index)

    if (index == -1): return False

    start_index = index
    end_index = index

    while True:
        if (input[start_index] == "\n"):
            break
        start_index -= 1

    while True:
        if (input[end_index] == "\n"):
            break
        end_index += 1

    return (input[start_index: end_index].strip().split(','), index)

# Returns a list of the stop_time entries from a specific trip, inputted as list.
def stop_times_from_trip(input_trip):
    stop_times_list = []

    current_index = 0
    while entry := entry_containing(stop_times_string, input_trip[indexes_of(trips_string)["trip_id"]], current_index):
        stop_times_list.append(entry[0])
        current_index = entry[1] + 1 # Plus one to get to *next* entry containing the string.

    sort_by_stop_sequence(stop_times_list)

    return stop_times_list

# Returns a list of stops (names only) with a list of stop times as input. Removes repeated stops at the same station.
def stops_from_stop_times(stop_times_list):
    stations = []
    for entry in stop_times_list:
        candidate = correct_name(entry_containing(stops_string, entry[indexes_of(stop_times_string)["stop_id"]])[0][indexes_of(stops_string)["stop_name"]])
        if (candidate not in stations): # Sometimes the same station is repeated on a line due to drop off and let in points..
            stations.append(candidate)
    return stations

# Returns correct name for a station based on manual corrections.
def correct_name(station):
    for equivalence in manually_connected_stations:
        if station in equivalence:
            return equivalence[0]
    return station

# Sorts a list of stops by stop_sequence. Used to accomodate stop times out of order in file.
def sort_by_stop_sequence(list_of_stop_times):
    list_of_stop_times.sort(key=lambda stop: int(stop[indexes_of(stop_times_string)["stop_sequence"]]))

# Returns a list of lists of trips on a specific route (station names only).
def trips_on_route(route_id, iterations): # Antalet iterationer kan behöva bli väldigt stort om det körs väldigt många trips på linjen.
    lines = [] # Resulting 2D-list

    index = 0
    for i in range(iterations): # Ju högre värde, desto större chans att alla möjliga trips hittas. Hade kunnat gå igenom alla i hela filen men inte nödvändigt 99% av tiden.
        
        while trip_to_extrapolate := entry_containing(trips_string, route_id, index):
            index = trip_to_extrapolate[1] + 1

            if (trip_to_extrapolate[0][indexes_of(trips_string)["direction_id"]] != '1'): # Only save trips in specified direction, doesnt really matter but reduces redundant trips.
                continue
        
            stop_times_list = stop_times_from_trip(trip_to_extrapolate[0])
            temp_stations = stops_from_stop_times(stop_times_list)
        
            if (temp_stations not in lines):
                lines.append(temp_stations[:])

    return lines

# Generates a matrix based on a list of lists of lines.
def matrix_from_lines(lines):
    stop_list = []

    for line in lines:
        for stop in line:
            if stop not in stop_list:
                stop_list.append(stop)

    dim = len(stop_list)
    matrix = np.zeros((dim, dim), dtype=int)

    for line in lines:
        for i in range(len(line) - 1):
            matrix[stop_list.index(line[i]), stop_list.index(line[i + 1])] = 1
            matrix[stop_list.index(line[i + 1]), stop_list.index(line[i])] = 1

    return {"stop_list": stop_list, "matrix": matrix}

# Returns a list of lists of trips on a multiple routes (station names only).
def trips_on_routes(routes_to_extrapolate, iterations):
    lines = []
    num_of_routes = len(routes_to_extrapolate)
    print(f"Number of routes to calculate: {num_of_routes}.")
    for i, route in enumerate(routes_to_extrapolate):
        lines += trips_on_route(route, iterations)
        print(f"Generated line number {i + 1}, route_id: {route}.")
    return lines

# Used to verify that the correct connections have been made.
def verification_ask(path = output_path):
    with open(path, 'r') as file:
        stop_list, list_array = json.load(file)
    matrix = np.array(list_array)
    
    print("To verify if the matrix is correct, input stations that you want to check if they are connected or not.")
    stop_1 = input("Station 1: ")
    stop_2 = input("Station 2: ")
    print("Connection (1) or no connection (0)")
    print(matrix[stop_list.index(stop_1), stop_list.index(stop_2)])

# Returns all routes of the types specified in 'transit_types'.
def routes_of_type():
    result = []
    index = indexes_of(routes_string)
    for route_type in transit_types:
        current_index = 0
        while entry := entry_containing(routes_string, f",{route_type},", current_index):
            if (int(entry[0][index["route_type"]]) == route_type):
                result.append(entry[0][index["route_id"]])
            current_index = entry[1] + 1 # Plus one to get to *next* entry containing the string.
    return result

# Deletes every list that is a subset of another list in a huge list.
def delete_contained_lists(lists_input):
    result = []
    for contained in lists_input:
        for container in lists_input:
            if set(contained).issubset(set(container)) and contained != container:
                result.append(contained)
    
    for to_delete in result:
        if to_delete in lists_input:
            lists_input.remove(to_delete)



# Sparar datan från alla filer i strings samt index-dictionaries, borde vara lugnt med ram...
with open(routes_file, "r", encoding="utf-8") as handle:
    routes_string = "\n" + handle.read() + "\n"

with open(stops_file, "r", encoding="utf-8") as handle:
    stops_string = "\n" + handle.read() + "\n"

with open(trips_file, "r", encoding="utf-8") as handle:
    trips_string = "\n" + handle.read() + "\n"

#with open(transfers_file, "r", encoding="utf-8") as handle:
#    transfers_string = "\n" + handle.read() + "\n"

with open(stop_times_file, "r", encoding="utf-8") as handle:
    stop_times_string = "\n" + handle.read() + "\n"



# Running the code: 

lines = trips_on_routes(routes_of_type(), iteration_value)

print()
print("Lines generated. Deleting contained lines.")
print()

# This removes some of the trips that skip stations and create connections invisible on a tube map. But not all of them.
delete_contained_lists(lines)

print("Beginning matrix creation.")
print()

result = matrix_from_lines(lines)

print("Matrix done.")

print(lines)

data = (result["stop_list"], result["matrix"].tolist())
with open(output_path, 'w', encoding="utf-8") as file:
    json.dump(data, file)

print()
print("New file generated.")
print()


# Används för att kontrollera att stationer är kopplade korrekt.
while True:
    verification_ask()
    if input() == "stop":
        break

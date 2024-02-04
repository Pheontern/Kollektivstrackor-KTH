import numpy as np
import json

# data read example:
"""
with open('!!!yourfilenamehere!!!', 'r') as file:
    ref, list_array = json.load(file)
array = np.array(list_array)
"""

# Enter save file name and transport lines below:
save_file_name = 'TestMatrix.json'

lines = [['Liljeholmen', 'Hornstull', 'Zinkensdam'],
         ['Gröndal', 'Liljeholmen', 'Årstadal'],
         ['Årstadal', 'Zinkensdam']]

# The rest of the program stays the same
ref = []

for line in lines:
    for station in line:
        if station not in ref:
            ref.append(station)

dim = len(ref)

print(ref)

array = np.zeros((dim, dim), dtype=int)

for line in lines:
    for station_num in range(len(line) - 1):
        array[ref.index(line[station_num]), ref.index(line[station_num + 1])] = 1
        array[ref.index(line[station_num + 1]), ref.index(line[station_num])] = 1

print(array)

data = (ref, array.tolist())
with open(save_file_name, 'w') as file:
    json.dump(data, file)

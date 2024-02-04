import numpy as np


class Connections:
    def __init__(self, matrix, name_list):
        self.name_list = name_list
        self.direct_matrix = matrix
        self.con_matrix = None
        self.cent_list = None
        self.Interconnectivity = 0
        self.size = len(matrix)
        self.set_len_con_matrix_list = None
    
    def calculate_connections(self):
        i = 0
        connection_matrix = np.zeros((self.size,self.size), int)
        working_matrix = self.direct_matrix.copy()
        #print(connection_matrix, "\n", working_matrix)
        not_done = True
        working_matrix_list =[np.identity(self.size)]
        while not_done:
            i += 1
            not_done = False
            for y in range(self.size):
                for x in range(self.size):
                    if (connection_matrix[y, x] == 0) and not (working_matrix[y, x] == 0):
                        connection_matrix[y, x] = i
                    elif connection_matrix[y, x] == 0:
                        not_done = True
            working_matrix_list.append(working_matrix)
            working_matrix = np.matmul(working_matrix, self.direct_matrix)
        self.set_len_con_matrix_list = working_matrix_list
        self.con_matrix = connection_matrix

    def calculate_centrality(self):
        cent_list = []
        for i in range(self.size):
            cent_list.append((self.con_matrix.sum(axis=1)[i] - self.con_matrix[i, i])/(self.size - 1))
        self.cent_list = cent_list

    def calculate_interconnectivity(self):
        self.Interconnectivity = sum(self.cent_list)/self.size


if __name__ == '__main__':
    M = Connections(np.matrix([[0,1,1,0,0,0,0],
                               [1,0,1,0,0,0,0],
                               [1,1,0,1,0,0,0],
                               [0,0,1,0,1,1,0],
                               [0,0,0,1,0,0,0],
                               [0,0,0,1,0,0,1],
                               [0,0,0,0,0,1,0]]),
                              ['a','b','c','d','e','f','g'])

    M.calculate_connections()
    M.calculate_centrality()
    M.calculate_interconnectivity()
    print(M.con_matrix)
    print(M.cent_list)
    print(M.Interconnectivity)
    
            



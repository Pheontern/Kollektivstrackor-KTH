import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json
import tkinter as tk
from tkinter import filedialog
from calc_con_len import Connections


class MainWindow:
    def __init__(self):
        self.matrix = np.array([[0, 1], [1, 0]])
        self.name_list = ['1', '2']

        self.connections = Connections(self.matrix, self.name_list)

        self.root = tk.Tk()
        self.root.title('Graphtheory project')
        self.root.wm_minsize(300, 100)

        choices = sorted(self.name_list)

        self.main_frame = tk.Frame(self.root)

        self.distance_display = tk.Message(self.main_frame, width=150)

        self.centrality_display1 = tk.Message(self.main_frame, width=150)
        self.centrality_display2 = tk.Message(self.main_frame, width=150)
        self.interconnectivity_display = tk.Message(self.main_frame, width=150)

        self.centrality_ranking_display = tk.Text(width=75, height=8, state='disabled')

        self.place1_label = tk.Label(self.main_frame, text="Start station:")
        self.place1 = tk.StringVar(self.root)
        self.place1_picker = tk.OptionMenu(self.main_frame, self.place1, *choices)
        self.place2_label = tk.Label(self.main_frame, text="End station:")
        self.place2 = tk.StringVar(self.root)
        self.place2_picker = tk.OptionMenu(self.main_frame, self.place2, *choices)

        self.graph_button = tk.Button(self.main_frame, text="Look at this graph", command=lambda: show_graph(self.matrix, self.name_list))
        self.update_button = tk.Button(self.main_frame, text="Update results", command=self.update_display)
        self.load_matrix_button = tk.Button(self.main_frame, text="Load matrix", command=self.load_matrix_from_file)

        self.grid_all()

        self.load_matrix_from_file()

        self.root.mainloop()

    def grid_all(self):
        self.main_frame.grid()

        self.place1_label.grid(row=2, column=0)
        self.place2_label.grid(row=3, column=0)

        self.place1_picker.grid(row=2, column=1)
        self.place2_picker.grid(row=3, column=1)

        self.graph_button.grid(row=4, column=1)
        self.update_button.grid(row=1, column=1)
        self.load_matrix_button.grid(row=5, column=1)

        self.distance_display.grid(row=1, column=2)

        self.centrality_display1.grid(row=2, column=2)
        self.centrality_display2.grid(row=3, column=2)
        self.interconnectivity_display.grid(row=4, column=2)

        self.centrality_ranking_display.grid(row=0, column=3, rowspan=3)

    def update_display(self):
        self.connections.calculate_connections()
        self.connections.calculate_centrality()
        self.connections.calculate_interconnectivity()

        self.interconnectivity_display['text'] = "Interconnectivity:", round(self.connections.Interconnectivity, 5)

        if not (place1 := self.place1.get()) == '':
            index1 = self.name_list.index(place1)

            self.centrality_display1['text'] = "Centrality:", round(self.connections.cent_list[index1], 5)

            if not (place2 := self.place2.get()) == '':
                index2 = self.name_list.index(place2)

                self.centrality_display2['text'] = "Centrality:", round(self.connections.cent_list[index2], 5)

                self.distance_display['text'] = "Minimum stops between stations: " + str(self.connections.con_matrix[index1, index2])

        cent = [0]
        for i in range(len(self.connections.cent_list)):
            if len(cent) == 0:
                cent.append(i)
            else:
                for j in range(len(cent)):
                    if self.connections.cent_list[i] <= self.connections.cent_list[cent[j]]:
                        cent.insert(j, i)
                        cent.pop()
                        break
                if i not in cent:
                    cent.append(i)

        self.centrality_ranking_display.configure(state=tk.NORMAL)
        self.centrality_ranking_display.delete('0.0', 'end')
        n = 1
        for h in cent:
            self.centrality_ranking_display.insert(tk.END, f'#{n}: {str(self.name_list[h])} | {round(self.connections.cent_list[h], 5)}\n')
            n += 1
        self.centrality_ranking_display.configure(state=tk.DISABLED)

    def load_matrix_from_file(self):
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title='Select a file', initialdir='./', filetypes=filetypes)

        with open(filename, 'r') as file:
            ref, list_array = json.load(file)
        matrix = np.array(list_array)

        self.matrix = matrix
        self.name_list = ref
        self.connections = Connections(self.matrix, self.name_list)

        choices = sorted(self.name_list)
        self.place1_picker['menu'].delete(0, 'end')
        self.place2_picker['menu'].delete(0, 'end')

        self.place1.set('')
        self.place2.set('')

        for place in choices:
            self.place1_picker['menu'].add_command(label=place, command=lambda x=place: self.place1.set(x))
            self.place2_picker['menu'].add_command(label=place, command=lambda x=place: self.place2.set(x))

        self.update_display()


def show_graph(array, ref):
    translation = {}
    i = 0
    for name in ref:
        translation[i] = name
        i += 1

    fig = plt.figure()

    directed_graph = nx.DiGraph(array)
    directed_graph = nx.relabel_nodes(directed_graph, translation)

    layout = nx.kamada_kawai_layout(directed_graph, scale=1)

    nx.draw(directed_graph, layout, with_labels=True, node_size=50, node_color='pink', edge_color='orchid', font_size='8', font_color='black')

    fig.set_facecolor('white')

    plt.show()


window = MainWindow()

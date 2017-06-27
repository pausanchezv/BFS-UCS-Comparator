#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx
import random
import heapq
import sys

__author__ = "Pau Sanchez Valdivieso"
__email__ = "pausanchez.admifin@gmail.com"

# Detalls de l'experiment

# S'explora a fons el mateix que s'ha dut a terme a l'experiment del BFS. Aqui es demostra que l'UCS que no
# torna a posar els nodes expandits a la frontera és erroni o no retorna camins òptims en alguns els casos.
# Per demostrar que l'UCS de IA és òptim s'ha comparat iterativament amb un algorisme de cerca ingènua o exhaustiva
# per backtracking, demostrant que sempre tornen camins de cost mínim.


class PriorityQueue(object):
    """ Cua de prioritats utilitzant un heap """

    def __init__(self):
        """ PriorityQueue Constructor """
        self.heap = []

    def push(self, item, priority):
        """ Afegeix un ítem al heap """
        entry = priority, item
        heapq.heappush(self.heap, entry)

    def pop(self):
        """ Retorna l'ítem més prioritari """
        _, item = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        """ Comprova si el heap està buit """
        return not self.heap


def get_cost(graph, node, neighbor):
    """ Actualitza i retorna el cost acumulat d'un node en un moment donat """

    cost = graph.node[node]['cost'] + graph[node][neighbor]['weight']

    if cost < graph.node[neighbor]['cost']:
        graph.node[neighbor]['cost'] = cost
        graph.node[neighbor]['parent'] = node

    return cost


def construct_path(graph, goal):
    """ Reconstrueix el camí a partir del node final """

    path, current_node = [goal], goal

    while graph.node[current_node]['parent']:
        current_node = graph.node[current_node]['parent']
        path.insert(0, current_node)

    return path


def reset_graph_info(graph, start):
    """ Reseteja la informació del graf """
    nx.set_node_attributes(graph, 'parent', None)
    nx.set_node_attributes(graph, 'cost', float('inf'))
    graph.node[start]['cost'] = 0


def ucs_IA(graph, start, goal):
    """ UCS que posa els nodes expandits a la frontera """

    reset_graph_info(graph, start)
    queue = PriorityQueue()
    queue.push(start, 0)
    visited = set()

    while not queue.is_empty():
        node = queue.pop()

        if node not in visited:
            if node == goal:
                return construct_path(graph, node)
            visited.add(node)

            for neighbor in graph.neighbors(node):
                cost = get_cost(graph, node, neighbor)
                queue.push(neighbor, cost)
    return []


def ucs(graph, start, goal):
    """ UCS que no posa els nodes expandits a la frontera """

    reset_graph_info(graph, start)
    queue = PriorityQueue()
    queue.push(start, 0)
    visited = {start}

    while not queue.is_empty():
        node = queue.pop()

        for neighbor in graph.neighbors(node):
            cost = get_cost(graph, node, neighbor)

            if neighbor == goal:
                return construct_path(graph, neighbor)

            if neighbor not in visited:
                queue.push(neighbor, cost)
                visited.add(neighbor)
    return []


def plot_graph(graph):
    """ Mostra el graf en una figura """

    # Assignant les coordenades per mostrar el graf en forma de CUB
    graph.node[1]['pos'] = 2.0, 7.0
    graph.node[2]['pos'] = 6.0, 4.6
    graph.node[3]['pos'] = 8.6, 5.8
    graph.node[4]['pos'] = 5.0, 8.0
    graph.node[5]['pos'] = 0.0, 3.0
    graph.node[6]['pos'] = 3.0, 4.0
    graph.node[7]['pos'] = 7.0, 1.4
    graph.node[8]['pos'] = 4.0, 0.0

    fig = plt.figure()
    fig.suptitle("Weighted Graf Cube", fontsize=25)

    pos = nx.get_node_attributes(graph, 'pos')
    nx.draw_networkx(graph, pos)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    plt.show()


def show_graph_info(name, graph):
    """ Mostra per pantalla la forma que ha assolit el graf"""

    print """
        {0}

        Num nodes >> {1}
        Num edges >> {2}
        Node example >> {3}
        Edge example >> {4}
    """.format(name, len(graph.nodes()), len(graph.edges()), graph.nodes(data=True)[random.randint(1, len(graph.nodes()) - 1)],
               graph.edges(data=True)[random.randint(1, len(graph.nodes()) - 1)])


def show_result(path_A, path_B, path_C, cost_A, cost_B, cost_C):
    """ Mostra el resultat de l'experiment per pantalla"""

    print """
        ************************************************************************************************
        Solució UCS
        Path >> {0}
        Cost del camí >> {1}

        Solució UCS de I.A.
        Path >> {2}
        Cost del camí >> {3}

        Confirmació per backtracking
        Path >> {4}
        Cost del camí {5}

        Es demostra que l'UCS de IA és òptim mentre que l'altre pot donar camins erronis o menys òptims.
        El camí òptim per UCS pot diferir del camí òptim per backtracking ja que poden existir diversos
        camins de cost mínim. El que no pot diferir és el cost del camí.
        ************************************************************************************************
    """.format(path_A, cost_A, path_B, cost_B, path_C, cost_C)


def get_path_cost(graph, path):
    """ Retorna el cost d'un camí """
    return sum([graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1)])


def read_graph(filename):
    """ Llegeix el fitxer i crea el graf """
    try:
        return nx.read_edgelist(filename, nodetype=int, data=(('weight', int),))
    except IOError:
        sys.exit("El fitxer {} no existeix".format(filename))


# Mètode de cerca exhaustiva per backtracking per buscar el camí òptim i comparar amb l'UCS per acabar
# demostrant que l'UCS de IA és òptim i l'altre no ho és. Aquest mètode no es pot equivocar mai ja que explora
# per absolutament tot l'espai d'estats. *No utilitzar en grafs de mida mitjana-gran perquè és altament costós
# i no acabaria mai.

def backtracking_shortest_path(graph, start, goal, path=list()):
    """ Camí més curt. Versió ingènua que explora tot l'espai d'estats  """

    path = path + [start]

    if start == goal:
        return path

    shortest = None
    for node in graph.neighbors(start):
        if node not in path:
            newpath = backtracking_shortest_path(graph, node, goal, path)

            if newpath:
                if not shortest or get_path_cost(graph, newpath) < get_path_cost(graph, shortest):
                    shortest = newpath
    return shortest


def main():
    """ Mètode principal """

    graph = read_graph('graph.dat')

    # Nodes de sortida i arribada de l'exemple
    start = 1
    goal = 2

    # Inicialitzant i mostrant el graf
    reset_graph_info(graph, start)
    show_graph_info("Graph from file", graph)

    # Es mostra un exemple camí executant els dos UCS i la cerca exhaustiva
    path_ucs = ucs(graph, start, goal)
    path_ucs_IA = ucs_IA(graph, start, goal)
    path_backtracking = backtracking_shortest_path(graph, start, goal)

    # Cerquem els costos dels dos camins tenint en compte els pesos de les arestes
    cost_ucs = get_path_cost(graph, path_ucs)
    cost_ucs_IA = get_path_cost(graph, path_ucs_IA)
    cost_backtracking= get_path_cost(graph, path_backtracking)

    # Imprimint el resultat
    show_result(path_ucs, path_ucs_IA, path_backtracking, cost_ucs, cost_ucs_IA, cost_backtracking)

    # Generem tots els possibles camins -parelles de nodes (start, goal)-
    # Aqui podem probar tots els casos perquè el graf és petit
    all_possible_paths = list(combinations(range(1, len(graph.nodes()) + 1), 2))

    for start, goal in all_possible_paths:
        """ Comprem cada cada camí UCS amb la mateixa cerca per backtracking """

        ucs_IA_path = ucs_IA(graph, start, goal)
        backtracking_path = backtracking_shortest_path(graph, start, goal)

        # Cal comparar el cost del camí i no el camí ja que poden existir diversos camins amb el mateix cost
        # i els dos són òptims.
        # Si els camins no coincideixen en cost fem petar el programa i l'experiment haurà fallat.
        assert get_path_cost(graph, ucs_IA_path) == get_path_cost(graph, backtracking_path), "Error:: un dels camins no és òptim!"

    plot_graph(graph)


if __name__ == '__main__':
    """ Executant el programa """

    main()

    print """
    Conclusions: En aquest cas no tenia cap sentit comparar iterativament els dos UCS ja que se sap només mostrar
    el primer exemple que un dels dos UCS falla. El que s'ha fet aleshores és demostrar que l'UCS de l'assignatura és òptim
    i per això hem comparat tots els possibles camins entre nodes del graf del fitxer, per UCS i per backtracking.
    Com que el backtracking sense ramificació i poda no pot equivocar-se mai perquè és cerca absoluta s'ha demostrat
    que l'UCS és òptim ja que en tots els possibles casos ambdós han retornat camins de cost mínim.

    En aquest experiment no tenia cap sentit comptar les adhesions que fa cada algorisme a estructures de dades ja
    que un dels dos se sap que no és òptim i per tant no es poden comparar per optimalitat.
    """
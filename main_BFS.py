#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import networkx as nx
import random
import sys

__author__ = "Pau Sanchez Valdivieso"
__email__ = "pausanchez.admifin@gmail.com"

# Detalls de l'experiment

# S'explora a fons el BFS i es fa la comparativa de posar els nodes expandits a la frontera i no posar-los.
# S'han dut a terme dos sub-experiments. El primer sobre un graf aleatori de 1000 nodes i unes 4000 arestes.
# Es repeteix aquest experiment 1000 vegades generant nodes de sortida i arribada aleatoris per demostrar que
# el BFS que no posa els nodes a la frontera és igual de vàlid i és més òptim que l'altre tenint en compte el cost.
# El segon sub-experiment treballa sobre un graf que es llegeix de fitxer i es veu en una figura per saber què
# és realment el que està passant.


def get_random_graph(num_nodes):
    """ Genera un graph connex aleatori de n nodes """

    graph = nx.Graph()
    graph.add_nodes_from(range(1, num_nodes + 1), parent=None)

    while not nx.is_connected(graph):

        node_1 = random.randint(1, num_nodes)
        node_2 = random.randint(1, num_nodes)

        if node_1 != node_2:
            graph.add_edge(node_1, node_2)

    return graph


def get_start_and_goal(num_nodes):
    """ Genera aleatòriament els nodes de sortida i arribada """

    start = random.randint(1, num_nodes)
    goal = random.randint(1, num_nodes)

    while start == goal:
        start = random.randint(1, num_nodes)
        goal = random.randint(1, num_nodes)

    return start, goal


def construct_path(graph, goal):
    """ Reconstrueix el camí a partir del node final """

    path, current_node = [goal], goal

    while graph.node[current_node]['parent']:
        current_node = graph.node[current_node]['parent']
        path.insert(0, current_node)

    return path


def add_node_parent(graph, node, neighbor, visited):
    """ Afegeix, si escau, l'enllaç d'un node amb el seu antecessor """

    if neighbor not in visited and not graph.node[neighbor]['parent']:
        graph.node[neighbor]['parent'] = node


def reset_graph_info(graph):
    """ Posa a None tots els antecessors de tots els nodes per començar una nova exploració """
    nx.set_node_attributes(graph, 'parent', None)
    nx.set_edge_attributes(graph, 'weight', 1)


def bfs_IA(graph, start, goal):
    """
    BFS utilitzat a IA
    Posa tots els nodes a la frontera sempre (expandits i tot)
    """
    reset_graph_info(graph)
    queue, visited = [start], set()
    additions = 1

    while queue:
        node = queue.pop(0)

        if node not in visited:
            if node == goal:
                return construct_path(graph, node), additions
            visited.add(node)

            for neighbor in graph.neighbors(node):
                add_node_parent(graph, node, neighbor, visited)
                queue.append(neighbor)
                additions += 1

    return [], additions


def bfs(graph, start, goal):
    """
    BFS sense nodes expandits a la frontera
    Els nodes expandits no es tornen a posar a la frontera
    """
    reset_graph_info(graph)
    queue, visited = [start], {start}
    additions = 1

    while queue:
        node = queue.pop(0)

        for neighbor in graph.neighbors(node):
            add_node_parent(graph, node, neighbor, visited)

            if neighbor == goal:
                return construct_path(graph, neighbor), additions

            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                additions += 1

    return [], additions


def show_graph_info(name, graph):
    """ Mostra per pantalla la forma que ha assolit el graf"""

    print """
        {0}

        Num nodes >> {1}
        Num edges >> {2}
        Node example >> {3}
        Edge example >> {4}
    """.format(name, len(graph.nodes()), len(graph.edges()), graph.nodes(data=True)[random.randint(1, len(graph.nodes()) - 1)],
               graph.edges()[random.randint(1, len(graph.nodes()) - 1)])


def read_graph(filename):
    """ Llegeix el fitxer i crea el graf """
    try:
        return nx.read_edgelist(filename, nodetype=int, data=(('weight', int),))
    except IOError:
        sys.exit("El fitxer {} no existeix".format(filename))


def show_result(algorithm, path_A, cost_A, path_B, cost_B):
    """ Mostra el resultat de l'experiment per pantalla"""

    print """
        ****************************************************************************
        {0}

        Solució BFS

        Path >> {1}
        Num adhesions (cost) >> {2}

        Solució BFS de I.A.

        Path >> {3}
        Num adhesions (cost) >> {4}

        El -BFS- utilitzat a IA fa {5} adhesions més de nodes a estructures de dades.
        Com que els dos BFS segueixen el mateix ordre d'exploració han de retornar
        camins idèntics.
        *****************************************************************************
    """.format(algorithm, path_A, cost_A, path_B, cost_B, cost_B - cost_A)


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
    fig.suptitle("Graf Cube - cost=1", fontsize=25)

    pos = nx.get_node_attributes(graph, 'pos')
    nx.draw_networkx(graph, pos)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    plt.show()


def main():
    """ Mètode principal"""

    # *** EXPERIMENT 1:: Graf gran aleatori i repetim l'experiment 1000 vegades ***

    print "\n\tCreant i connectant el graf ..."

    # Creació del graf de n nodes on 'n' es pot canviar per a fer proves.
    num_nodes = 1000
    graph = get_random_graph(num_nodes)

    # Mostra la forma del graf (proporció nodes-arestes)
    show_graph_info('Graph Random (N=1000)', graph)

    print "\tCalculant 1000 BFS per cada cas ..."

    # Repetirem l'experiment mil vegades
    EXPERIMENT_REPETITIONS = 1000

    for i in range(EXPERIMENT_REPETITIONS):
        """ Les repeticions es fan sobre el mateix graf canviant els nodes de sortida i arribada """

        # Genera nodes de sortida i arribada
        start, goal = get_start_and_goal(num_nodes)

        # Crides als BFS(s)
        path_bfs, cost_bfs = bfs(graph, start, goal)
        path_bfs_IA, cost_bfs_IA = bfs_IA(graph, start, goal)

        # Els resultats han de ser idèntics, en cas contrari farem petar el programa
        assert path_bfs == path_bfs_IA, "Error:: Resultats de BFS diferents!"

        # Mostrem el resultat de la última execució (per mostrar alguna cosa)
        if i == EXPERIMENT_REPETITIONS - 1:
            show_result("BFS Random", path_bfs, cost_bfs, path_bfs_IA, cost_bfs_IA)

    # *** EXPERIMENT 2:: Graf petit de fitxer 'contra-exemple' ***

    # Llegint el graf des del fitxer
    graph = read_graph('graph.dat')

    start = 2
    goal = 6

    reset_graph_info(graph)
    show_graph_info('Graph from file', graph)

    # Crides als BFS(s)
    path_bfs, cost_bfs = bfs(graph, start, goal)
    path_bfs_IA, cost_bfs_IA = bfs_IA(graph, start, goal)

    # Mostrant resultats i plot
    show_result("BFS Fitxer", path_bfs, cost_bfs, path_bfs_IA, cost_bfs_IA)
    plot_graph(graph)


if __name__ == '__main__':
    """ Executant el programa """

    main()

    print """
    Conclusions: Es demostra que al BFS no és necessari col·locar els nodes visitats a la frontera i que es pot dur a
    terme la cerca estalviant-nos adhesions innecessàries de nodes a l'estructura de dades utilitzada.

    Per contra aquest últim BFS no detecta el cas en què el node de sortida és el mateix que el node d'arribada i per
    això caldria afegir una condició extra a l'inici de l'algorisme.

    """
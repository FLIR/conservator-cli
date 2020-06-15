from networkx import DiGraph
import networkx as nx


def get_nodes_from_graph(graph: DiGraph):
    return [x for x in graph.nodes() if graph.out_degree(x) != 0]


def get_subgraph(graph: DiGraph, searched_synset: str) -> DiGraph:
    descendants: set = nx.descendants(graph, searched_synset)
    descendants.update({searched_synset})
    subgraph = graph.subgraph(descendants)
    return subgraph


def get_depth_for_each_node(graph: DiGraph, root_node: str) -> dict:
    return nx.shortest_path_length(graph, root_node)


def get_nodes_at_the_same_level(depth_to_node: dict, searched_node: str):
    level = depth_to_node[searched_node]
    return [key for key, value in depth_to_node.items() if value == level]


def get_leaves_from_graph(graph: DiGraph):
    return [x for x in graph.nodes() if graph.out_degree(x) == 0]


def _successors_for_node(graph: DiGraph, node: str, list_to_fulfill: list) -> None:
    successors: list = list(graph.successors(node))
    if len(successors) == 0:
        list_to_fulfill.append(node)
    else:
        for successor in successors:
            _successors_for_node(graph, successor, list_to_fulfill)


def get_successors_for_node(graph, searched_synset):
    list_with_items = []
    _successors_for_node(graph, searched_synset, list_with_items)
    return list_with_items

def save_graph_to_file(graph, dst_path):
    nx.write_yaml(graph, dst_path)

def read_graph_from_file(src_path):
    return nx.read_yaml(src_path)

def check_if_node_exists(graph, node_name):
    return node_name in graph.nodes()

def how_many_nodes_to_add(graph, list_of_edges: list):
    return len(list_of_edges) - sum([check_if_node_exists(graph, edge) for edge in list_of_edges])
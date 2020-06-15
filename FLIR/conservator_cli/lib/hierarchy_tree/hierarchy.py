import logging
from pathlib import Path
from pprint import pprint
from typing import Tuple

import networkx as nx
from matplotlib import colors
from networkx import DiGraph

from FLIR.conservator_cli.app.search.search_videos import search_videos
from FLIR.conservator_cli.lib.hierarchy_tree.constants import DATA_PATH, EMAIL, CONSERVATOR_TOKEN
from FLIR.conservator_cli.lib.hierarchy_tree.figures import plot_graph
from FLIR.conservator_cli.lib.hierarchy_tree.graphs import get_nodes_from_graph, get_leaves_from_graph, \
    get_depth_for_each_node, get_successors_for_node, save_graph_to_file, read_graph_from_file, \
    get_nodes_at_the_same_level, how_many_nodes_to_add
from FLIR.conservator_cli.lib.hierarchy_tree.utils import get_lines_from_file, save_to_json_file, read_json_file
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_hypernym_paths, get_name, \
    get_entities_containing_search_class, get_synsets, is_last_word_same_as_the_key, contains_physical_object, \
    get_definition

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)

flir_keys_to_wn_words = {}


def form_dictionary_tree(list_of_hypernyms: list):
    tree = {
        'id': 'entity.n.01',
        'children': list()
    }
    for item in list_of_hypernyms:
        curr_item = tree
        for key in item:
            if type(curr_item) is dict:
                if key == curr_item['id']:
                    curr_item = curr_item['children']
            elif type(curr_item) is list:
                list_with_key = list(filter(lambda x: x['id'] == key, curr_item))

                if len(list_with_key) == 0:
                    curr_item.append({
                        'id': key,
                        'children': list()
                    })
                    curr_item = curr_item[-1]['children']
                else:
                    item_found = list_with_key[0]
                    index = curr_item.index(item_found)
                    curr_item = curr_item[index]['children']
    return tree


def get_unique_classes_from_files(files: list):
    unique_words = []
    for path in files:
        lines_from_path = get_lines_from_file(path)
        unique_words.extend(lines_from_path)
    return set(unique_words)


def build_graph(files) -> Tuple[DiGraph, dict]:
    unique_words = get_unique_classes_from_files(files)
    # hypernyms_to_class = {}
    graph = DiGraph()
    graph.add_node('entity.n.01')

    # word_synsets = [get_synsets(word) for word in unique_words]
    # hypernym_paths = [[s.hypernym_paths() for s in l] for l in word_synsets]
    synsets_hypernyms = {}
    wn_word_to_key = {}

    for word in unique_words:
        word_synsets = get_synsets(word)
        hypernym_paths = [s.hypernym_paths() for s in word_synsets]
        filtered_hypernym_paths = []
        for p in hypernym_paths:
            paths = list(filter(lambda x: contains_physical_object(x), p))
            # paths = list(filter(lambda x: is_last_word_same_as_the_key(word, x), p))
            if paths:
                filtered_hypernym_paths.append(paths)
        synsets_hypernyms[word] = filtered_hypernym_paths

    unknown_words = [key for key, value in synsets_hypernyms.items() if len(value) == 0]
    synsets_hypernyms = {
        key: value for key, value in synsets_hypernyms.items() if len(value) != 0
    }

    synsets_hypernyms = {
        key: value[0] for key, value in synsets_hypernyms.items()  # todo chooses always the first option available
    }

    single_path_hypernyms = {
        key: value for key, value in synsets_hypernyms.items() if len(value) == 1  # words with only single path to root
    }

    multi_path_hypernyms = {
        key: value for key, value in synsets_hypernyms.items() if len(value) > 1  # words with multi path to root
    }

    for key, group in single_path_hypernyms.items():
        edges_to_iter = dict()
        nodes_to_iter = dict()
        for i, synsets in enumerate(group):
            synset_names = [s.name() for s in synsets]
            nodes_to_iter[i] = synset_names
            list_of_pairs = list(zip(synset_names[0:-1], synset_names[1:]))
            edges_to_iter[i] = list_of_pairs
        # select key with min number of nodes to add
        key_to_take = min(edges_to_iter.keys(), key=lambda x: len(edges_to_iter[x]))
        graph.add_edges_from(edges_to_iter[key_to_take])
        wn_word_to_key[key] = nodes_to_iter[key_to_take][-1]

    for key, group in multi_path_hypernyms.items():
        edges_to_iter = dict()
        nodes_to_iter = dict()
        for i, synsets in enumerate(group):
            synset_names = [s.name() for s in synsets]
            nodes_to_iter[i] = synset_names
            list_of_pairs = list(zip(synset_names[0:-1], synset_names[1:]))
            edges_to_iter[i] = list_of_pairs
        # select key with min number of nodes to add
        key_to_take = min(edges_to_iter.keys(), key=lambda x: how_many_nodes_to_add(graph, nodes_to_iter[x]))
        graph.add_edges_from(edges_to_iter[key_to_take])
        wn_word_to_key[key] = nodes_to_iter[key_to_take][-1]

    plot_graph(graph, Path(DATA_PATH) / 'CHUJOWY.png')

    # for word in unique_words:
    #     hypernym_paths = get_hypernym_paths(word)
    #     if len(hypernym_paths) != 0:
    #         chosen_path = hypernym_paths[0]
    #         hypernyms_to_class[chosen_path[-1].name()] = [p.name() for p in
    #                                                       chosen_path]  # get the first hypernym path which exists in the list
    #     else:
    #         hypernyms_to_class[word] = []

    lg.info(f'len of all unique words accross all files: {len(unique_words)}')

    # unknown_words = [key for key in hypernyms_to_class.keys() if len(hypernyms_to_class[key]) == 0]
    lg.info(f'len of unknown accross all files: {len(unknown_words)}')
    lg.info(f'unknown words: {unknown_words}')

    # tree = form_dictionary_tree(hypernyms_to_class.values())
    # graph: DiGraph = nx.readwrite.json_graph.tree_graph(tree)

    nodes = get_nodes_from_graph(graph)
    nodes_acting_as_leaves = list(set(nodes).intersection([wn_word_to_key[k] for k in synsets_hypernyms.keys()]))
    auxillary_nodes = list(set(nodes).difference(nodes_acting_as_leaves))
    leaves = get_leaves_from_graph(graph)
    graph_info: dict = {
        'classes_in_leaves': leaves,
        'classes_in_nodes': nodes_acting_as_leaves,
        'auxillary_nodes': auxillary_nodes,
        'words_not_in_wordnet': unknown_words
    }
    return graph, graph_info


def main():
    yolo_file_path = Path(DATA_PATH) / 'yolo_9000_class_names.txt'
    coco_file_path = Path(DATA_PATH) / 'coco_names.txt'
    flir_names_file_path = Path(DATA_PATH) / 'flir_names.txt'
    flir_tags_file_path = Path(DATA_PATH) / 'flir_tags.txt'

    files = [
        # yolo_file_path,
        coco_file_path,
        flir_names_file_path,
        flir_tags_file_path
    ]

    graph_path = Path(DATA_PATH) / 'graph.yaml'
    graph_info_path = Path(DATA_PATH) / 'graph_info.json'

    graph, graph_info = build_graph(files)
    # save_graph_to_file(graph, graph_path)
    # save_to_json_file(graph_info, graph_info_path)

    # graph = read_graph_from_file(graph_path)
    # graph_info = read_json_file(graph_info_path)

    search_class = 'physical_phenomenon'
    found_targets = get_entities_containing_search_class(search_class, graph.nodes())

    if len(found_targets) == 0:
        raise IndexError(f'there are no found synsets for specific phrase: {search_class}')
    else:
        lg.info(f'found targets: {found_targets}')

    searched_synset = found_targets[0]

    list_with_items = get_successors_for_node(graph, searched_synset)
    for item in list_with_items:
        print(item, get_definition(item))
    names = [get_name(s) for s in list_with_items]
    names = [name.replace('_', ' ') for name in names]

    commands = [f'hasPrediction:"{name}"' for name in names]
    output_command = ' OR\n'.join(commands)

    print(f'output for search class: {search_class}')
    print('=' * 20)
    print(output_command)

    print(f'search command for Conservator : ')
    search_text = f'{" OR ".join(commands)}'
    print(search_text)

    # videos = search_videos(search_text=search_text,
    #                        email=EMAIL,
    #                        conservator_token=CONSERVATOR_TOKEN,
    #                        properties=None)


if __name__ == '__main__':
    main()

import argparse
import logging
from pathlib import Path
from typing import List, Tuple

import pandas
from networkx import DiGraph

from FLIR.conservator_cli.lib.hierarchy_tree.constants import DATA_PATH
from FLIR.conservator_cli.lib.hierarchy_tree.figures import plot_graph
from FLIR.conservator_cli.lib.hierarchy_tree.graphs import get_nodes_from_graph, get_leaves_from_graph, \
    save_graph_to_file, how_many_nodes_to_add
from FLIR.conservator_cli.lib.hierarchy_tree.utils import save_to_json_file, get_unique_classes_from_files
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_synset_by_name, get_synsets

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)


def build_graph(list_of_files: List[str], path_to_annotations_file=None) -> Tuple[DiGraph, dict]:
    graph = DiGraph()
    graph.add_node('entity.n.01')

    synsets_hypernyms = {}
    wn_word_to_key = {}

    unique_words = get_unique_classes_from_files(list_of_files)

    if path_to_annotations_file:
        df = pandas.read_csv(path_to_annotations_file, sep='\t')
        df_true = df[~df.isna().any(axis=1)]
        df_false = df[df.isna().any(axis=1)]
        for i, row in df_true.iterrows():
            word_synsets = [get_synset_by_name(row['wordnet'])]
            hypernym_paths = [s.hypernym_paths() for s in word_synsets]
            synsets_hypernyms[row['words']] = hypernym_paths
        for i, row in df_false.iterrows():
            synsets_hypernyms[row['words']] = []
    else:
        for word in unique_words:
            word_synsets = get_synsets(word)
            hypernym_paths = [s.hypernym_paths() for s in word_synsets]
            synsets_hypernyms[word] = hypernym_paths

    unknown_words = [key for key, value in synsets_hypernyms.items() if len(value) == 0]

    synsets_hypernyms = {
        key: value for key, value in synsets_hypernyms.items() if len(value) != 0
    }

    synsets_hypernyms = {
        key: value[0] for key, value in synsets_hypernyms.items()  # chooses always the first option available
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

    plot_graph(graph, Path(DATA_PATH) / 'graph.png')

    lg.info(f'len of all unique words accross all files: {len(unique_words)}')

    lg.info(f'len of unknown accross all files: {len(unknown_words)}')
    lg.info(f'unknown words: {unknown_words}')

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
    parser = argparse.ArgumentParser(description='Build hierarchy tree.')
    parser.add_argument('list_of_files', metavar='N', type=str, nargs='+',
                        help='list of files containing label names')
    parser.add_argument('-s', '--save_path', type=str, required=True)
    parser.add_argument('-a', '--annotation_file', type=str,
                        help='File containing mappings from labels to wordnet meanings')

    args = parser.parse_args()
    files = args.list_of_files
    annotation_file = args.annotation_file
    save_path = Path(args.save_path)

    graph, graph_info = build_graph(files, annotation_file)

    save_graph_to_file(graph, save_path / 'graph.yaml')
    save_to_json_file(graph_info, save_path / 'graph_info.json')


if __name__ == '__main__':
    main()

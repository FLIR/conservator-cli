import argparse
import logging
from pathlib import Path
from pprint import pprint

from FLIR.conservator_cli.lib.hierarchy_tree.graphs import read_graph_from_file
from FLIR.conservator_cli.lib.hierarchy_tree.utils import get_unique_classes_from_files
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_synsets, get_most_similar_nodes_in_graph

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)


def get_prediction_for_tags():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--path_to_graph', type=str, help='path where graph is saved', required=True)
    parser.add_argument('-t', '--tag_file_path', type=str, help='path to file with tag names', required=True)
    # parser.add_argument('-w', '--word', type=str, required=True)

    args = parser.parse_args()
    path_to_graph = args.path_to_graph
    tag_file_path = args.tag_file_path

    graph_file_path = Path(path_to_graph) / 'graph.yaml'
    graph = read_graph_from_file(graph_file_path)
    unique_tags = get_unique_classes_from_files(
        [
            tag_file_path
        ]
    )

    synsets_for_tags = {
        key: get_synsets(key) for key in unique_tags
    }

    for key, value in synsets_for_tags.items():
        if value:
            lg.info(f'for given key: {key} and its definition: {value[0].definition()}')
            lg.info(f'most similar words are: ')
            pprint(get_most_similar_nodes_in_graph(graph, value[0])[:10])


if __name__ == '__main__':
    get_prediction_for_tags()

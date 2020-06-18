import argparse
import logging
from pathlib import Path

from FLIR.conservator_cli.lib.hierarchy_tree.constants import DATA_PATH
from FLIR.conservator_cli.lib.hierarchy_tree.graphs import get_successors_for_node, read_graph_from_file
from FLIR.conservator_cli.lib.hierarchy_tree.utils import read_json_file
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_name, \
    get_entities_containing_search_class, get_definition

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)


# todo deprecated
def form_dictionary_tree(list_of_hypernyms: list) -> dict:
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


def get_labels_nested_below_word():
    parser = argparse.ArgumentParser(description='get all labels similar to a word based on a graph.')
    parser.add_argument('-p', '--path_to_graph', type=str, help='path where graph is saved', required=True)
    parser.add_argument('-w', '--word', type=str, required=True)

    args = parser.parse_args()
    path_to_graph: str = args.path_to_graph
    provided_word: str = args.word

    yaml_graph_path = Path(path_to_graph) / 'graph.yaml'
    graph_info_path = Path(path_to_graph) / 'graph_info.json'

    graph = read_graph_from_file(yaml_graph_path)
    graph_info = read_json_file(graph_info_path)

    found_targets = get_entities_containing_search_class(provided_word, graph.nodes())

    if len(found_targets) == 0:
        raise IndexError(f'there are no found synsets for specific phrase: {provided_word}')
    else:
        lg.info(f'Found nodes for provided word ({provided_word}): ')
        for i, target in enumerate(found_targets):
            lg.info(f'{i}: {target}')
    lg.info('*' * 40)

    searched_synset = found_targets[0]

    list_with_items = get_successors_for_node(graph, searched_synset)
    lg.info(f'Successors for {searched_synset} :')
    for item in list_with_items:
        lg.info(f'{item}, {get_definition(item)}')
    names = [get_name(s) for s in list_with_items]
    names = [name.replace('_', ' ') for name in names]

    commands = [f'hasPrediction:"{name}"' for name in names]
    lg.info('*' * 40)
    lg.info(f'search command for Conservator : {" OR ".join(commands)}')


if __name__ == '__main__':
    get_labels_nested_below_word()

import logging
from pathlib import Path
from pprint import pprint

from FLIR.conservator_cli.lib.hierarchy_tree.constants import DATA_PATH
from FLIR.conservator_cli.lib.hierarchy_tree.graphs import get_successors_for_node, read_graph_from_file
from FLIR.conservator_cli.lib.hierarchy_tree.utils import read_json_file, \
    get_unique_classes_from_files
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_name, \
    get_entities_containing_search_class, get_synsets, get_definition, get_most_similar_nodes_in_graph

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)


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
    graph_path = Path(DATA_PATH) / 'graph.yaml'
    graph_info_path = Path(DATA_PATH) / 'graph_info.json'

    graph = read_graph_from_file(graph_path)
    graph_info = read_json_file(graph_info_path)

    search_class = 'wheeled_vehicle'
    found_targets = get_entities_containing_search_class(search_class, graph.nodes())

    if len(found_targets) == 0:
        raise IndexError(f'there are no found synsets for specific phrase: {search_class}')
    else:
        for i, target in enumerate(found_targets):
            lg.info(f'{i}: {target}')

    searched_synset = found_targets[0]

    list_with_items = get_successors_for_node(graph, searched_synset)

    for item in list_with_items:
        lg.info(item, get_definition(item))
    names = [get_name(s) for s in list_with_items]
    names = [name.replace('_', ' ') for name in names]

    commands = [f'hasPrediction:"{name}"' for name in names]

    lg.info(f'search command for Conservator : ')
    search_text = f'{" OR ".join(commands)}'
    lg.info(search_text)


if __name__ == '__main__':
    get_labels_nested_below_word()

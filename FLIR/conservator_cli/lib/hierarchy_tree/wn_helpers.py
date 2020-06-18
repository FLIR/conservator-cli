import nltk
import re
from typing import Union

from networkx import DiGraph
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk.corpus.reader import Synset
from nltk.wsd import lesk

nltk.download('wordnet', quiet=True)
nltk.download('wordnet_ic', quiet=True)

brown_ic = wordnet_ic.ic('ic-brown.dat')

def get_name(synset_name: Union[Synset, str]) -> str:
    if type(synset_name) is Synset:
        name = synset_name.name()
    else:
        name = synset_name
    return re.search(r'([\w._\"\'-]+)\.\w\.\d{2}$', name).group(1)


def check_if_noun(synset: Synset) -> bool:
    return synset.pos() == wn.NOUN


def contains_physical_object(hierarchy_of_synsets: list) -> bool:
    return any(['physical_entity' in get_name(i) for i in hierarchy_of_synsets])


def is_last_word_same_as_the_key(key: str, hierarchy: list) -> bool:
    return key == get_name(hierarchy[-1])


def get_synsets(word: str) -> list:
    return wn.synsets(word, pos=wn.NOUN)


def get_hypernym_paths(word: str) -> list:
    synsets = wn.synsets(word, pos=wn.NOUN)
    # TODO how to choose a proper synset / hypernym path
    hypernym_paths = [s.hypernym_paths() for s in synsets]
    filtered_hypernym_paths = list(filter(lambda x: is_last_word_same_as_the_key(word, x), hypernym_paths))
    if filtered_hypernym_paths:
        return filtered_hypernym_paths
    else:
        return hypernym_paths


def _get_entity_if_search_class_matched(search_class: str, item: str):
    match = re.match(re.escape(search_class) + r'\.\w\.\d{2}$', item)
    return match.group() if match else None


def get_entities_containing_search_class(search_class: str, list_of_entities: list) -> list:
    list_of_matches = [_get_entity_if_search_class_matched(search_class, x) for x in list_of_entities]
    return list(filter(lambda match: match is not None, list_of_matches))


def get_definition(entity_name: str) -> str:
    return wn.synset(entity_name).definition()

def get_synset_by_name(name: str):
    return wn.synset(name)


def get_most_similar_nodes_in_graph(graph: DiGraph, name: Synset) -> list:
    similarities = {}
    for node in graph.nodes():
        similarities[node] = wn.lin_similarity(name, wn.synset(node), ic=brown_ic)
        # similarities[node] = wn.wup_similarity(name, wn.synset(node))
    return sorted(similarities.items(), key=lambda x: x[1], reverse=True)

def get_best_synset(word: str, context_sentence: str) -> Synset:
    return lesk(context_sentence.split(), word, pos=wn.NOUN, synsets=wn.synsets(word))

def get_synsets_with_definition(word):
    return {
        s.name(): s.definition() for s in get_synsets(word)
    }


if __name__ == '__main__':
    words = ['computer', 'mouse', 'car']
    for word in words:
        synsets = get_synsets(word)
        print(f'Word we are trying to find a proper meaning: {word}')
        for s in synsets:
            print(f'found word: {s.name()}, definition: {s.definition()}')









    word = 'mouse'
    context_sentence = 'An electronic device used together with computer'

    best_synset = get_best_synset(word, context_sentence)
    print(f'{best_synset.name()}, {best_synset.definition()}')

    print(f'end.')

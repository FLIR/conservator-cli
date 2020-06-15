import nltk
import re
from typing import Union

from nltk.corpus import wordnet as wn
from nltk.corpus.reader import Synset

nltk.download('wordnet')


def get_name(synset_name: Union[Synset, str]):
    if type(synset_name) is Synset:
        name = synset_name.name()
    else:
        name = synset_name
    return re.search(r'([\w._\"\'-]+)\.\w\.\d{2}$', name).group(1)


def check_if_noun(synset):
    return synset.pos() == wn.NOUN


def contains_physical_object(hierarchy):
    return any(['physical_entity' in get_name(i) for i in hierarchy])


def is_last_word_same_as_the_key(key: str, hierarchy: list):
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


def _get_entity_if_search_class_matched(search_class, item):
    match = re.match(re.escape(search_class) + r'\.\w\.\d{2}$', item)
    return match.group() if match else None


def get_entities_containing_search_class(search_class: str, list_of_entities: list) -> list:
    list_of_matches = [_get_entity_if_search_class_matched(search_class, x) for x in list_of_entities]
    return list(filter(lambda match: match is not None, list_of_matches))


def get_definition(entity_name: str):
    return wn.synset(entity_name).definition()

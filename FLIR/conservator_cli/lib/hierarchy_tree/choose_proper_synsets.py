import argparse
from pathlib import Path

import pandas

from FLIR.conservator_cli.lib.hierarchy_tree.constants import DATA_PATH
from FLIR.conservator_cli.lib.hierarchy_tree.hierarchy import get_unique_classes_from_files
from FLIR.conservator_cli.lib.hierarchy_tree.wn_helpers import get_synsets


def choose_option(name_and_def_list: list):
    which_to_choose = input('Which definition you want to choose?\n')
    try:
        which_to_choose = int(which_to_choose)
        assert which_to_choose <= len(name_and_def_list)
        return name_and_def_list[which_to_choose]
    except Exception:
        print(f'Invalid input. Please try again.')
        return choose_option(name_and_def_list)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('list_of_files', metavar='N', type=str, nargs='+',
                        help='list of files containing label names')
    parser.add_argument('-s', '--save_path', type=str, required=True)

    args = parser.parse_args()
    files = args.list_of_files
    save_path = args.save_path

    print(f'files found: {files}')
    print(f'path where to save file: {Path(save_path).absolute().resolve()}')

    unique_words = get_unique_classes_from_files(files)

    data = {
        'words': unique_words,
        'wordnet': [get_synsets(w)[0].name() if len(get_synsets(w)) == 1 else '?' for w in unique_words],
        'definition': [get_synsets(w)[0].definition().strip() if len(get_synsets(w)) == 1 else '?' for w in
                       unique_words]
    }

    df = pandas.DataFrame(data=data)
    df = df.set_index('words')

    multi_definition_synsets = {
        word: get_synsets(word) for word in unique_words if len(get_synsets(word)) > 1
    }

    print(f'number of multi definition synsets: {len(multi_definition_synsets)}')

    for key, item in multi_definition_synsets.items():
        name_and_def_list = [(key, row.name(), row.definition()) for row in item]
        print(f'options for : {key}')
        for i, row in enumerate(item):
            print(i, name_and_def_list[i][2])
        row = choose_option(name_and_def_list)
        df.loc[row[0]] = [row[1], row[2]]
        print(f'chosen row: {row}')
        print('=' * 40)

    df.to_csv(Path(DATA_PATH) / 'wordnet_to_words.csv', sep='\t')


if __name__ == '__main__':
    main()

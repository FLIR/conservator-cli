#!/usr/bin/env python3
import json
import argparse

from FLIR.dataset_toolkit.lib.dataset import Dataset

def count_annotations_main():
    """This script counts the number of human (optional all) annotations in an index file."""
    parser = argparse.ArgumentParser()
    parser.add_argument('index_file', help="Index file from fc-git")
    parser.add_argument('-a', '--all', help="show statistics for all annotations", action='store_true')
    args = parser.parse_args()
    dataset = Dataset.load(args.index_file, include_machine_annotations=args.all)
    print(dataset.get_annotation_count())

if __name__ == "__main__":
    count_annotations_main()

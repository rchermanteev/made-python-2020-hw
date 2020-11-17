"""Library for work with inverted index

Library offers functionality for build, dump, load and query inverted index
Please, for work with inverted index use class "InvertedIndex" and function "build_inverted_index".
For load documents use function "load_documents"
"""
from argparse import ArgumentParser, FileType
from collections import defaultdict
import sys
from typing import List, Dict

from storage_policy import ArrayStoragePolicy, JsonStoragePolicy


class InvertedIndex:
    """class to build, dump, load and query inverted index

    main methods:
    - query(words: List[str]) -> List[str]:
        return the list of relevant documents for the given query

    - dump(filepath: str, storage_policy="array_storage_policy"):
        dump inverted index into hard drive

    - load(filepath: str, storage_policy="array_storage_policy"):
        load inverted index from hard drive (classmethod)
    """
    def __init__(self):
        self.inv_idx_dict = None

    def __eq__(self, other):
        return self.inv_idx_dict == other.inv_idx_dict

    def set_inverted_index_dict(self, inv_idx_dict: Dict[str, List[str]]):
        """Set new inverted index"""
        self.inv_idx_dict = inv_idx_dict

    def query(self, words: List[str]) -> List[str]:
        """Return the list of relevant documents for the given query"""
        if not words:
            return []

        if self.inv_idx_dict.get(words[0]):
            result = set(self.inv_idx_dict[words[0]])
        else:
            return []

        for word in words:
            result.intersection_update(
                self.inv_idx_dict.get(word) if self.inv_idx_dict.get(word) else []
            )

        return list(result)

    def dump(self, filepath: str, storage_policy="array_storage_policy"):
        """Dump inverted index into hard drive

        You can choose a policy to dump:
        - array_storage_policy : saving to a binary file using compression using the library struct.
        - json_storage_policy : saving to a file in format json
        """
        print("start dump inverted index...", file=sys.stderr)
        if storage_policy == "array_storage_policy":
            ArrayStoragePolicy().dump(self.inv_idx_dict, filepath)

        if storage_policy == "json_storage_policy":
            JsonStoragePolicy().dump(self.inv_idx_dict, filepath)

    @classmethod
    def load(cls, filepath: str, storage_policy="array_storage_policy"):
        """Load inverted index from hard drive

        You can choose a policy to load:
        - array_storage_policy : saving to a binary file using compression using the library struct.
        - json_storage_policy : saving to a file in format json
        """
        print("start load inverted index...", file=sys.stderr)
        inv_index = InvertedIndex()

        if storage_policy == "array_storage_policy":
            inv_index.set_inverted_index_dict(ArrayStoragePolicy().load(filepath))

        if storage_policy == "json_storage_policy":
            inv_index.set_inverted_index_dict(JsonStoragePolicy().load(filepath))

        return inv_index


def load_documents(filepath: str) -> List[str]:
    """Load documents from hard drive"""
    print("start load documents...", file=sys.stderr)
    data = []
    with open(filepath, encoding="utf_8") as file:
        line = file.readline()
        while line:
            data.append(line.strip())
            line = file.readline()

    return data


def build_inverted_index(documents: List[str]) -> InvertedIndex:
    """Build inverted index from array of documents"""
    print("start build inverted index...", file=sys.stderr)
    inv_idx_dict = defaultdict(set)

    for document in documents:
        document_id, *data = document.strip("\t").strip().split()
        for word in data:
            word = word.strip()
            document_id = document_id.strip()
            inv_idx_dict[word].add(document_id)

    inv_idx_dict = dict(inv_idx_dict)
    for key in inv_idx_dict.keys():
        inv_idx_dict[key] = list(inv_idx_dict[key])

    inv_idx = InvertedIndex()
    inv_idx.set_inverted_index_dict(inv_idx_dict)

    return inv_idx


def callback_build(arguments):
    """Callback for method build"""
    documents = load_documents(arguments.path_to_dataset)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(arguments.path_to_load)


def callback_query(arguments):
    """Callback for method query"""
    inverted_index = InvertedIndex.load(arguments.path_to_inv_index)
    queries = []
    if arguments.queries:
        queries = arguments.queries
    elif arguments.query_file:
        queries = arguments.query_file

    for query in queries:
        query = query.strip()
        document_ids = inverted_index.query(query)
        print(",".join(document_ids), file=sys.stdout)


def setup_parser(parser):
    subparsers = parser.add_subparsers(help="choose command")

    build_parser = subparsers.add_parser(
        "build",
        help="build inverted index and save into hard drive"
    )
    build_parser.add_argument(
        "-d", "--dataset", required=True, dest="path_to_dataset",
        help="path to dataset to load",
    )
    build_parser.add_argument(
        "-o", "--output", required=True,
        help="path to store inverted index", dest="path_to_load"
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query",
        help="query inverted index"
    )
    query_parser.add_argument(
        "-i", "--index", required=True, dest="path_to_inv_index",
        help="path to inverted index"
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=False)
    query_file_group.add_argument(
        "--query-file-utf8", required=False, dest="query_file",
        type=FileType("r", encoding="utf-8"),
        help="path to query in encoding utf-8"
    )
    query_file_group.add_argument(
        "--query-file-cp1251", required=False, dest="query_file",
        type=FileType("r", encoding="cp1251"),
        help="path to query in encoding cp1251"
    )
    query_parser.add_argument(
        "--query", required=False, nargs="+", dest="queries",
        metavar="WORD",
        help="query to run against inverted index"
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    parser = ArgumentParser(
        prog="inverted-index",
        description="tool to build, dump, load and query inverted index",
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()

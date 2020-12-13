import os
from textwrap import dedent

import pytest

from inverted_index_starter import InvertedIndex, load_documents, build_inverted_index
from storage_policy import ArrayStoragePolicy, JsonStoragePolicy


DATASET_BIG_FPATH = "./test_data/wikipedia_sample.txt"
DATASET_SMALL_FPATH = "./test_data/small_wikipedia_sample.txt"
DATASET_TINY_FPATH = "./test_data/tiny_wikipedia_sample.txt"


def test_can_load_documents_v1():
    documents = load_documents(DATASET_TINY_FPATH)
    etalon_documents = [
        "123     some words with A_word",
        "2       some words with B_word",
        "5       famous_phrases like to be or not to be",
        "3128    words A_word with B_word in one document"
    ]

    assert etalon_documents == documents, (
        "load_documents incorrectly loaded dataset"
    )


def test_can_load_documents_v2(tmpdir):
    dataset_str = dedent("""\
        123     some words with A_word
        2       some words with B_word
        5       famous_phrases like to be or not to be
        3128    words A_word with B_word in one document
    """)
    dataset_fio = tmpdir.join("tiny.dataset")
    dataset_fio.write(dataset_str)
    documents = load_documents(dataset_fio)
    etalon_documents = [
        "123     some words with A_word",
        "2       some words with B_word",
        "5       famous_phrases like to be or not to be",
        "3128    words A_word with B_word in one document"
    ]
    assert etalon_documents == documents, (
        "load_documents incorrectly loaded dataset"
    )


DATASET_TINY_STR = dedent("""\
        123     some words with A_word
        2       some words with B_word
        5       famous_phrases like to be or not to be
        3128    words A_word with B_word in one document
    """)


@pytest.fixture
def tiny_dataset_fio(tmpdir):
    dataset_fio = tmpdir.join("dataset.txt")
    dataset_fio.write(DATASET_TINY_STR)
    return dataset_fio


def test_can_load_documents(tiny_dataset_fio):
    documents = load_documents(tiny_dataset_fio)
    etalon_documents = [
        "123     some words with A_word",
        "2       some words with B_word",
        "5       famous_phrases like to be or not to be",
        "3128    words A_word with B_word in one document"
    ]
    assert etalon_documents == documents, (
        "load_documents incorrectly loaded dataset"
    )


@pytest.mark.parametrize(
    "query, etalon_answer",
    [
        pytest.param(["A_word"], ["123", "3128"], id="A_word"),
        pytest.param(["B_word"], ["2", "3128"], id="B_word"),
        pytest.param(["A_word", "B_word"], ["3128"], id="both words"),
        pytest.param(["word_does_not_exist"], [], id="word does not exist"),
    ]
)
def test_query_inverted_index_intersect_result(tiny_dataset_fio, query, etalon_answer):
    documents = load_documents(tiny_dataset_fio)
    tiny_inverted_index = build_inverted_index(documents)
    answer = tiny_inverted_index.query(query)
    assert sorted(answer) == sorted(etalon_answer), (
        f"Expected answer is {etalon_answer}, but you got {answer}"
    )


def test_can_load_wikipedia_sample():
    documents = load_documents(DATASET_BIG_FPATH)
    assert len(documents) == 4100, (
        "you incorrectly loaded Wikipedia sample"
    )


@pytest.fixture
def wikipedia_documents():
    documents = load_documents(DATASET_BIG_FPATH)
    return documents


@pytest.fixture
def small_sample_wikipedia_documents():
    documents = load_documents(DATASET_SMALL_FPATH)
    return documents


@pytest.fixture
def tiny_sample_wikipedia_documents():
    documents = load_documents(DATASET_TINY_FPATH)
    return documents


def test_can_build_and_query_inverted_index(tiny_sample_wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(tiny_sample_wikipedia_documents)
    doc_ids = wikipedia_inverted_index.query(["wikipedia"])
    assert isinstance(doc_ids, list), "inverted index query should return list"


@pytest.fixture
def wikipedia_inverted_index(wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(wikipedia_documents)
    return wikipedia_inverted_index


@pytest.fixture
def tiny_wikipedia_inverted_index(tiny_sample_wikipedia_documents):
    tiny_wikipedia_inverted_index = build_inverted_index(tiny_sample_wikipedia_documents)
    return tiny_wikipedia_inverted_index


@pytest.fixture
def small_wikipedia_inverted_index(small_sample_wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(small_sample_wikipedia_documents)
    return wikipedia_inverted_index


def test_can_dump_and_load_inverted_index(tmpdir, tiny_wikipedia_inverted_index):
    index_fio = tmpdir.join("index.dump")
    tiny_wikipedia_inverted_index.dump(index_fio)
    loaded_inverted_index = InvertedIndex.load(index_fio)
    assert tiny_wikipedia_inverted_index == loaded_inverted_index, (
        "load should return the same inverted index"
    )


@pytest.mark.parametrize(
    ("filepath",),
    [
        pytest.param(DATASET_SMALL_FPATH, id="small dataset"),
        pytest.param(
            DATASET_BIG_FPATH,
            marks=[pytest.mark.skipif(1 == 0, reason="Takes a long time")],
            id="big dataset"
        )
    ],
)
def test_can_dump_and_load_inverted_index_with_array_policy_parametrized(filepath, tmpdir):
    index_fio = tmpdir.join("index.dump")
    documents = load_documents(filepath)
    etalon_inverted_index = build_inverted_index(documents)
    etalon_inverted_index.dump(index_fio, storage_policy="array_storage_policy")
    loaded_inverted_index = InvertedIndex.load(index_fio, storage_policy="array_storage_policy")
    assert etalon_inverted_index == loaded_inverted_index, (
        "load should return same inverted index"
    )


@pytest.mark.parametrize(
    ("filepath",),
    [
        pytest.param(DATASET_SMALL_FPATH, id="small dataset"),
        pytest.param(
            DATASET_BIG_FPATH,
            marks=[pytest.mark.skipif(1 == 0, reason="Takes a long time")],
            id="big dataset"
        )
    ],
)
def test_can_dump_and_load_inverted_index_with_json_policy_parametrized(filepath, tmpdir):
    index_fio = tmpdir.join("index.dump")
    documents = load_documents(filepath)
    etalon_inverted_index = build_inverted_index(documents)
    etalon_inverted_index.dump(index_fio, storage_policy="json_storage_policy")
    loaded_inverted_index = InvertedIndex.load(index_fio, storage_policy="json_storage_policy")
    assert etalon_inverted_index == loaded_inverted_index, (
        "load should return same inverted index"
    )


def test_can_create_instance_class_inverted_index():
    assert InvertedIndex()


def test_instance_have_necessary_methods():
    assert {'query', 'dump', 'load'}.issubset(InvertedIndex.__dict__.keys())


def test_load_documents():
    test_file_path = "./test_data/test_file.txt"
    data = load_documents(test_file_path)

    assert type(data) == list
    assert len(data) == 151
    assert data[3].strip() == "eg"


def test_build_inverted_index():
    filepath = "./data/wikipedia_sample.txt"
    with open(filepath, encoding="utf-8") as file:
        data = [file.readline() for _ in range(5)]

    inv_ind = build_inverted_index(data)

    assert type(inv_ind) == InvertedIndex
    assert inv_ind.inv_idx_dict['anarchism'] == ["12"]
    assert inv_ind.inv_idx_dict['the'].sort() == ["290", "39", "12", "303", "25"].sort()


def test_inverted_index_dump():
    test_data = {"q": [1, 2], "adsfaf": [1, 2, 4, 5], "w": [9], "test": [666]}
    inv_ind = InvertedIndex()
    inv_ind.inv_idx_dict = test_data
    test_file_path = "test_data/test_dump.json"
    inv_ind.dump(test_file_path, "json_storage_policy")

    assert os.path.exists(test_file_path)
    os.remove(test_file_path)


def test_inverted_index_load():
    test_file_path = "./test_data/test_load.json"
    inv_ind = InvertedIndex.load(test_file_path, "json_storage_policy")

    assert type(inv_ind) == InvertedIndex
    assert inv_ind.inv_idx_dict["q"] == [1, 2]
    assert len(inv_ind.inv_idx_dict) == 4


def test_inverted_index_query():
    test_file_path = "./test_data/test_load.json"
    inv_ind = InvertedIndex.load(test_file_path, "json_storage_policy")

    assert inv_ind.query([]) == []
    assert inv_ind.query(["adsfaf", "q"]).sort() == [2].sort()
    assert inv_ind.query(["adsfaf", "w"]).sort() == [5].sort()
    assert inv_ind.query(["adsfaf", "q", "w"]).sort() == [2, 5].sort()

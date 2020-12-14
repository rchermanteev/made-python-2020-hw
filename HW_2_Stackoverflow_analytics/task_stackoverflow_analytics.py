"""Library for stackoverflow analytics

"""
from argparse import ArgumentParser
from collections import defaultdict
import json
from re import findall
import sys
from typing import List

import logging
import logging.config
import yaml

from lxml import etree

DEFAULT_LOGGING_CONFIG_FILEPATH = "logging.conf.yml"


class StackoverflowAnalytics:
    """Class to stackoverflow analytics

    main methods:
    - query(start_year: int, end_year: int, num_words: int) -> str:
        return the list of top num_words words for interval start_year-end_year
        format return: json-line

    - build_data_to_analysis(posts: List[str], stop_words: List[str]):
        prepare data for further analysis

        prepared data has the following structure:
        {year(int): {word(str): score(int)}}
        example:
        data = {
            2010: {'to': 1, 'selector': 1, 'parameter': 1, 'passing': 1, 'not': 1, 'css': 1},
            2008: {'how': 74, 'i': 74, 'write': 74, 'c': 74, 'do': 74,
            'short': 74, 'in': 74, 'literal': 74}
        }
    """
    def __init__(self):
        self._data = defaultdict(dict)
        logger = logging.getLogger("stackoverflow_analytics")
        self.logger = logger

    @staticmethod
    def _preprocess_date_in_post(date_time: str) -> int:
        """Process data_time to year

        Example:
            input date_time: '2008-10-15T00:44:56.847'
            output: 2008
        """
        return int(date_time.split("-")[0])

    @staticmethod
    def _preprocess_title_in_post(title: str, stop_words) -> List[str]:
        """Process title

        Delete same words, stop_words, deleting characters other than
        lettersand translate in lowercase.
        """

        title_with_stop_words = set(findall(r"\w+", title.lower()))
        clear_title = [word for word in title_with_stop_words if word not in stop_words]

        return clear_title

    @staticmethod
    def _preprocess_score_in_post(score: str) -> int:
        """Process score

        Translate score to int.
        """
        return int(score)

    def build_data_to_analysis(self, posts: List[str], stop_words: List[str]):
        """Prepare data for further analysis

        prepared data has the following structure:
        {year(int): {word(str): score(int)}}
        example:
        data = {
            2010: {'to': 1, 'selector': 1, 'parameter': 1, 'passing': 1, 'not': 1, 'css': 1},
            2008: {'how': 74, 'i': 74, 'write': 74, 'c': 74, 'do': 74,
            'short': 74, 'in': 74, 'literal': 74}
        }
        """
        self.logger.info("start build data to analysis...")
        for post in posts:
            xml_post = etree.fromstring(post)
            if xml_post.attrib["PostTypeId"] == '1':
                year = self._preprocess_date_in_post(xml_post.attrib["CreationDate"])
                score = self._preprocess_score_in_post(xml_post.attrib["Score"])
                words = self._preprocess_title_in_post(xml_post.attrib["Title"], stop_words)
                for word in words:
                    if year in self._data:
                        if word in self._data[year]:
                            self._data[year][word] += score
                        else:
                            self._data[year][word] = score

                    else:
                        self._data[year] = {word: score}

        self.logger.info("finish build data to analysis...")

    @staticmethod
    def _format_top_to_result(data):
        return list(map(list, data))

    def query(self, start_year: int, end_year: int, num_words: int) -> str:
        """Get the list of top num_words words for interval start_year-end_year

        format return: json-line
        """
        self.logger.info("start processing query...")
        self.logger.debug("got query: start_year(%s) end_year(%s) num_words(%s)", start_year, end_year, num_words)

        query_data = self._data[start_year].copy()
        for year in range(start_year + 1, end_year + 1):
            if year in self._data:
                data_from_year = self._data[year].items()
                for word, score in data_from_year:
                    if word in query_data:
                        query_data[word] += score
                    else:
                        query_data[word] = score

        query_data = sorted(
            sorted(query_data.items(), key=lambda x: x[0]),
            key=lambda x: x[1], reverse=True
        )
        if len(query_data) < num_words:
            self.logger.warning(
                "not enough data to answer, found top_K(%s) words out of top_N(%s) for period %s - %s",
                len(query_data),
                num_words,
                start_year,
                end_year
            )
        result = {
            "start": start_year,
            "end": end_year,
            "top": self._format_top_to_result(query_data[:num_words])
        }
        result = json.dumps(result)
        self.logger.info("finish processing query...")

        return result


def load_data(filepath: str, encoding: str = "utf-8") -> List[str]:
    """Load some data in a given format from hard drive"""
    data = []
    with open(filepath, encoding=encoding) as file:
        line = file.readline()
        while line:
            data.append(line.rstrip())
            line = file.readline()

    return data


def load_posts(filepath: str) -> List[str]:
    """Load posts from hard drive"""
    logger = logging.getLogger("stackoverflow_analytics")
    logger.info("start load posts...")
    posts = load_data(filepath, encoding="utf-8")
    logger.info("finish load posts...")
    return posts


def load_stop_words(filepath: str) -> List[str]:
    """Load stop words from hard drive"""
    logger = logging.getLogger("stackoverflow_analytics")
    logger.info("start load stop words...")
    stop_words = load_data(filepath, encoding="koi8-r")
    logger.info("finish load stop words...")
    return stop_words


def load_queries(filepath: str) -> List[List[int]]:
    """Load queries from hard drive"""
    logger = logging.getLogger("stackoverflow_analytics")
    logger.info("start load queries...")
    dirty_queries = load_data(filepath, encoding="utf-8")
    logger.info("finish load queries...")
    logger.info("start process queries...")
    queries = [list(map(int, query.split(','))) for query in dirty_queries]
    logger.info("finish process queries...")
    return queries


def callback_parser(arguments):
    """Base callback for program"""
    stop_words = load_stop_words(arguments.path_to_stop_words_dataset)
    posts = load_posts(arguments.path_to_questions_dataset)
    sof_analytics = StackoverflowAnalytics()
    sof_analytics.build_data_to_analysis(posts, stop_words)
    queries = load_queries(arguments.path_to_query_file)
    for query in queries:
        response = sof_analytics.query(*query)
        print(response, file=sys.stdout)


def setup_parser(parser):
    parser.add_argument(
        "--questions", required=True, dest="path_to_questions_dataset",
        help="path to dataset with questions to load",
    )
    parser.add_argument(
        "--stop-words", required=True, dest="path_to_stop_words_dataset",
        help="path to dataset with stop words to load",
    )
    parser.add_argument(
        "--queries", required=True, dest="path_to_query_file",
        help="path to query in csv"
    )
    parser.set_defaults(callback=callback_parser)


def setup_logging():
    with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as config_fin:
        logging.config.dictConfig(yaml.safe_load(config_fin))


def main():
    parser = ArgumentParser(
        prog="stackoverflow-analytics",
        description="stackoverflow analytics tool",
    )
    setup_parser(parser)
    setup_logging()
    logger = logging.getLogger("stackoverflow_analytics")
    logger.info("run application")
    arguments = parser.parse_args()
    logger.debug("get arguments: %s", repr(arguments))
    arguments.callback(arguments)


if __name__ == "__main__":
    main()

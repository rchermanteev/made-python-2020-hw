import os
from textwrap import dedent
import json

import pytest

from task_stackoverflow_analytics import (
    StackoverflowAnalytics,
    load_data,
    load_stop_words,
    load_posts,
    load_queries,
)


DATA_TINY_FPATH = "./test_data/tiny_test_data.txt"
STOP_WORDS_TINY_FPATH = "./test_data/tiny_stop_words_en.txt"
POSTS_TINY_FPATH = "./test_data/tiny_posts.xml"
QUERIES_TINY_FPATH = "./test_data/tiny_queries.csv"


def test_can_load_data():
    data = load_data(DATA_TINY_FPATH)
    etalon_data = [
        "hello world",
        "many words one two three",
        "two words cat car",
        "three same words tree tree tree"
    ]

    assert etalon_data == data, (
        "load_documents incorrectly loaded dataset"
    )


def test_can_load_stop_words():
    stop_words = load_stop_words(STOP_WORDS_TINY_FPATH)
    etalon_stop_words = [
        'a', 'about', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost'
    ]

    assert etalon_stop_words == stop_words, (
        "load_documents incorrectly loaded dataset"
    )


@pytest.fixture
def tiny_stop_words():
    stop_words = load_stop_words(STOP_WORDS_TINY_FPATH)
    return stop_words


def test_can_load_posts():
    posts = load_posts(POSTS_TINY_FPATH)
    etalon_posts = [
        '<row Id="201905" PostTypeId="2" ParentId="201323" CreationDate="2008-10-14T16:35:44.180" Score="38" Body="&lt;p&gt;&lt;a href=&quot;http://www.iamcal.com/&quot; rel=&quot;nofollow noreferrer&quot;&gt;Cal Henderson&lt;/a&gt; (Flickr) wrote an article called &lt;a href=&quot;http://www.iamcal.com/publish/articles/php/parsing_email/&quot; rel=&quot;nofollow noreferrer&quot;&gt;Parsing Email Adresses in PHP&lt;/a&gt; and shows how to do proper RFC (2)822-compliant Email Address parsing.  You can also get the source code in &lt;a href=&quot;http://code.iamcal.com/php/rfc822/&quot; rel=&quot;nofollow noreferrer&quot;&gt;php&lt;/a&gt;, python and ruby which is &lt;a href=&quot;http://creativecommons.org/licenses/by-sa/2.5/&quot; rel=&quot;nofollow noreferrer&quot;&gt;cc licensed&lt;/a&gt;.&lt;/p&gt;&#xA;" OwnerUserId="27886" OwnerDisplayName="adnam" LastActivityDate="2008-10-14T16:35:44.180" CommentCount="3" CommunityOwnedDate="2009-12-16T00:37:16.437" />',
        '<row Id="4162353" PostTypeId="1" AcceptedAnswerId="4162367" CreationDate="2010-11-12T07:07:41.060" Score="1" ViewCount="507" Body="&lt;p&gt;I have a function to hide all divs on the page except one div. &lt;/p&gt;&#xA;&#xA;&lt;pre&gt;&lt;code&gt;// hide all div exceept div1&#xA;function hideAllExcept()&#xA;{&#xA;  $(\'div:not(#div1)\').slideUp(800);&#xA;}&#xA;&lt;/code&gt;&lt;/pre&gt;&#xA;&#xA;&lt;p&gt;or&lt;/p&gt;&#xA;&#xA;&lt;pre&gt;&lt;code&gt;// hide all div exceept \'thisdiv\' &#xA;function hideAllExcept()&#xA;{&#xA;  $(\'div:not(&quot;#div1&quot;)\').slideUp(800);&#xA;}&#xA;&lt;/code&gt;&lt;/pre&gt;&#xA;&#xA;&lt;p&gt;The above works fine (difference is first function doesn\'t have &quot;&quot; around #div1). However, I would like to pass a parameter in the hideAllExcept function to dynamically specify which div to not hide. So I changed the function to:&lt;/p&gt;&#xA;&#xA;&lt;pre&gt;&lt;code&gt;// hide all div exceept \'thisdiv\' &#xA;function hideAllExcept(thisdiv)&#xA;{&#xA;  $(\'div:not(thisdiv)\').slideUp(800);&#xA;}&#xA;&lt;/code&gt;&lt;/pre&gt;&#xA;&#xA;&lt;p&gt;if i call the function using: &lt;code&gt;hideAllExcept(\'#div1\')&lt;/code&gt; or &lt;code&gt;hideAllExcept(&quot;#div1&quot;)&lt;/code&gt; it doesn\'t work. It seems that $(\'div:not(thisdiv)\') still selects all divs, it doesn\'t exclude thisdiv.&lt;/p&gt;&#xA;&#xA;&lt;p&gt;Any ideas? Many thanks&lt;/p&gt;&#xA;" OwnerUserId="109027" LastActivityDate="2010-11-12T07:11:31.467" Title="Passing parameter to css :not selector" Tags="&lt;javascript&gt;&lt;css&gt;&lt;selector&gt;" AnswerCount="3" CommentCount="0" />',
        '<row Id="202080" PostTypeId="2" ParentId="8761" CreationDate="2008-10-14T17:28:54.933" Score="1" Body="&lt;p&gt;&lt;code&gt;afxGlobalData&lt;/code&gt; contains some useful information on the current colours, brushes and fonts being used by the MFC Feature Pack.  In particular I use &lt;code&gt;afxGlobalData.m_clrBarFace&lt;/code&gt; when painting my own control bar backgrounds.&lt;/p&gt;&#xA;&#xA;&lt;p&gt;(note that I am not in front of my work PC so the above syntax isn\'t spot on.)&lt;/p&gt;&#xA;" OwnerUserId="9236" OwnerDisplayName="Rob" LastActivityDate="2008-10-14T17:28:54.933" CommentCount="0" />',
        '<row Id="208433" PostTypeId="1" AcceptedAnswerId="208446" CreationDate="2008-10-16T12:57:34.090" Score="74" ViewCount="25804" Body="&lt;p&gt;Very basic question: how do I write a &lt;code&gt;short&lt;/code&gt; literal in C++?&lt;/p&gt;&#xA;&#xA;&lt;p&gt;I know the following:&lt;/p&gt;&#xA;&#xA;&lt;ul&gt;&#xA;&lt;li&gt;&lt;code&gt;2&lt;/code&gt; is an &lt;code&gt;int&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;2U&lt;/code&gt; is an &lt;code&gt;unsigned int&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;2L&lt;/code&gt; is a &lt;code&gt;long&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;2LL&lt;/code&gt; is a &lt;code&gt;long long&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;2.0f&lt;/code&gt; is a &lt;code&gt;float&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;2.0&lt;/code&gt; is a &lt;code&gt;double&lt;/code&gt;&lt;/li&gt;&#xA;&lt;li&gt;&lt;code&gt;\'\\2\'&lt;/code&gt; is a &lt;code&gt;char&lt;/code&gt;.&lt;/li&gt;&#xA;&lt;/ul&gt;&#xA;&#xA;&lt;p&gt;But how would I write a &lt;code&gt;short&lt;/code&gt; literal?  I tried &lt;code&gt;2S&lt;/code&gt; but that gives a compiler warning.&lt;/p&gt;&#xA;" OwnerUserId="18511" OwnerDisplayName="Kip" LastEditorUserId="18511" LastEditorDisplayName="Kip" LastEditDate="2015-04-22T21:39:49.070" LastActivityDate="2016-06-08T16:20:57.147" Title="How do I write a short literal in C++?" Tags="&lt;c++&gt;&lt;literals&gt;" AnswerCount="6" CommentCount="1" FavoriteCount="9" />'
    ]

    assert etalon_posts == posts, (
        "load_posts incorrectly loaded dataset"
    )


@pytest.fixture
def tiny_posts():
    posts = load_stop_words(POSTS_TINY_FPATH)
    return posts


def test_can_load_queries():
    queries = load_queries(QUERIES_TINY_FPATH)
    etalon_queries = [
        [2008, 2008, 3],
        [2008, 2010, 2],
        [2010, 2010, 0],
        [2010, 2010, 4]
    ]

    assert etalon_queries == queries, (
        "load_queries incorrectly loaded dataset"
    )


@pytest.fixture
def tiny_queries():
    queries = load_queries(QUERIES_TINY_FPATH)
    return queries


def test_build_data_to_analysis(tiny_posts, tiny_stop_words):
    test_analysis = StackoverflowAnalytics()
    test_analysis.build_data_to_analysis(tiny_posts, tiny_stop_words)
    data = test_analysis._data
    etalon_data = {
        2010: {'to': 1, 'selector': 1, 'parameter': 1, 'passing': 1, 'not': 1, 'css': 1},
        2008: {'how': 74, 'i': 74, 'write': 74, 'c': 74, 'do': 74, 'short': 74, 'in': 74, 'literal': 74}
    }

    assert etalon_data == data, (
        "build_data_to_analysis incorrectly works"
    )


@pytest.fixture
def data_to_analysis(tiny_posts, tiny_stop_words):
    test_analysis = StackoverflowAnalytics()
    test_analysis.build_data_to_analysis(tiny_posts, tiny_stop_words)
    data = test_analysis._data

    return data


@pytest.mark.parametrize(
    "start,end,num_words,expected",
    [
        pytest.param(
            2008, 2008, 3,
            {"start": 2008, "end": 2008, "top": [["c", 74], ["do", 74], ["how", 74]]},
        ),
        pytest.param(
            2008, 2010, 2,
            {"start": 2008, "end": 2010, "top": [["c", 74], ["do", 74]]},
        ),
        pytest.param(
            2010, 2010, 0,
            {"start": 2010, "end": 2010, "top": []},
        ),
    ],
)
def test_build_answer_to_query(start, end, num_words, expected, data_to_analysis):
    test_analysis = StackoverflowAnalytics()
    test_analysis._data = data_to_analysis
    response = json.loads(test_analysis.query(start, end, num_words))

    assert response == expected


CUSTOM_DATA_TO_ANALYSIS = [
    {
        "title": "Is SEO better better better done with repetition?",
        "score": "10",
        "year": 2019
    },
    {
        "title": "What is SEO?",
        "score": "5",
        "year": 2019
    },
    {
        "title": "Is Python better than Javascript?",
        "score": "20",
        "year": 2020
    }
]
CUSTOM_STOP_WORDS = ["is", "than"]


@pytest.fixture
def custom_data_to_analysis():
    test_analysis = StackoverflowAnalytics()
    data = {}
    for post in CUSTOM_DATA_TO_ANALYSIS:
        words = test_analysis._preprocess_title_in_post(post["title"], CUSTOM_STOP_WORDS)
        score = test_analysis._preprocess_score_in_post(post["score"])
        year = post["year"]
        for word in words:
            if year in data:
                if word in data[year]:
                    data[year][word] += score
                else:
                    data[year][word] = score

            else:
                data[year] = {word: score}

    return data


@pytest.mark.parametrize(
    "start,end,num_words,expected",
    [
        pytest.param(
            2019, 2019, 2,
            {"start": 2019, "end": 2019, "top": [ ["seo", 15], ["better", 10]]},
        ),
        pytest.param(
            2019, 2020, 4,
            {"start": 2019, "end": 2020, "top": [["better", 30], ["javascript", 20], ["python", 20], ["seo", 15]]},
        ),
    ],
)
def test_custom_params_from_description_homework(start, end, num_words, expected, custom_data_to_analysis):
    test_analysis = StackoverflowAnalytics()
    test_analysis._data = custom_data_to_analysis
    response = json.loads(test_analysis.query(start, end, num_words))

    assert response == expected

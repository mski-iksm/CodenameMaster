import unittest

import pandas as pd
from pandera.typing import DataFrame

from codename_master.guesser.wordnet.convert_wordnet_scores import ConvertWordnetScores
from codename_master.guesser.wordnet.make_connected_words_table import ConnectedWordsTableSchema


class TestConvertWordnetScores(unittest.TestCase):
    def test_score_by_link(self):
        connected_words_table = DataFrame[ConnectedWordsTableSchema](
            pd.DataFrame(
                {
                    'word': ['word'],
                    'link1': ['hype'],
                    'link2': [None],
                    'link3': [None],
                }
            )
        )
        resulted = connected_words_table.apply(ConvertWordnetScores._score_by_link, axis=1)
        expected = pd.Series([1.0])
        pd.testing.assert_series_equal(resulted, expected)

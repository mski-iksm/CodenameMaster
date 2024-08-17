import unittest

import pandas as pd
from pandera.typing import DataFrame

from codename_master.estimator.make_estimation_table import EstimationTableSchema, MakeEstimationTable
from codename_master.guesser.word_guesser_base import GuessedWordsSchema


class TestMakeEstimationTable(unittest.TestCase):
    def test_make_estimation_table(self):
        aggregated_scores = DataFrame[GuessedWordsSchema](
            pd.DataFrame(
                dict(
                    target_word=['A', 'A', 'B'],
                    word=['あ', 'い', 'あ'],
                    score=[1.0, 1.0, 1.0],
                )
            )
        )
        resulted = MakeEstimationTable._make_estimation_table(
            aggregated_scores=aggregated_scores,
            my_words=['A', 'B'],
            opponent_words=[],
            black_words=[],
            white_words=[],
        )
        expected = DataFrame[EstimationTableSchema](
            pd.DataFrame(
                dict(
                    word=['あ', 'い'],
                    my_score=[2.0, 1.0],
                    target_my_words=['A,B', 'A'],
                    target_my_words_count=[2, 1],
                )
            )
        )
        pd.testing.assert_frame_equal(resulted, expected)

    def test_make_estimation_table_with_opponent_words(self):
        aggregated_scores = DataFrame[GuessedWordsSchema](
            pd.DataFrame(
                dict(
                    target_word=['A', 'A', 'B', 'C', 'D'],
                    word=['あ', 'い', 'あ', 'う', 'え'],
                    score=[1.0, 1.0, 1.0, 1.0, 1.0],
                )
            )
        )
        resulted = MakeEstimationTable._make_estimation_table(
            aggregated_scores=aggregated_scores,
            my_words=['A'],
            opponent_words=['B'],
            black_words=['C'],
            white_words=['D'],
        )
        expected = DataFrame[EstimationTableSchema](
            pd.DataFrame(
                dict(
                    word=['い', 'あ', 'え', 'う'],
                    my_score=[1.0, 0.0, -0.5, -1000.0],
                    target_my_words=['A', 'A', '', ''],
                    target_my_words_count=[1, 1, 0, 0],
                )
            )
        )
        pd.testing.assert_frame_equal(resulted.reset_index(drop=True), expected.reset_index(drop=True))

    def test_remove_english_words(self):
        df = pd.DataFrame(
            dict(
                word=['a', 'あ', 'いc', '1', '_'],
                my_score=[1.0, 2.0, 3.0, 4.0, 5.0],
                target_my_words=['A', 'A,B', '', '', ''],
                target_my_words_count=[1, 2, 0, 0, 0],
            )
        )
        expected = pd.DataFrame(
            dict(
                word=['あ', 'いc'],
                my_score=[2.0, 3.0],
                target_my_words=['A,B', ''],
                target_my_words_count=[2, 0],
            )
        )
        resulted = MakeEstimationTable._remove_english_words(df)
        pd.testing.assert_frame_equal(resulted.reset_index(drop=True), expected.reset_index(drop=True))

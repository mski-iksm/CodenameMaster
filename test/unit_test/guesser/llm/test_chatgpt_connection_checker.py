import unittest
from unittest.mock import patch

import pandas as pd
from pandera.typing import DataFrame

from codename_master.guesser.llm.chatgpt_connection_checker import ChatGPTConnectionChecker
from codename_master.guesser.word_guesser_base import GuessedWordsSchema


class TestChatGPTConnectionChecker(unittest.TestCase):
    def test_check_connection_with_invalid_words(self):
        guessed_words = DataFrame[GuessedWordsSchema](
            pd.DataFrame(
                dict(
                    word=['ペット', 'ペット', '野生', '野生'],
                    target_word=['犬', '猫', '熊', '狼'],
                    score=[1.0, 1.0, 1.0, 1.0],
                )
            )
        )
        invalid_words = ['猿']

        with patch('codename_master.guesser.llm.chatgpt_connection_checker.ChatGPTConnectionChecker._query_chatgpt') as mock_query_chatgpt:
            mock_query_chatgpt.return_value = [
                {'ヒント単語': '野生', '想起するinvalid_wordsの単語': ['猿']},
            ]
            resulted = ChatGPTConnectionChecker._check_connection_with_invalid_words(guessed_words=guessed_words, invalid_words=invalid_words)
            expected = pd.DataFrame(
                dict(
                    word=['野生'],
                    target_word=['猿'],
                    score=[1.0],
                )
            )
            pd.testing.assert_frame_equal(resulted, expected)

import unittest
from unittest.mock import patch

import pandas as pd

from codename_master.guesser.llm.chatgpt_guesser import ChatgptGuesser


class TestChatgptGuesser(unittest.TestCase):
    def test_make_guessed_words(self):
        my_words = ['犬', '猫', '飛行機', '自動車', '鳥', '魚', '犀', '象', '熊', '狼']
        opponent_words = ['いるか', 'くじら']
        black_words = ['鹿']
        white_words = ['猿']

        with patch('codename_master.guesser.llm.chatgpt_guesser.ChatgptGuesser._query_chatgpt') as mock_query_chatgpt:
            mock_query_chatgpt.return_value = [
                {'ヒント単語': 'ペット', '想起するmy_wordsの単語': ['犬', '猫']},
                {'ヒント単語': '野生', '想起するmy_wordsの単語': ['熊', '狼']},
            ]
            resulted = ChatgptGuesser._make_guessed_words(my_words=my_words, opponent_words=opponent_words, black_words=black_words, white_words=white_words)
            expected = pd.DataFrame(
                dict(
                    word=['ペット', 'ペット', '野生', '野生'],
                    target_word=['犬', '猫', '熊', '狼'],
                    score=[1.0, 1.0, 1.0, 1.0],
                )
            )
            pd.testing.assert_frame_equal(resulted, expected)

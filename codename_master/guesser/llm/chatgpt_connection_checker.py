import json
import os

import gokart
import luigi
import pandas as pd
from openai import OpenAI
from pandera.typing import DataFrame

from codename_master.guesser.llm.chatgpt_error import InvalidGPTOutputError
from codename_master.guesser.word_guesser_base import GuessedWordsSchema, WordGuesserBase

client = OpenAI(api_key=os.getenv('OPENAI_API_PERSONAL_KEY'))


class ChatGPTConnectionChecker(WordGuesserBase):
    chatgpt_guesser = gokart.TaskInstanceParameter(expected_type=WordGuesserBase)

    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

    RETRY_COUNT = 5

    def requires(self):
        return self.chatgpt_guesser

    def run(self):
        guessed_words = DataFrame[GuessedWordsSchema](self.load())
        self.dump(
            self._check_connection_with_invalid_words(guessed_words=guessed_words, invalid_words=self.opponent_words + self.black_words + self.white_words)
        )

    @classmethod
    def _check_connection_with_invalid_words(cls, guessed_words: DataFrame[GuessedWordsSchema], invalid_words: list[str]) -> DataFrame[GuessedWordsSchema]:
        guessed_words_list = list(set(guessed_words['word'].tolist()))
        guess_words_list = cls._make_connected_words_list(guessed_words_list=guessed_words_list, invalid_words=invalid_words)
        return DataFrame[GuessedWordsSchema](cls._make_df_from_guess_words_list(response=guess_words_list))

    @classmethod
    def _make_connected_words_list(cls, guessed_words_list: str, invalid_words: str) -> list[dict[str, list[str]]]:
        prompt = cls._make_prompt(guessed_words_list=guessed_words_list, invalid_words=invalid_words)
        for _ in range(cls.RETRY_COUNT):
            try:
                response = cls._query_chatgpt(prompt=prompt)
                break
            except (InvalidGPTOutputError, json.decoder.JSONDecodeError):
                continue
        print(response)

        return response

    @classmethod
    def _make_prompt(cls, guessed_words_list: str, invalid_words: str) -> str:
        guessed_words_str = ', '.join(guessed_words_list)
        invalid_words_str = ', '.join(invalid_words)

        return f"""これから与える候補キーワードのうち、invalid_wordsのいずれかを想起できるかを教えて下さい。
少しでも想起できるものは含めるようにしてください。
回答時にはどの単語を想起できるかも教えてください。

候補ワード = [{guessed_words_str}]

invalid_words = [{invalid_words_str}]

なお回答は以下のJSON形式でお願いします。
[{{"ヒント単語": "XXXXXX", "想起するinvalid_wordsの単語": ["XXXXXX", "XXXXXX"]}}]
"""

    @classmethod
    def _query_chatgpt(cls, prompt: str) -> list[dict[str, list[str]]]:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': prompt},
            ],
        )
        answer = response.choices[0].message.content
        answers_list = json.loads(answer)

        # 形式をassert
        if not isinstance(answers_list, list):
            raise InvalidGPTOutputError('answer_listがlistでない')

        if any([not isinstance(answer_dict, dict) for answer_dict in answers_list]):
            raise InvalidGPTOutputError('answer_listにdictでないものがある')

        return answers_list

    @classmethod
    def _make_df_from_guess_words_list(cls, response: list[dict[str, list[str]]]) -> pd.DataFrame:
        guess_word_2_target_words = {guess_item['ヒント単語']: guess_item['想起するinvalid_wordsの単語'] for guess_item in response}

        rows = [
            {'word': guess_word, 'target_word': target_word} for guess_word, target_words in guess_word_2_target_words.items() for target_word in target_words
        ]
        df = pd.DataFrame(rows)
        df['score'] = 1.0
        return df

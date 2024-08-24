import json
import os

import luigi
import pandas as pd
from openai import OpenAI
from pandera.typing import DataFrame

from codename_master.guesser.llm.chatgpt_error import InvalidGPTOutputError
from codename_master.guesser.word_guesser_base import GuessedWordsSchema, WordGuesserBase

client = OpenAI(api_key=os.getenv('OPENAI_API_PERSONAL_KEY'))


class ChatgptGuesser(WordGuesserBase):
    my_words: list[str] = luigi.ListParameter()
    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

    RETRY_COUNT = 5

    def run(self):
        guessed_words = self._make_guessed_words(
            my_words=self.my_words,
            opponent_words=self.opponent_words,
            black_words=self.black_words,
            white_words=self.white_words,
        )
        self.dump(guessed_words)

    @classmethod
    def _make_guessed_words(
        cls,
        my_words: str,
        opponent_words: str,
        black_words: str,
        white_words: str,
    ) -> DataFrame[GuessedWordsSchema]:
        guess_words_list = cls._make_guess_words_list(my_words=my_words, opponent_words=opponent_words, black_words=black_words, white_words=white_words)
        return DataFrame[GuessedWordsSchema](cls._make_df_from_guess_words_list(response=guess_words_list))

    @classmethod
    def _make_guess_words_list(cls, my_words: str, opponent_words: str, black_words: str, white_words: str) -> list[dict[str, list[str]]]:
        prompt = cls._make_prompt(my_words=my_words, opponent_words=opponent_words, black_words=black_words, white_words=white_words)
        for _ in range(cls.RETRY_COUNT):
            try:
                response = cls._query_chatgpt(prompt=prompt)
                break
            except (InvalidGPTOutputError, json.decoder.JSONDecodeError):
                continue

        return response

    @classmethod
    def _make_prompt(cls, my_words: str, opponent_words: str, black_words: str, white_words: str) -> str:
        my_words_str = ', '.join(my_words)
        opponent_words_str = ', '.join(opponent_words)
        black_words_str = ', '.join(black_words)
        white_words_str = ', '.join(white_words)

        return f"""これから与えるキーワードのうち、my_wordsのいくつかの単語を想起できる単語を10個教えて下さい。
なるべく多くのmy_wordsを想起できる単語を教えてください。
ただし、opponent_words,black_words,white_wordsを想起できてしまう単語は教えないでください。
特にblack_wordsに関連する単語は絶対に避けたいので、ちょっとでもこれらを想起しかねない単語は除外してください
回答時にはどの単語を想起できるかも教えてください。

my_words = [{my_words_str}]
opponent_words = [{opponent_words_str}]
black_words = [{black_words_str}]
white_words = [{white_words_str}]

なお回答は以下のJSON形式でお願いします。
[{{"ヒント単語": "XXXXXX", "想起するmy_wordsの単語": ["XXXXXX", "XXXXXX"]}}]
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
        guess_word_2_target_words = {guess_item['ヒント単語']: guess_item['想起するmy_wordsの単語'] for guess_item in response}

        rows = [
            {'word': guess_word, 'target_word': target_word} for guess_word, target_words in guess_word_2_target_words.items() for target_word in target_words
        ]
        df = pd.DataFrame(rows)
        df['score'] = 1.0
        return df

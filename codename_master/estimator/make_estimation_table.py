import gokart
import luigi
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series

from codename_master.guesser.word_guesser_base import GuessedWordsSchema
from codename_master.score_aggregator.score_aggregator import AggregateScores


class EstimationTableSchema(pa.DataFrameModel):
    word: Series[str] = pa.Field()
    my_score: Series[float] = pa.Field()
    target_my_words: Series[str] = pa.Field()
    target_my_words_count: Series[int] = pa.Field()


class MakeEstimationTable(gokart.TaskOnKart):
    aggregate_scores = gokart.TaskInstanceParameter(expected_type=AggregateScores)

    my_words: list[str] = luigi.ListParameter()
    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

    MY_WORD_COEF = 1.0
    OPPONENT_WORD_COEF = -1.0
    BLACK_WORD_COEF = -1000.0
    WHITE_WORD_COEF = -0.5

    __version: float = luigi.FloatParameter(default=0.003)

    def requires(self):
        return self.aggregate_scores

    def run(self):
        aggregated_scores = DataFrame[GuessedWordsSchema](self.load_data_frame())
        top_hint_words_table = self._make_estimation_table(
            aggregated_scores=aggregated_scores,
            my_words=self.my_words,
            opponent_words=self.opponent_words,
            black_words=self.black_words,
            white_words=self.white_words,
        )
        self.dump(top_hint_words_table)

    @classmethod
    def _make_estimation_table(
        cls,
        aggregated_scores: DataFrame[GuessedWordsSchema],
        my_words: list[str],
        opponent_words: list[str],
        black_words: list[str],
        white_words: list[str],
    ) -> DataFrame[EstimationTableSchema]:
        my_score_table = aggregated_scores.copy()
        my_score_table['coef'] = my_score_table['target_word'].apply(lambda x: cls._calc_coef(x, my_words, opponent_words, black_words, white_words))
        my_score_table['my_score'] = my_score_table['score'] * my_score_table['coef']
        total_scores_by_hint_word = my_score_table.groupby('word')[['my_score']].sum().reset_index()

        total_scores_by_hint_word = cls._remove_english_words(total_scores_by_hint_word)

        # my_scoreが高いhint_wordを取得
        top_hint_words_table = total_scores_by_hint_word.sort_values('my_score', ascending=False).iloc[:20]
        top_hint_words = top_hint_words_table['word'].tolist()

        # hint_wordsごとにtarget_wordを集計
        target_words_by_hint_word: list[list[str]] = [
            aggregated_scores[aggregated_scores['word'] == hint_word]['target_word'].unique().tolist() for hint_word in top_hint_words
        ]
        target_my_words = [','.join([word for word in words if word in my_words]) for words in target_words_by_hint_word]
        target_my_words_count = [len([word for word in words if word in my_words]) for words in target_words_by_hint_word]

        top_hint_words_table['target_my_words'] = target_my_words
        top_hint_words_table['target_my_words_count'] = target_my_words_count

        return DataFrame[EstimationTableSchema](top_hint_words_table)

    @classmethod
    def _remove_english_words(cls, df: pd.DataFrame) -> pd.DataFrame:
        # wordが全部英語の場合は除外
        # 記号や数字も英字とみなす
        return df[~df['word'].str.match(r'^[a-zA-Z_0-9]+$')]

    @classmethod
    def _calc_coef(
        cls,
        target_word: str,
        my_words: list[str],
        opponent_words: list[str],
        black_words: list[str],
        white_words: list[str],
    ) -> pd.DataFrame:
        if target_word in my_words:
            return cls.MY_WORD_COEF
        if target_word in opponent_words:
            return cls.OPPONENT_WORD_COEF
        if target_word in black_words:
            return cls.BLACK_WORD_COEF
        if target_word in white_words:
            return cls.WHITE_WORD_COEF

        raise ValueError(f'Unexpected target_word: {target_word}')

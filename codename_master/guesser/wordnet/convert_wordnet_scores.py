import gokart
import luigi
import pandera as pa
from pandera.typing import DataFrame, Series

from codename_master.guesser.wordnet.make_connected_words_table import ConnectedWordsTableSchema, MakeConnectedWordsTable


class ScoredWordsSchema(pa.DataFrameModel):
    target_word: Series[str] = pa.Field()
    word: Series[str] = pa.Field()
    score: Series[float] = pa.Field()


class ConvertWordnetScores(gokart.TaskOnKart):
    make_connected_words_table = gokart.TaskInstanceParameter(expected_type=MakeConnectedWordsTable)
    target_word: str = luigi.Parameter()

    __version: float = luigi.FloatParameter(default=0.001)

    def requires(self):
        return self.make_connected_words_table

    def run(self):
        connected_words_table = DataFrame[ConnectedWordsTableSchema](self.load_data_frame())
        self.dump(self._make_scored_words(connected_words_table=connected_words_table, target_word=self.target_word))

    @classmethod
    def _make_scored_words(cls, connected_words_table: DataFrame[ConnectedWordsTableSchema], target_word: str) -> DataFrame[ScoredWordsSchema]:
        df = connected_words_table[['word']].copy()
        df['target_word'] = target_word

        # TODO: TBD
        df['score'] = 1.0

        # 最高スコアだけ残す
        df = df.sort_values('score', ascending=False).drop_duplicates(subset=['target_word', 'word'])
        return DataFrame[ScoredWordsSchema](df[['target_word', 'word', 'score']])

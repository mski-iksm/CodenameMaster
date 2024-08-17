import luigi
from pandera.typing import DataFrame

from codename_master.guesser.word_guesser_base import GuessedWordsSchema, WordGuesserBase
from codename_master.guesser.wordnet.convert_wordnet_scores import ConvertWordnetScores, ScoredWordsSchema
from codename_master.guesser.wordnet.make_connected_words_table import MakeConnectedWordsTable


class WordNetGuesser(WordGuesserBase):
    target_word: str = luigi.Parameter()
    traverse_depth: int = luigi.IntParameter(default=3)

    def requires(self):
        # 結合のあるwordsをtableにまとめる
        make_connected_words_table = MakeConnectedWordsTable(target_word=self.target_word)

        # scoreを調整する
        convert_wordnet_scores = ConvertWordnetScores(make_connected_words_table=make_connected_words_table, target_word=self.target_word)

        return convert_wordnet_scores

    def run(self):
        guessed_words = self._make_guessed_words(target_word=self.target_word, scored_words=DataFrame[ScoredWordsSchema](self.load_data_frame()))
        self.dump(guessed_words)

    @classmethod
    def _make_guessed_words(cls, target_word: str, scored_words: DataFrame[ScoredWordsSchema]) -> DataFrame[GuessedWordsSchema]:
        df = scored_words.copy()
        df['target_word'] = target_word
        return DataFrame[GuessedWordsSchema](df)

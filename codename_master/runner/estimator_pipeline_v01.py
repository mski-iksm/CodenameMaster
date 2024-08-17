# wordnetでGuess
import luigi

from codename_master.estimator.make_estimation_table import MakeEstimationTable
from codename_master.guesser.wordnet.wordnet_guesser import WordNetGuesser
from codename_master.runner.estimator_pipeline_base import EstimatorPipelineBase
from codename_master.score_aggregator.score_aggregator import AggregateScores


class EstimatorPipelineV01(EstimatorPipelineBase):
    target_words: list[str] = luigi.ListParameter()
    my_words: list[str] = luigi.ListParameter()
    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

    def requires(self):
        # フィールド単語ごとにヒント単語とスコアを出す
        hint_guesser_by_word = {target_word: WordNetGuesser(target_word=target_word) for target_word in self.target_words}

        # 全フィールド単語のスコアを集計
        aggregate_scores = AggregateScores(hint_guessers=list(hint_guesser_by_word.values()))

        # 合計スコアを算出
        make_estimation_table = MakeEstimationTable(
            aggregate_scores=aggregate_scores,
            my_words=self.my_words,
            opponent_words=self.opponent_words,
            black_words=self.black_words,
            white_words=self.white_words,
        )

        return make_estimation_table

    def run(self):
        self.dump(self.load())

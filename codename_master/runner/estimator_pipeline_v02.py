# wordnetでGuess
import luigi

from codename_master.estimator.make_estimation_table import MakeEstimationTable
from codename_master.guesser.llm.chatgpt_connection_checker import ChatGPTConnectionChecker
from codename_master.guesser.llm.chatgpt_guesser import ChatgptGuesser
from codename_master.runner.estimator_pipeline_base import EstimatorPipelineBase
from codename_master.score_aggregator.score_aggregator import AggregateScores


class EstimatorPipelineV02(EstimatorPipelineBase):
    # target_words: list[str] = luigi.ListParameter()
    my_words: list[str] = luigi.ListParameter()
    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

    def requires(self):
        # 全フィールド単語まとめてヒント候補を出す
        chatgpt_guesser = ChatgptGuesser(
            my_words=self.my_words,
            opponent_words=self.opponent_words,
            black_words=self.black_words,
            white_words=self.white_words,
        )

        # ヒント単語をngワードと比較して、想起connectionを作る
        chatgpt_connection_checker = ChatGPTConnectionChecker(
            chatgpt_guesser=chatgpt_guesser,
            opponent_words=self.opponent_words,
            black_words=self.black_words,
            white_words=self.white_words,
        )

        # 全フィールド単語のスコアを集計
        aggregate_scores = AggregateScores(hint_guessers=[chatgpt_guesser, chatgpt_connection_checker])

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

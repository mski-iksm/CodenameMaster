import gokart
import luigi
from pydantic import BaseModel


class EstimatedWords(BaseModel):
    hint_word: str
    words_num: int
    target_words: list[str]


class EstimatorPipelineBase(gokart.TaskOnKart):
    """DataFrame[EstimationTableSchema]を返す"""

    my_words: list[str] = luigi.ListParameter()
    opponent_words: list[str] = luigi.ListParameter()
    black_words: list[str] = luigi.ListParameter()
    white_words: list[str] = luigi.ListParameter()

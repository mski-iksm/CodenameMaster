import gokart
import luigi
import pandera as pa
from pandera.typing import Series


class GuessedWordsSchema(pa.DataFrameModel):
    target_word: Series[str] = pa.Field()
    word: Series[str] = pa.Field()
    score: Series[float] = pa.Field()


class WordGuesserBase(gokart.TaskOnKart):
    target_word: str = luigi.Parameter(description='ボード上の既知単語')

    # DataFrame[GuessedWordsSchema] を出力する

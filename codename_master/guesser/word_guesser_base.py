import gokart
import pandera as pa
from pandera.typing import Series


class GuessedWordsSchema(pa.DataFrameModel):
    target_word: Series[str] = pa.Field()
    word: Series[str] = pa.Field()
    score: Series[float] = pa.Field()


class WordGuesserBase(gokart.TaskOnKart):
    # DataFrame[GuessedWordsSchema] を出力する
    pass

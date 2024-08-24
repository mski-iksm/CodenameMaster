import logging

import gokart
from pandera.typing import DataFrame

from codename_master.estimator.make_estimation_table import EstimationTableSchema
from codename_master.runner.estimator_pipeline_v02 import EstimatorPipelineV02

if __name__ == '__main__':
    my_words = ['犬', '猫', '飛行機', '自動車', '鳥', '魚', '犀', '象', '熊', '狼']
    opponent_words = ['いるか', 'くじら']
    black_words = ['鹿']
    white_words = ['猿']

    result = DataFrame[EstimationTableSchema](
        gokart.build(
            EstimatorPipelineV02(
                target_words=my_words + opponent_words + black_words + white_words,
                my_words=my_words,
                opponent_words=opponent_words,
                black_words=black_words,
                white_words=white_words,
            ),
            log_level=logging.ERROR,
        )
    )
    print(result)

import logging

import gokart

from codename_master.runner.estimator_pipeline_v01 import EstimatorPipelineV01

if __name__ == '__main__':
    my_words = ['犬', '猫']
    opponent_words = ['いるか', 'くじら']
    black_words = ['鹿']
    white_words = ['猿']

    result = gokart.build(
        EstimatorPipelineV01(
            target_words=my_words + opponent_words + black_words + white_words,
            my_words=my_words,
            opponent_words=opponent_words,
            black_words=black_words,
            white_words=white_words,
        ),
        log_level=logging.ERROR,
    )
    print(result)

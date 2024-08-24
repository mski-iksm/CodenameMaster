import logging

import gokart
import multiprocess as mp
import pandas as pd
from pandera.typing import DataFrame

from codename_master.estimator.make_estimation_table import EstimationTableSchema
from codename_master.runner.estimator_pipeline_v02 import EstimatorPipelineV02


def _run_task(my_words: list[str], opponent_words: list[str], black_words: list[str], white_words: list[str], return_dict):
    task = EstimatorPipelineV02
    estimated_table = DataFrame[EstimationTableSchema](
        gokart.build(
            task(
                target_words=my_words + opponent_words + black_words + white_words,
                my_words=my_words,
                opponent_words=opponent_words,
                black_words=black_words,
                white_words=white_words,
            ),
            log_level=logging.INFO,
        )
    )
    return_dict.update(estimated_table.to_dict())


def run_estimator_in_new_process(
    my_words: list[str], opponent_words: list[str], black_words: list[str], white_words: list[str]
) -> DataFrame[EstimationTableSchema]:
    """
    Run gokart task in a new process.
    """

    manager = mp.Manager()
    return_dict = manager.dict()
    process = mp.Process(
        target=_run_task,
        kwargs={
            'my_words': my_words,
            'opponent_words': opponent_words,
            'black_words': black_words,
            'white_words': white_words,
            'return_dict': return_dict,
        },
    )
    process.start()
    process.join()
    print(return_dict)

    returned_df = pd.DataFrame(return_dict)
    print(returned_df)

    return DataFrame[EstimationTableSchema](returned_df)

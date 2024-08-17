import gokart

from codename_master.guesser.word_guesser_base import WordGuesserBase


class AggregateScores(gokart.TaskOnKart):
    hint_guessers = gokart.ListTaskInstanceParameter(expected_elements_type=WordGuesserBase)

    def requires(self):
        return self.hint_guessers

    def run(self):
        self.dump(self.load_data_frame())

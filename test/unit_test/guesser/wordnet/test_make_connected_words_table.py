import unittest

from codename_master.guesser.wordnet.make_connected_words_table import MakeConnectedWordsTable


class TestMakeConnectedWordsTable(unittest.TestCase):
    def test_make_connected_words_table(self):
        result = MakeConnectedWordsTable._make_connected_words_table(target_word='犬')
        self.assertEqual(len(result), 23212)

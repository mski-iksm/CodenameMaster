import sqlite3

import gokart
import luigi
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series


class ConnectedWordsTableSchema(pa.DataFrameModel):
    word: Series[str] = pa.Field()
    link1: Series[str] = pa.Field()
    link2: Series[str] = pa.Field(nullable=True)
    link3: Series[str] = pa.Field(nullable=True)


class MakeConnectedWordsTable(gokart.TaskOnKart):
    target_word: str = luigi.Parameter()

    def run(self):
        self.dump(self._make_connected_words_table(target_word=self.target_word))

    @classmethod
    def _make_connected_words_table(cls, target_word: str) -> DataFrame[ConnectedWordsTableSchema]:
        conn = sqlite3.connect('./data/wnjpn.db')
        cur = conn.execute(f"""
        SELECT
            synlink.link AS link_hop1,
            word1.lemma AS lemma1,
            synlink2.link AS link_hop2,
            word2.lemma AS lemma2,
            synlink3.link AS link_hop3,
            word3.lemma AS lemma3

        -- target_word に対する結合synset（hop1）を取得
        FROM word
        INNER JOIN sense ON word.wordid = sense.wordid
        INNER JOIN synlink ON sense.synset = synlink.synset1
        INNER JOIN sense AS sense1 ON synlink.synset2 = sense1.synset
        INNER JOIN word AS word1 ON sense1.wordid = word1.wordid

        -- hop1 に対する結合synset（hop2）を取得
        INNER JOIN synlink AS synlink2 ON synlink.synset2 = synlink2.synset1
        INNER JOIN sense AS sense2 ON synlink2.synset2 = sense2.synset
        INNER JOIN word AS word2 ON sense2.wordid = word2.wordid

        -- hop2 に対する結合synset（hop3）を取得
        INNER JOIN synlink AS synlink3 ON synlink2.synset2 = synlink3.synset1
        INNER JOIN sense AS sense3 ON synlink3.synset2 = sense3.synset
        INNER JOIN word AS word3 ON sense3.wordid = word3.wordid

        WHERE word.lemma = '{target_word}'
        """)

        df = pd.DataFrame(cur.fetchall(), columns=['link_hop1', 'lemma1', 'link_hop2', 'lemma2', 'link_hop3', 'lemma3'])
        df.loc[df['link_hop2'] != 'hype', ['link_hop3', 'lemma3']] = None
        df.loc[df['link_hop1'] != 'hype', ['link_hop2', 'lemma2', 'link_hop3', 'lemma3']] = None
        df = df.drop_duplicates()

        # 最も右のNon-nullを採用
        df['word'] = df['lemma3'].fillna(df['lemma2']).fillna(df['lemma1'])
        df = df.rename(columns={'link_hop1': 'link1', 'link_hop2': 'link2', 'link_hop3': 'link3'})
        return DataFrame[ConnectedWordsTableSchema](df[['word', 'link1', 'link2', 'link3']])

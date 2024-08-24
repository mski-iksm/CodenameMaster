import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton

from codename_master.ocr.read_board import read_board
from codename_master.streamlit_ui.get_board_words import get_my_words, get_opponent_words
from codename_master.streamlit_ui.run_estimator import run_estimator_in_new_process

if __name__ == '__main__':
    paste_result = pbutton('📋 Paste an image')

    # todo: トグルかなにかで切り替える
    my_color = 'blue'

    if paste_result.image_data is not None:
        st.write('Pasted image:')
        st.image(paste_result.image_data)

        # OCRで読み取り
        # todo: OCR制度が悪い
        words_by_color = read_board(image=paste_result.image_data)

        # 読み取り結果を出力
        st.write('Red words:', words_by_color.red_words)
        st.write('Blue words:', words_by_color.blue_words)
        st.write('Black words:', words_by_color.black_words)
        st.write('White words:', words_by_color.white_words)

        my_words = get_my_words(words_by_color=words_by_color, my_color=my_color)
        opponent_words = get_opponent_words(words_by_color=words_by_color, my_color=my_color)
        black_words = words_by_color.black_words
        white_words = words_by_color.white_words

        estimated_table = run_estimator_in_new_process(my_words=my_words, opponent_words=opponent_words, black_words=black_words, white_words=white_words)

        st.subheader('ヒントワード')
        st.dataframe(estimated_table)

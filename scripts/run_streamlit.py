import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton

from codename_master.ocr.read_board import read_board

if __name__ == '__main__':
    paste_result = pbutton('📋 Paste an image')

    if paste_result.image_data is not None:
        st.write('Pasted image:')
        st.image(paste_result.image_data)

        # OCRで読み取り
        words_by_color = read_board(image=paste_result.image_data)

        # 読み取り結果を出力
        st.write('Red words:', words_by_color.red_words)
        st.write('Blue words:', words_by_color.blue_words)
        st.write('Black words:', words_by_color.black_words)
        st.write('White words:', words_by_color.white_words)

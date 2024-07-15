import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton

if __name__ == "__main__":
    paste_result = pbutton("📋 Paste an image")

    if paste_result.image_data is not None:
        st.write("Pasted image:")
        st.image(paste_result.image_data)

        # OCRで読み取り

        # 読み取り結果を出力

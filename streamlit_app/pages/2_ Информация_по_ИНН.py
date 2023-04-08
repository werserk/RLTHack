import streamlit as st
import pandas as pd

inn = st.text_input("Введите ИНН:")

if st.button('Найти инофрмацию'):
    st.write(inn)

col1, col2, col3 = st.columns(3)

with col1:
    col1.markdown("Информация")

with col2:
    col2.markdown("Информация")

with col3:
    col3.markdown("Информация")

col4, col5, col6 = st.columns(3)

with col4:
    col4.markdown("Информация")

with col5:
    col5.markdown("Информация")

with col6:
    col6.markdown("Информация")

st.download_button(
        label="Скачать",
        data="инфа хз",
        mime='text/csv',
    )
import streamlit as st
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool
import pickle
import utils

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Загрузите список ИНН")

with col2:
    number_of_cols = st.selectbox("Сколько строк выводить:", [5, 10, 15, 30, "Все"])

if uploaded_file is not None:
    inns = pd.read_csv(uploaded_file)
    if number_of_cols == "Все":
        number_of_cols = len(inns)

    if "data" not in st.session_state:
        st.session_state["data"] = utils.load()

    df = st.session_state["data"]
    missed_inns = set(inns["inn"].astype(str)) - set(df["inn"].astype(str))
    if missed_inns:
        st.warning(f"Данные ИНН не найдены в базе: {','.join(missed_inns)}")
    df = df[["inn", "score"]]
    df = df[df['inn'].isin(inns['inn'])]
    df["inn"] = df["inn"].astype(str)
    df = df.head(number_of_cols)
    df.set_index("inn", inplace = True)

    st.dataframe(df, use_container_width = True)

    st.download_button(
        label="Скачать",
        data=convert_df(df),
        file_name='top_of_companies.csv',
        mime='text/csv',
    )
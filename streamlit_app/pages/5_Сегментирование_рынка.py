import streamlit as st
import utils

def filter_columns(final_df, okved, region):
    return final_df[(final_df["okved_basic_code"] == okved) & (final_df["lower_region"] == region)]

if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

df = st.session_state["data"]

col1, col2 = st.columns(2)

okved = col1.selectbox("Выберите ОКВЕД", set(df["okved_basic_code"]))
region = col2.selectbox("Выберите регион", set(df["lower_region"]))

filtered_df = filter_columns(df, okved, region)

filtered_df = filtered_df[["inn", "score", "name"]].reset_index(drop = True)

st.dataframe(filtered_df, use_container_width = True)

st.download_button(
    label="Скачать",
    data=utils.convert_df(filtered_df),
    file_name='segmented_companies.csv',
    mime='text/csv',
)
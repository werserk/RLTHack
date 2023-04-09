import streamlit as st
import utils

st.set_page_config(layout="wide")

def filter_columns(final_df, okved, region):
    return final_df[(final_df["okved_basic_code"] == okved) & (final_df["lower_region"] == region)]

if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

df = st.session_state["data"]

col1, col2 = st.columns(2)
okveds = sorted(set(df["okved_basic_code"].dropna()))
regions = sorted(set(df["lower_region"].dropna()))

okveds.remove("46.32")
regions.remove("москва")

okved = col1.selectbox("Выберите ОКВЭД", ["46.32"] + okveds)
region = col2.selectbox("Выберите регион", ["москва"] + regions)

filtered_df = filter_columns(df, okved, region)

filtered_df = filtered_df[["inn", "name", "score"]].reset_index(drop = True)

df_to_show = filtered_df.rename(columns = {"inn": "ИНН", "score": "Рейтинг", "name": "Название"})
df_to_show = df_to_show.set_index("ИНН")
st.dataframe(df_to_show, use_container_width = True)

st.download_button(
    label="Скачать",
    data=utils.convert_df(filtered_df),
    file_name='segmented_companies.csv',
    mime='text/csv',
)
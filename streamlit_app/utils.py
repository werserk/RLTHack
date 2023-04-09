import pandas as pd
import streamlit as st

@st.cache_data
def load():
    data = pd.read_feather("/Users/deevs/development/programming/AIML/tasks_2023/rlt_hack/RLTHack/streamlit_app/data/data.feather")
    data["lower_region"] = data["region"].str.lower()
    return data

@st.cache_data
def convert_df(df):
    return df.to_csv(sep = ";").encode('utf-8')
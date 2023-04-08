import pandas as pd
import streamlit as st

@st.cache_data
def load():
    data = pd.read_feather("/Users/deevs/development/programming/AIML/tasks_2023/rlt_hack/RLTHack/streamlit_app/data/data.feather")
    return data
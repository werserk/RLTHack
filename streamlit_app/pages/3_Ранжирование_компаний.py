import streamlit as st
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool
import pickle
import utils
import plotly.express as px

def get_fi_plot():
    fi = pd.read_csv('/Users/deevs/development/programming/AIML/tasks_2023/rlt_hack/RLTHack/streamlit_app/data/feature_importance.csv', index_col='0')
    fi['1'] = np.log(fi['1'])
    fig = px.bar(fi.iloc[:10], y=fi.index[:10], x='1', labels={'y':'', '1':'Значение важности'}, 
             title='Топ 10 самых важных признаков при работе модели', color=fi.index[:10])
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    
    return fig

if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Загрузите список ИНН", type=['csv'])

with col2:
    number_of_cols = st.selectbox("Сколько строк выводить:", [5, 10, 15, 30, "Все"])

if uploaded_file is not None:
    try:
        inns = pd.read_csv(uploaded_file, sep=";")
        if "inn" not in inns.columns:
            st.warning("Не найдена колонка с ИНН (inn)")
        else:
            inns["inn"] = inns["inn"].astype(str)
            if number_of_cols == "Все":
                number_of_cols = len(inns)

            df = st.session_state["data"]
            missed_inns = set(inns["inn"]) - set(df["inn"])
            if missed_inns:
                st.warning(f"Данные ИНН не найдены в базе: {','.join(missed_inns)}")
            df = df[["inn", "score"]]
            df = df[df['inn'].isin(inns['inn'])]
            df = df.head(number_of_cols)
            df.set_index("inn", inplace = True)

            st.dataframe(df, use_container_width = True)

            st.download_button(
                label="Скачать",
                data=utils.convert_df(df),
                file_name='top_of_companies.csv',
                mime='text/csv',
            )

            st.plotly_chart(get_fi_plot())
    except pd.errors.ParserError:
        st.warning("Использован не тот раздилитель")
    except Exception:
        st.warning("Ошибка загрузки данных")
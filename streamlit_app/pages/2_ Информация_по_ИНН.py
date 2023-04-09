import streamlit as st
import pandas as pd
import utils
import plotly.express as px

def pieplot_builder(df):
    financial_columns_for_pieplot = ['inn', 'str_code_1400', 'str_code_1500', 'str_code_1600']
    pieplot = pd.DataFrame(df.loc[df[financial_columns_for_pieplot[1:]].values > 0, financial_columns_for_pieplot].iloc[0]).T
    pieplot = pd.melt(pieplot, 'inn')

    to_replace = {'str_code_1400':'Долгосрочные обязательства', 'str_code_1500': 'Краткосрочные обязательства', 'str_code_1600': 'Активы'}
    pieplot['variable'] = pieplot['variable'].replace(to_replace)

    fig = px.pie(pieplot, names='variable', values='value', color='variable', title='Обязательства и активы компании')
    return fig

def barplot_builder(df):
    financial_columns_for_barplot = ['inn', 'str_code_2100', 'str_code_2110', 'str_code_2200', 'str_code_2300', 'str_code_2400']
    barplot = pd.DataFrame(df.loc[df[financial_columns_for_barplot[1:]].values > 0, financial_columns_for_barplot].iloc[0]).T
    barplot = pd.melt(barplot, 'inn')

    to_replace = {'str_code_2100':'Валовая прибыль', 'str_code_2110': 'Выручка', 'str_code_2200': 'Прибыль от продаж',
                'str_code_2300': 'Прибыль до налогообложения', 'str_code_2400': 'Чистая прибыль'}
    barplot['variable'] = barplot['variable'].replace(to_replace)

    fig = px.bar(barplot, x='variable', y='value', color='variable', title='Доходы компании', labels={'value':'Значение тыс.руб.', 'variable': ''})
    return fig

if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

inn = st.text_input("Введите ИНН:")

if st.button('Найти информацию'):
    df = st.session_state["data"]
    company = df[df["inn"] == inn]

    if len(company) == 0:
        st.warning("Данный ИНН не найден в базе")
    else:
        who_dict = {
            0: "Юр. лицо",
            1: "Физ. лицо",
            -1: "ИП"
        }

        exp3 = st.expander("Основное")
        exp3.metric("Название компании",  company["name"].iloc[0])
        exp3.metric("Регион", company["region"].iloc[0])
        col11, col12, col13 = exp3.columns(3)
        col11.metric("Рейтинг доверия", round(company["score"], 2))
        col12.metric("Статус активности", "Закрыта" if company["termination"].iloc[0] else "Работает")
        col13.metric("Юридический статус", who_dict[company["is_entity_person"].iloc[0]])

        exp1 = st.expander("Финансовая информация")

        col1, col2, col3, col4 = exp1.columns(4)
        col1.metric("Выручка", company["str_code_2110"])
        col2.metric("Чистая прибыль", round(company["str_code_2400"], 2))
        col3.metric("Активы", round(company["str_code_1600"], 2))
        col4.metric("Задолжность", round(company["amount_due"], 2))
        col5, col6 = exp1.columns(2)
        col5.metric("Чистая маржа", round(company["net_margin"], 2))
        col6.metric("Ликвидность", round(company["current_liquid"], 2))

        exp1.plotly_chart(pieplot_builder(company))
        exp1.plotly_chart(barplot_builder(company))

        exp2 = st.expander("Тендерная статистика")
        col7, col8 = exp2.columns(2)
        col7.metric("Доля побед в тендерах по 44ФЗ", round(company["winrate_44fz"], 2))
        col8.metric("Доля побед в тендерах по 223ФЗ", round(company["winrate_223fz"], 2))
        col9, col10 = exp2.columns(2)
        col9.metric("Количество участий в тендерах по 44ФЗ", round(company["procedure_qty_44fz"], 2))
        col10.metric("Количество участий в тендерах по 223ФЗ", round(company["procedure_qty_223fz"], 2))
import streamlit as st
import pandas as pd
import utils
import plotly.express as px

st.set_page_config(layout="wide")

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

def format(value, is_float = False):
    if str(value) == "nan":
        value = "-"
        return value
    if is_float:
        return str(round(value, 2))
    else:
        return str(int(round(value, 2)))


if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

inn = st.text_input("Введите ИНН:")

if st.button('Найти информацию'):
    df = st.session_state["data"]
    company = df[df["inn"] == inn]

    if len(company) == 0:
        st.warning("Данный ИНН не найден в базе")
    else:
        exp3 = st.expander("Основное")
        exp3.metric("Название компании",  company["name"].iloc[0])
        exp3.metric("Регион", company["region"].iloc[0])
        col16, col17 = exp3.columns(2)
        col16.metric("Рейтинг доверия", round(company["score"], 2))
        col17.metric("Статус активности", "Закрыта" if company["termination"].iloc[0] else "Работает")

        exp1 = st.expander("Финансовая информация")

        col1, col2, col3, col4 = exp1.columns(4)
        col1.metric("Выручка (тыс. ₽)", format(company["str_code_2110"].iloc[0]))
        col2.metric("Чистая прибыль (тыс. ₽)", format(company["str_code_2400"].iloc[0]))
        col3.metric("Активы (тыс. ₽)", format(company["str_code_1600"].iloc[0]))
        col4.metric("Задолжность (тыс. ₽)",format(company["amount_due"].iloc[0]))
        col5, col6 = exp1.columns(2)
        col5.metric("Чистая маржа", str(round(company["net_margin"].iloc[0] * 100, 2)) + "%")
        col6.metric("Ликвидность", format(company["current_liquid"].iloc[0], True))

        exp1.plotly_chart(pieplot_builder(company))
        exp1.plotly_chart(barplot_builder(company))

        exp2 = st.expander("Тендерная статистика")
        col7, col8, col9 = exp2.columns(3)
        col7.metric("Доля побед в тендерах по 44ФЗ", round(company["winrate_44fz"].iloc[0], 2))
        col8.metric("Доля побед в тендерах по 223ФЗ", round(company["winrate_223fz"].iloc[0], 2))
        col9.metric("Доля побед в тендерах", round(company["winrate_full"].iloc[0], 2))
        col10, col11, col12 = exp2.columns(3)
        col10.metric("Количество участий в тендерах по 44ФЗ", round(company["procedure_qty_44fz"].iloc[0], 2))
        col11.metric("Количество участий в тендерах по 223ФЗ", round(company["procedure_qty_223fz"].iloc[0], 2))
        col12.metric("Количество участий", round(company["procedure_qty_full"].iloc[0], 2))
        col13, col14, col15 = exp2.columns(3)
        col13.metric("Количество побед в тендерах по 44ФЗ", round(company["win_qty_44fz"].iloc[0], 2))
        col14.metric("Количество побед в тендерах по 223ФЗ", round(company["win_qty_223fz"].iloc[0], 2))
        col15.metric("Количество побед", round(company["win_qty_full"].iloc[0], 2))
        
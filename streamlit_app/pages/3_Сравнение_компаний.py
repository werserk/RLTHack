import streamlit as st
import pandas as pd
import utils
import plotly.express as px

def plot_winrate_44fz_builder(df):
    df['winrate_44fz'] = df['win_qty_44fz']/df['procedure_qty_44fz']
    df = df.fillna(0)
    df["inn"] = df["inn"].astype(str) + "_"

    winrate44_df = df[['inn', 'winrate_44fz', 'win_qty_44fz', 'procedure_qty_44fz']].copy()

    fig = px.bar(winrate44_df.sort_values('winrate_44fz', ascending=False), x='inn', y='winrate_44fz', hover_data=['win_qty_44fz', 'procedure_qty_44fz'],
                title='Процент выигранных тендеров для каждого ИНН по 44 федеральному закону', color='inn', 
                labels={'inn':'ИНН', 'winrate_44fz':'Процент побед в тендерах', 'win_qty_44fz':'Количество побед в тендерах',
                        'procedure_qty_44fz':'Количество участий в тендерах'})
    fig.update_xaxes(tickangle=45)
    return fig

def plot_winrate_223fz_builder(df):
    df['winrate_223fz'] = df['win_qty_223fz']/df['procedure_qty_223fz']
    df = df.fillna(0)
    df["inn"] = df["inn"].astype(str) + "_"

    print(df.info())

    winrate223_df = df[['inn', 'winrate_223fz', 'win_qty_223fz', 'procedure_qty_223fz']].copy()

    fig = px.bar(winrate223_df.sort_values('winrate_223fz', ascending=False), x='inn', y='winrate_223fz', hover_data=['win_qty_223fz', 'procedure_qty_223fz'],
                title='Процент выигранных тендеров для каждого ИНН по 223 федеральному закону', color='inn', 
                labels={'inn':'ИНН', 'winrate_223fz':'Процент побед в тендерах', 'win_qty_223fz':'Количество побед в тендерах',
                        'procedure_qty_223fz':'Количество участий в тендерах'})
    fig.update_xaxes(tickangle=45)
    return fig

def plot_contract_success(df):
    df["supplier_inn"] = df["supplier_inn"].astype(str) + "_"
    fig = px.bar(df.sort_values('termination', ascending=False), x='supplier_inn', y='termination',
             title='Количество успешно выполненных заказов для каждого ИНН', color='supplier_inn', 
             labels={'supplier_inn':'ИНН', 'termination':'Количество успешно выполненных заказов'})
    fig.update_xaxes(tickangle=45)
    return fig

if "data" not in st.session_state:
    st.session_state["data"] = utils.load()

contract_success = pd.read_feather("/Users/deevs/development/programming/AIML/tasks_2023/rlt_hack/RLTHack/streamlit_app/data/contract_success.feather")

uploaded_file = st.file_uploader("Загрузите список ИНН")

if uploaded_file is not None:
    inns = pd.read_csv(uploaded_file)
    inns["inn"] = inns["inn"].astype(str)

    df = st.session_state["data"]
    missed_inns = set(inns["inn"]) - set(df["inn"])
    if missed_inns:
        st.warning(f"Данные ИНН не найдены в базе: {','.join(missed_inns)}")
    df = df[df['inn'].isin(inns['inn'])]

    df_to_show = df[["inn", "termination", "is_entity_person", "score", "str_code_2110", "str_code_2400", "str_code_1600", "amount_due", "net_margin", "current_liquid", "winrate_44fz", "winrate_223fz", "procedure_qty_44fz", "procedure_qty_223fz"]]
    rename_dict = {
        "inn": "ИНН",
        "termination": "Статус активности",
        "is_entity_person": "Юридический статус",
        "score": "Рейтинг доверия",
        "str_code_2110": "Выручка",
        "str_code_2400": "Чистая прибыль",
        "str_code_1600": "Активы",
        "amount_due": "Задолжность",
        "net_margin": "Чистая маржа",
        "current_liquid": "Ликвидность",
        "winrate_44fz": "Доля побед в тендерах по 44ФЗ",
        "winrate_223fz": "Доля побед в тендерах по 223ФЗ",
        "procedure_qty_44fz": "Количество участий в тендерах по 44ФЗ",
        "procedure_qty_223fz": "Количество участий в тендерах по 223ФЗ"
    }
    df_to_show = df_to_show.rename(columns = rename_dict)
    df_to_show["Статус активности"] = df_to_show["Статус активности"].apply(lambda x: "Закрыта" if x else "Работает")
    who_dict = {
        0: "Юр. лицо",
        1: "Физ. лицо",
        -1: "ИП"
    }
    df_to_show["Юридический статус"] = df_to_show["Юридический статус"].apply(lambda x: who_dict[x])

    st.dataframe(df_to_show, use_container_width = True)

    st.plotly_chart(plot_winrate_44fz_builder(df))
    st.plotly_chart(plot_winrate_223fz_builder(df))
    st.plotly_chart(plot_contract_success(contract_success[contract_success["supplier_inn"].isin(inns["inn"])]))

    st.download_button(
        label="Скачать",
        data=utils.convert_df(df),
        file_name='comapines_comparison.csv',
        mime='text/csv',
    )
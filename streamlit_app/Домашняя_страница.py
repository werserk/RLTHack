import streamlit as st
import pandas as pd
import numpy as np
import glob
import os
from typing import Union
import copy
from datetime import datetime
from omegaconf import OmegaConf
import utils



def main():
    st.set_page_config(layout="wide")
    data = utils.load()
    if "data" not in st.session_state:
        st.session_state["data"] = data
    st.markdown("""
    ### Бизнес-око
    Практичное решение для анализа и оценки участников рынка закупок! Здесь вы найдете инструменты, которые помогут вам принимать обоснованные решения и снижать риски при выборе контрагентов.

    ##### 🔍 Анализ одного участника: 
    Введите ИНН и получите информацию о финансовых показателях, деятельности и репутации компании, чтобы определить надежных партнеров для вашего бизнеса.

    ##### 📊 Сравнительный анализ: 
    Загрузите список ИНН и сравните участников по ключевым показателям, чтобы выбрать лучшие возможности для сотрудничества и максимизировать выгоду от заключаемых контрактов.

    ##### 🏆 Система ранжирования: 
    Оцените рейтинг и надежность участников с помощью нашей модели машинного обучения. Разместите список ИНН и получите отранжированный список контрагентов в порядке убывания репутации, чтобы улучшить ваш процесс выбора партнеров.

    *Используйте нашу интеллектуальную систему анализа участников рынка закупок для расширения возможностей вашего бизнеса. Начните прямо сейчас и убедитесь в практичности нашего инструмента!*
    """)

if __name__ == '__main__':
    main()
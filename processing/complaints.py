# --- Жалобы ---

from typing import Dict, Union

import pandas as pd

from base import DataObj


def transform_complaints_to_df(complaints_dict: Dict, inn: int) -> pd.DataFrame:
    """Перевести словарь в pandas строку."""
    data = [inn]
    labels = ["inn"]
    for role in complaints_dict:
        role_dict = complaints_dict[role]
        for status in role_dict:
            if status == 'Рассмотрена':
                for result in role_dict[status]:
                    data.append(role_dict[status][result])
                    labels.append(f"{role} | {result}")
            else:
                data.append(role_dict[status])
                labels.append(f"{role} | {status}")
    df = pd.DataFrame(data=[data],
                      columns=labels)
    return df


def calculate_numbers_per_role(db: DataObj, df: pd.DataFrame) -> Dict[str, Union[Dict[str, int], int]]:
    """Посчитать статистику по жалобам для роли: поставщик или заказчик"""
    result = {}
    for status in db.data['complaint_info']['status'].unique():
        result[status] = {}
        status_df = df.loc[df['status'] == status]
        if status == 'Рассмотрена':
            for processing_result in ['Признана обоснованной', 'Признана обоснованной (частично)', 'Признана необоснованной']:
                result[status][processing_result] = len(status_df.loc[status_df['processing_result'] == processing_result])
        else:
            result[status] = len(status_df)
    result['Всего жалоб'] = len(df)  # Общее количество поданных жалоб
    return result


def get_numbers_of_complaints(db: DataObj, inn: int, get_row: bool = False) -> Union[Dict[str, Dict[str, Union[Dict[str, int], int]]], pd.DataFrame]:
    """
    Получить общее количество жалоб и одобренных жалоб в ситуациях, где ИНН был поставщиком и заказчиком.
    :param db: Вся БД
    :param inn: ИНН для получения информации
    :param get_row: перевести ли в строку pandas
    :return: Словарь или строка с информацией об ИНН в жалобах (как поставщик или как закупщик)
    """
    assert inn in db.data['inn_list']['inn'].values, "ИНН не существует в БД"
    contract_df = db.data['contract_main_info']  # Таблица контрактов
    customer_contracts = contract_df.loc[contract_df['customer_inn'] == inn]  # Таблица в каких контрактах был заказчиком
    supplier_contracts = contract_df.loc[contract_df['supplier_inn'] == inn]  # Таблица в каких контрактах был поставщиком
    customer_complaints = pd.merge(customer_contracts, db.data['complaint_info'])  # Таблица жалоб как на заказчика
    supplier_complaints = pd.merge(supplier_contracts, db.data['complaint_info'])  # Таблица жалоб как от поставщика
    result = {'as_customer': {},
              'as_supplier': {}}
    for role, df in zip(result, (customer_complaints, supplier_complaints)):
        result[role] = calculate_numbers_per_role(db, df)
    if not get_row:
        return result
    row = transform_complaints_to_df(result, inn)
    row = row.set_index("inn")
    return row


def main():
    full_data = DataObj('../data')
    result = get_numbers_of_complaints(full_data, inn=5908078473, get_row=False)
    print(result)


if __name__ == '__main__':
    main()

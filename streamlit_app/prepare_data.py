import pandas as pd
import numpy as np
import glob
import os
from typing import Union
import copy
from datetime import datetime
from omegaconf import OmegaConf
import pickle
import catboost as cb


class DataObj:
    def __init__(self, data_path: Union[str, os.PathLike]):
        csv_paths = glob.glob(os.path.join(data_path, "**", "*.csv"))
        self.data = {os.path.basename(path).split('.')[0]: pd.read_csv(path, sep=';') for path in csv_paths}
        desc = pd.read_excel(glob.glob(os.path.join(data_path, "*.xlsx"))[0], sheet_name=None)
        desc.pop('Перечень файлов')
        self.desc = {key.split('.')[1]: desc[key] for key in desc}
        assert self.data.keys() == self.desc.keys(), "Keys must be equal"
        assert len(self.data.keys()) == 26, "Keys length must equals 26"
        self._keys = list(self.desc.keys())
        self._len = len(self._keys)

    def keys(self):
        return self._keys

    def __len__(self):
        return self._len

    def __getitem__(self, idx):
        return self._keys[idx]

def str_value2int(x):
    x = str(x)
    if '-' in x:
        return 0
    elif x == 'nan':
        return 0
    elif x.startswith('(') and x.endswith(')'):
        return -int(x[1:-1])
    else:
        try:
            return int(x)
        except:
            return 0

def get_egrul_features(full_data):
    egrul_info = copy.deepcopy(full_data.data["egrul_info"])
    egrul_info["termination"] = ~egrul_info["termination_date"].isna()
    egrul_info["is_entity_person"] = egrul_info["entity_wo_attorney_type"] == "Физическое лицо"
    egrul_info["delta_days"] = (datetime.today() - pd.to_datetime(egrul_info["registration_date"])).dt.days
    egrul_info = egrul_info[["inn", "termination", "is_entity_person", "okved_basic_code", "delta_days", "has_filial", "capital_size"]]
    return egrul_info.set_index("inn")

def get_participation_features(full_data):
    df = copy.deepcopy(full_data.data["participation_statistic"])
    df = df.pivot_table(index='participant_inn',
                        columns='fz', values=['procedure_qty', 'win_qty'],
                        aggfunc='sum', fill_value=0)
    df.columns = ["_".join(col) for col in df.columns]
    df.index.names = ["inn"]
    return df

def get_bo_pivot(df, config):
    df = df.loc[df["str_code"].isin(config.data.financial_codes), ["inn", "str_code", "str_value"]]\
        .groupby(["inn", "str_code"]).agg(["sum"])["str_value"]
    df = df.reset_index()
    pivot_df = df.pivot_table(index='inn', columns='str_code', values='sum', aggfunc='sum', fill_value=0)
    pivot_df.columns = [f'str_code_{col}' for col in pivot_df.columns]
    return pivot_df


def get_financial_features(df):
    # Коэффициент текущей ликвидности
    df["current_liquid"] = df["str_code_1200"] / (df["str_code_1400"] + df["str_code_1500"])
    
    # Коэффициент быстрой ликвидности
    df["quick_liquid"] = (df["str_code_1250"] + df["str_code_1230"]) / (df["str_code_1400"] + df["str_code_1500"])
    
    # Валовая маржа
    df["gross_margin"] = df["str_code_2100"] / df["str_code_2110"]
    
    # Операционная маржа
    df["operating_margin"] = df["str_code_2200"] / df["str_code_2110"]
    
    # Маржа по прибыли до налогообложения
    df["profit_before_tax_margin"] = df["str_code_2300"] / df["str_code_2110"]
    
    # Чистая маржа
    df["net_margin"] = df["str_code_2400"] / df["str_code_2110"]
    
    # Коэффициент задолженности
    df["debt_ratio"] = (df["str_code_1400"] + df["str_code_1500"]) / df["str_code_1600"]
    
    # Фондоотдача
    df["asset_turnover"] = df["str_code_2110"] / df["str_code_1150"]
    
    return df

def get_contract_main_info_features(full_data):
    df = copy.deepcopy(full_data.data["contract_main_info"])\
                       .merge(copy.deepcopy(full_data.data["contract_termination"]), how="left", on="id_contract")
    df["is_termination"] = ~df["t_termination_date"].isna()
    
    info1 = df[["id_contract", "supplier_inn"]].groupby("supplier_inn").agg("count")
    info2 = df[["contract_price_rub", "supplier_inn", "is_termination"]].groupby("supplier_inn").agg("sum")
    
    info = pd.concat([info1, info2], axis=1)
    info.index.names = ["inn"]
    
    t = df[["supplier_inn", "t_reason_name", "id_contract"]].groupby(["supplier_inn", "t_reason_name"]).agg(["count"])["id_contract"]
    t = t.reset_index()
    t = t.pivot_table(index='supplier_inn',
                      columns='t_reason_name', values="count",
                      aggfunc='sum', fill_value=0)
    t.index.names = ["inn"]
    return pd.concat([info, t], axis=1)

def get_egrip_features(full_data):
    egrip_info = copy.deepcopy(full_data.data["egrip_info"])
    egrip_info["is_entity_person"] = -1
    return egrip_info[["inn", "okved_basic_code"]].set_index("inn")

def get_complaint_features(full_data):
    df = copy.deepcopy(full_data.data["contract_main_info"])\
            .merge(copy.deepcopy(full_data.data["complaint_info"]),
                   how="inner", on="id_procedure")
    df = df[["supplier_inn", "status", "id_procedure"]].groupby(["supplier_inn", "status"]).agg(["count"])
    df.columns = ["_".join(col) for col in df.columns]
    df = df.reset_index()
    df = df.pivot_table(index='supplier_inn',
                        columns='status', values="id_procedure_count",
                        aggfunc='sum', fill_value=0)
    df.index.names = ["inn"]
    return df

def get_bo_features(full_data, config):
    bo_balance = copy.deepcopy(full_data.data["bo_balance"]) # бухгалтерский баланс
    bo_financial_results = copy.deepcopy(full_data.data["bo_financial_results"]) # отчет о финансовых результатах
    bo = pd.concat([bo_balance, bo_financial_results])
    bo["str_value"] = bo["str_value"].apply(str_value2int)
    bo["str_code"] = bo["str_code"].apply(lambda x: int(str(x).replace("*", "")))

    bo_pivot = get_bo_pivot(bo, config)
    bo_pivot = get_financial_features(bo_pivot)
    return bo_pivot

def get_fssp_enforcement_proceedings_features(full_data):
    fssp_enforcement_proceedings = copy.deepcopy(full_data.data["fssp_enforcement_proceedings"])
    fssp_enforcement_proceedings = fssp_enforcement_proceedings[["debtor_inn", "amount_due"]].groupby("debtor_inn").agg("sum")
    fssp_enforcement_proceedings.index.names = ["inn"]
    return fssp_enforcement_proceedings

def get_rnp_features(full_data):
    rnp = copy.deepcopy(full_data.data["rnp"])
    rnp = rnp[["inn", "rnp_supplier_reg_number"]].groupby("inn").agg("count")
    rnp = rnp.rename({"rnp_supplier_reg_number": "rnp_count"}, axis=1)
    return rnp

def get_avg_staff_qty_features(full_data):
    return full_data.data["avg_staff_qty"].set_index("inn")

def catboost_info(df):
    df['termination'] = df['termination'].fillna(False)
    df['capital_size'] = df['capital_size'].fillna(0)
    df.capital_size = df.capital_size.apply(lambda x: 0 if isinstance(x, str) else x) 
    df['has_filial'] = df['has_filial'].astype(bool)
    df['is_entity_person'] = df['is_entity_person'].fillna(-1).astype(int)
    return df


def get_contract_main_info_features_positive(full_data):
    df = copy.deepcopy(full_data.data["contract_main_info"]).merge(copy.deepcopy(full_data.data["contract_termination"]), how="left", on="id_contract")
    df["termination"] = df["t_termination_date"].isna()
    info = df[["termination", "supplier_inn"]].groupby("supplier_inn").agg("sum")
    return info["termination"]


def prepare_full_from_config(config):
    full_data = DataObj(config.paths.csv_path)

    full_data.data["contract_main_info"] = full_data.data["contract_main_info"].dropna(subset=["supplier_inn"])
    full_data.data["contract_main_info"]["supplier_inn"] = full_data.data["contract_main_info"]["supplier_inn"].astype(np.int64)

    bo_features = get_bo_features(full_data, config)
    egrul_features = get_egrul_features(full_data)
    participation_features = get_participation_features(full_data)
    contract_main_info_features = get_contract_main_info_features(full_data)
    egrip_features = get_egrip_features(full_data)
    complaint_features = get_complaint_features(full_data)
    avg_staff_qty_features = get_avg_staff_qty_features(full_data)
    fssp_enforcement_proceedings_features = get_fssp_enforcement_proceedings_features(full_data)
    rnp_features = get_rnp_features(full_data)
    egrul_egrip_features = pd.concat([egrul_features, egrip_features])
    
    final_df = pd.concat([bo_features, contract_main_info_features,
                        participation_features, egrul_egrip_features,
                        complaint_features, avg_staff_qty_features,
                        fssp_enforcement_proceedings_features,
                        rnp_features], axis=1)

    final_df = final_df.reset_index()
    final_df = final_df[final_df["inn"].isin(full_data.data["inn_list"]["inn"])]
    final_df = final_df.reset_index(drop=True)

    final_df = catboost_info(final_df)
    final_df['inn'] = final_df['inn'].astype(int).astype(str)

    contract_success = get_contract_main_info_features_positive(full_data).reset_index()
    contract_success['supplier_inn'] = contract_success['supplier_inn'].astype(int).astype(str)
    contract_success = contract_success[contract_success['supplier_inn'].isin(final_df['inn'].unique())]

    return final_df, contract_success

def ranking(df):
    with open('./models_with_threshes.pkl', 'rb') as f:
        models, _ = pickle.load(f)

        test = cb.Pool(
            data=df.drop(columns=['id_contract', 'inn']).fillna(0),
            cat_features=['okved_basic_code']
        )

        res = np.zeros(len(df))
        for model in models:
            res += model.predict_proba(test)[:, 1]
        res /= 5
    return res.tolist()

def get_external_data():
    ergip_union_inns = pd.read_csv("./data/ergip_union_inns.csv").drop_duplicates().replace("none", np.nan)
    ergul_union_inns = pd.read_csv("./data/ergul_union_inns.csv").drop_duplicates().replace("none", np.nan)
    
    ergip_union_inns["inn"] = ergip_union_inns["inn"].astype(np.int64).astype(str)
    ergul_union_inns["inn"] = ergul_union_inns["inn"].astype(np.int64).astype(str)
    
    ergip_union_inns = ergip_union_inns.groupby("inn").agg(lambda x: list(x)[-1]).reset_index()
    ergul_union_inns = ergul_union_inns.groupby("inn").agg(lambda x: list(x)[-1]).reset_index()
    
    eg_info = pd.concat([ergip_union_inns, ergul_union_inns])
    return eg_info


config = {
    
    'paths':{
        'csv_path': './data',
    },
    
    'data':{
        'use_financial_features': True,
        'financial_codes': [1200, 1400, 1500, 1250, 1230, 2100, 2110, 2200, 2300, 2400, 1600, 1150],
        
        'use_complaint_features': True,
        'use_contract_features': True,
        'use_other_features': True,
        
        'cat_features': ['okved_basic_code_x', 'okved_basic_code_y']
    },
    
}

config = OmegaConf.create(config)

final_df, contract_success = prepare_full_from_config(config)
final_df["prediction"] = ranking(final_df)
final_df['winrate_44fz'] = (final_df['win_qty_44fz']/final_df['procedure_qty_44fz']).fillna(0)
final_df['winrate_223fz'] = (final_df['win_qty_223fz']/final_df['procedure_qty_223fz']).fillna(0)
final_df["notna"] = final_df.notna().sum(axis=1) / len(final_df.columns)
final_df['delta_days_norm'] = (final_df['delta_days'] / final_df['delta_days'].mean()).clip(0, 1).fillna(0.1)
# final_df["termination_coef"] = (final_df["is_termination"] / final_df["id_contract"]).fillna(0.5)
final_df["score"] = final_df["prediction"] * final_df["notna"] * ((final_df["winrate_44fz"] \
                            + final_df["winrate_223fz"]) / 2) * final_df['delta_days_norm']
eg_info = get_external_data()
final_df = final_df.merge(eg_info, how="left", on="inn")
final_df = final_df.sort_values(by="score", ascending=False)
final_df = final_df.reset_index(drop=True)
contract_success = contract_success.reset_index()

final_df['inn'] = final_df['inn'].astype(str)

final_df.to_feather("data/data.feather")
contract_success.to_feather("data/contract_success.feather")



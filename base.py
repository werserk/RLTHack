import glob
import os

import pandas as pd
from tqdm.notebook import tqdm


class BaseDataFrame:
    def __init__(self, data_path):
        csv_paths = glob.glob(os.path.join(data_path, "**", "*.csv"))
        self.data = {os.path.basename(path).split('.')[0]: pd.read_csv(path, sep=';') for path in tqdm(csv_paths)}
        desc = pd.read_excel(glob.glob(os.path.join(data_path, "*.xlsx"))[0], sheet_name=None)
        desc.pop('Перечень файлов')
        self.desc = {key.split('.')[1]: desc[key] for key in desc}
        assert self.data.keys() == self.desc.keys(), "Keys must be equal"

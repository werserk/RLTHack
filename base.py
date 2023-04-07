import glob
import os
from typing import Union

import pandas as pd
from tqdm.notebook import tqdm


class DataObj:
    def __init__(self, data_path: Union[str, os.PathLike]):
        csv_paths = glob.glob(os.path.join(data_path, "**", "*.csv"))
        self.data = {os.path.basename(path).split('.')[0]: pd.read_csv(path, sep=';') for path in tqdm(csv_paths)}
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


def main():
    data = DataObj('data')
    print(data.desc.keys())


if __name__ == '__main__':
    main()

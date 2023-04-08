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

if __name__ == '__main__':
    main()
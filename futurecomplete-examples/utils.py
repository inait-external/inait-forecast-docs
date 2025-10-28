from inait_forecasting_client import read_file
import pandas as pd


def clean(data):
    return data.asfreq("B", method="ffill")  # api fails with C freq


def filter_by_target(data, target="AAPL"):
    return data.filter(like="AAPL")


def read_sp100_vola():
    data = read_file("../data/dataset_GKYZ_2016.csv", index_col=0)
    data.index = pd.to_datetime(data.index)
    data_clean = clean(data)
    targets = [col.split("__")[0] for col in data.filter(like="__hl").columns]
    return data_clean, targets


def read_aapl_vola():
    try:
        data = read_file("../data/dataset_GKYZ_2016_AAPL.csv", index_col=0)
        data.index = pd.to_datetime(data.index)
        data_aapl = clean(data)

    except FileNotFoundError:
        data = read_file("../data/dataset_GKYZ_2016.csv", index_col=0)
        data.index = pd.to_datetime(data.index)
        data_clean = clean(data)
        data_aapl = filter_by_target(data_clean)
    return data_aapl

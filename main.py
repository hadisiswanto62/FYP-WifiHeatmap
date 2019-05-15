# This code is used to create heatmap and csv data from the wifi scan data

from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
def save_output(df: pd.DataFrame, relevant_mac_addr_map:dict, method: str) -> None:
    df = df.pivot(index="mac_addr", columns="location", values="signal_str")
    filepath = f"{method} - All APs"
    df.to_csv(CSV_OUTPUT_FOLDER / f'{filepath}.csv')
    sns.heatmap(df, annot=True)
    plt.title(f"{method} - RSSI of ALL APs")
    plt.savefig(HEATMAP_OUTPUT_FOLDER / f'{filepath}.png', bbox_inches="tight")
    plt.clf()

    df.dropna(axis=0, inplace=True)
    filepath = f"{method} - Non-NaN APs"
    df.to_csv(CSV_OUTPUT_FOLDER / f'{filepath}.csv')
    sns.heatmap(df, annot=True)
    plt.title(f"{method} - RSSI of all Non-NaN APs")
    plt.savefig(HEATMAP_OUTPUT_FOLDER / f'{filepath}.png', bbox_inches="tight")
    plt.clf()

    df = df[df.index.isin(relevant_mac_addr_map.keys())]
    df = df.rename(index=relevant_mac_addr_map)
    df = df.sort_values('mac_addr')
    filepath = f"{method} - Relevant APs"
    df.to_csv(CSV_OUTPUT_FOLDER / f'{filepath}.csv')
    sns.heatmap(df, annot=True)
    plt.title(f"{method} - RSSI of Relevant APs")
    plt.savefig(HEATMAP_OUTPUT_FOLDER / f'{filepath}.png', bbox_inches="tight")
    plt.clf()

def add_to_or_create_df(source: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    if target is None:
        return source
    return target.append(source)

def process_df(df: pd.DataFrame, method: str) -> pd.DataFrame:
    final = None
    i = 0
    for group in df:
        mac_addr, actual_data = group
        processed_value = 0

        if method == "MEAN":
            processed_value = actual_data.mean().values
        elif method == "MEDIAN":
            processed_value = actual_data.median().values
        elif method == "CENTERED_MEAN":
            actual_data = actual_data.sort_values(by="signal_str")
            if len(actual_data) > 2:
                actual_data = actual_data[1:-1]
            processed_value = actual_data.mean().values
        elif method == "STANDARD_DEVIATION":
            processed_value = actual_data.std().values

        row_df = pd.DataFrame({
            "mac_addr": mac_addr,
            "signal_str": processed_value
        }, index=[i])
        final = add_to_or_create_df(row_df, final)
        i += 1
    return final

DATA_FOLDER = Path("data") / "csv"
PROCESSED_FOLDER = Path("processed_data")
OUTPUT_FOLDER = Path("output")
CSV_OUTPUT_FOLDER = OUTPUT_FOLDER / "CSV"
HEATMAP_OUTPUT_FOLDER = OUTPUT_FOLDER / "heatmap"
#FILE_LIST = [DATA_FOLDER / "loc1a.csv"]
FILE_LIST = list(DATA_FOLDER.iterdir())
ROUTER_DATA_FILE_LIST = list(Path("misc_data/under_router_data").iterdir())

method_list = [
    "MEAN",
    "MEDIAN",
    "CENTERED_MEAN",
]

for method in method_list:
    relevant_mac_addr_map = {}
    for file in ROUTER_DATA_FILE_LIST:
        df = pd.read_csv(file, delimiter=",")
        df = df.groupby(["mac_addr"], as_index=False)
        df = process_df(df, method=method)
        mac_with_max_mean = df.loc[df["signal_str"].idxmax()]["mac_addr"]
        router_name = file.name[:file.name.find('.')]
        relevant_mac_addr_map[mac_with_max_mean] = router_name

    processed_df = None
    for file in FILE_LIST:
        df = pd.read_csv(file, delimiter=",")
        df = df.groupby(["mac_addr"], as_index=False)
        df = process_df(df, method=method)
        #TODO: Fix this hax. Will error if there is >9 locations (currently only 6)
        df["location"] = file.name[:4]
        processed_df = add_to_or_create_df(source=df, target=processed_df)

    save_output(processed_df, relevant_mac_addr_map, method)
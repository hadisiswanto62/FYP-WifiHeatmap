# Same as main.py but for data under router. Too lazy to combinethem >_>

from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def save_output(df: pd.DataFrame, method: str) -> None:
    df = df.pivot(index="mac_addr", columns="location", values="signal_str")
    sns.heatmap(df, annot=True)
    plt.title(f"1{method} - RSSI of ALL APs (from under router)")
    plt.savefig(HEATMAP_OUTPUT_FOLDER / f"{method} - Router data - All APs.png", bbox_inches="tight")
    plt.clf()

    df.dropna(axis=0, inplace=True)
    sns.heatmap(df, annot=True)
    plt.title(f"2{method} - RSSI of all Non-NaN APs (from under router)")
    plt.savefig(HEATMAP_OUTPUT_FOLDER / f"{method} - Router data - Non-Nan APs.png", bbox_inches="tight")
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

        row_df = pd.DataFrame({
            "mac_addr": mac_addr,
            "signal_str": processed_value
        }, index=[i])
        final = add_to_or_create_df(row_df, final)
        i += 1
    return final

OUTPUT_FOLDER = Path("output")
ROUTER_DATA_FILE_LIST = list(Path("misc_data/under_router_data").iterdir())
HEATMAP_OUTPUT_FOLDER = OUTPUT_FOLDER / "heatmap"

method_list = [
    "MEAN",
    "MEDIAN",
    "CENTERED_MEAN"
]

for method in method_list:
    processed_df = None
    for file in ROUTER_DATA_FILE_LIST:
        df = pd.read_csv(file, delimiter=",")
        df = df.groupby(["mac_addr"], as_index=False)
        df = process_df(df, method=method)
        #TODO: Fix this hax. Will error if there is >9 locations (currently only 6)
        df["location"] = file.name[:file.name.find('.')]
        processed_df = add_to_or_create_df(source=df, target=processed_df)
    save_output(processed_df, method)
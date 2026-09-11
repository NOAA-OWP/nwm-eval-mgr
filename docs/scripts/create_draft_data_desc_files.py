"""Create draft data description CSV files for inputs and outputs.

The draft CSV files include the column names extracted from sample Parquet files for each dataset,
along with a sample file path and a description of the dataset. These draft CSV files can then be manually updated to
add descriptions for each column, which will be used to generate RST files for the documentation, using `data_schemas.py`.
"""

from pathlib import Path

import pandas as pd

from nwm_eval.utils import read_data

# output files
dir1 = "~/repos/nwm-eval-mgr/data/outputs"

files = {
    "metrics": "calib_basin_group1/metrics/v3_oct.nwm30.short_range.metrics.parquet",
    "pairs": "calib_basin_group1/joined/v3_oct.nwm30.short_range.joined.parquet",
    "forecast_data": "calib_basin_group1/v3_oct/short_range/20241001T00.parquet",
    "obs_data": "calib_basin_group1/usgs/2024-10-01.parquet",
}

files_desc = {
    "metrics": "Metrics computed for a given NWM dataset (here defined by forecast time period, NWM version and configuration, e.g., v3_oct.nwm30.short_range)",
    "pairs": "Paired data for a given NWM dataset (here defined by forecast time period, NWM version and configuration, e.g., v3_oct.nwm30.short_range), which includes the forecasted and observed values for each location and time step.",
    "forecast_data": "Raw forecast data for a given NWM dataset (here defined by forecast time period, NWM version and configuration, e.g., v3_oct.nwm30.short_range), which includes the forecasted values for all locations and time steps.",
    "obs_data": "Observation data, which includes the observed values for all locations and time steps.",
}

output_dir = Path("docs/scripts/data_desc/outputs")
output_dir.mkdir(exist_ok=True)

for key, file in files.items():
    path1 = Path(dir1).expanduser() / file

    df1 = read_data(path1)

    out_csv = output_dir / f"{key}.csv"

    df = pd.DataFrame({"column_name": df1.columns + "|"})

    # add two rows at the top for file path and description
    df.loc[-2] = [f"sample_file_path|{file}"]  # add file path as the first row
    df.loc[-1] = [f"title|{files_desc[key]}"]  # add description as the second row
    df.index = df.index + 2  # shift the index to start from 0
    df = df.sort_index()  # sort by index to ensure the new rows are at the top
    df.to_csv(
        out_csv,
        index=False,
        header=False,
    )

    print(f"Wrote {out_csv}")

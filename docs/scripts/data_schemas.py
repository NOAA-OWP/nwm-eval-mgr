"""Generate data description CSVs and RST schema files for input and output data.

This script supports two steps (default is ``--step schema``):

1. ``--step draft``:
   Read configured sample files from S3, extract column names, and create draft
   data description CSV files under ``docs/scripts/data_desc/inputs`` and
   ``docs/scripts/data_desc/outputs``. The draft files can then be manually
   updated with dataset and column descriptions.

2. ``--step schema``:
   Read the sample files from S3 together with the manually populated data
   description CSVs and generate ``input_data.rst`` and ``output_data.rst``
   under ``docs/source/tech_reference``.

The schema files are generated from sample CSV, Parquet, GPKG, and GDB files.

Here is the workflow:

--step draft
    ├── existing CSV → skip
    ├── missing CSV  → read S3 → create draft
    └── missing CSV  → read S3 → create draft

manual editing

--step schema
    ├── read CSV descriptions
    ├── read S3 sample
    └── generate RST

Before running the script, ensure AWS credentials are available in the
environment or in a ``.env`` file.

"""

import argparse
import csv
import os
import re
import tempfile
from io import BytesIO
from pathlib import Path
from pprint import pprint

import boto3
import fiona
import geopandas as gpd
import pandas as pd
import xarray as xr
from dotenv import load_dotenv

DIR_DATA_DESC = Path(__file__).resolve().parent / "data_desc"
DIR_TECH_REFERENCE = Path(__file__).resolve().parent.parent / "source/tech_reference"

# ---------------------------------------------------------------------------
# Sample input and output datasets used to create draft description files.
#
# Add new datasets here as needed. The values are S3 keys relative to the
# command-line --prefix.
#
# ---------------------------------------------------------------------------

DATASET_DEFINITIONS = {
    "inputs": {
        "gage_crosswalk": {
            "sample_file_path": "inputs/eval/usgs_ngen_crosswalk_conus.parquet",
            "title": "Crosswalk between USGS gages and NextGen catchments for the CONUS domain.",
        },
        "troute_output": {
            "sample_file_path": "outputs/ngen/regionalization/test_kmeans/vpu_03S/Output/troute_output_201210010000.nc",
            "title": "Troute output for the given configuration.",
        },
    },
    "outputs": {
        "metrics": {
            "sample_file_path": (
                "outputs/eval/vpu_03S/metrics/test_kmeans.ngen.ngen_simulation.metrics.parquet"
            ),
            "title": ("Metrics computed for a given dataset (e.g., test_kmeans)"),
        },
        "pairs": {
            "sample_file_path": (
                "outputs/eval/vpu_03S/joined/test_kmeans.ngen.ngen_simulation.joined.group0.parquet"
            ),
            "title": (
                "Paired data including the simulated and observed values for all locations and time steps."
            ),
        },
        "forecast_data": {
            "sample_file_path": (
                "outputs/eval/vpu_03S/test_kmeans/ngen_simulation/20121001T03-20121001T10.parquet"
            ),
            "title": (
                "Simulation data for a given NWM dataset (e.g., test_kmeans), "
                "including the simulated values for all locations and time steps. "
            ),
        },
        "obs_data": {
            "sample_file_path": "outputs/eval/vpu_03S/usgs/2012-10-01_2012-10-03.parquet",
            "title": (
                "Observation data including the observed values for all locations and time steps."
            ),
        },
    },
}


def initialize_s3_client():
    """Initialize and return an S3 client using credentials from environment variables."""
    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    aws_token = os.getenv("AWS_SESSION_TOKEN")

    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
        aws_session_token=aws_token,
    )


def read_description_file(desc_file: Path) -> pd.DataFrame:
    """Read a pipe-delimited data description CSV file."""
    return pd.read_csv(
        desc_file,
        delimiter="|",
        index_col=False,
        header=None,
        dtype=str,
    )


def get_sample_data_files(desc_dir: Path, base_prefix: str = "") -> dict[str, str]:
    """Return a mapping of dataset name to S3 sample-file key from description CSVs."""
    file_dict = {}

    for desc_file in sorted(desc_dir.glob("*.csv")):
        desc_df = read_description_file(desc_file)

        if "sample_file_path" not in desc_df[0].values:
            print(f"Warning: no sample_file_path found in description file {desc_file}")
            continue

        sample_path = desc_df.loc[desc_df[0] == "sample_file_path", 1].iloc[0].strip()

        if base_prefix:
            sample_path = f"{base_prefix.rstrip('/')}/{sample_path.lstrip('/')}"

        file_dict[desc_file.stem] = sample_path

    return file_dict


def make_anchor(title: str) -> str:
    """Convert title to a safe RST anchor ID."""
    anchor = title.strip().lower()
    anchor = re.sub(r"[^\w\-]+", "-", anchor)
    anchor = re.sub(r"-+", "-", anchor).strip("-")
    return anchor


def load_s3_file(
    s3_client,
    bucket: str,
    key: str,
    layer: str = "divides",
):
    """Load an S3 sample file, using the ``divides`` layer for GPKG/GDB files."""
    ext = Path(key).suffix.lower()

    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read()

    if ext == ".csv":
        return pd.read_csv(
            BytesIO(content),
            nrows=1000,
            dtype={
                "gage_id": str,
                "donor_gage_id": str,
                "receiver_gage_id": str,
            },
        )

    if ext == ".parquet":
        return pd.read_parquet(BytesIO(content), engine="pyarrow")

    if ext in {".gpkg", ".gdb"}:
        with tempfile.NamedTemporaryFile(suffix=ext) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()

            layers = fiona.listlayers(tmp_file.name)

            if layer not in layers:
                raise ValueError(f"{layer} layer not found in {key}")

            return gpd.read_file(
                tmp_file.name,
                layer=layer,
                rows=1000,
            )

    if ext in {".nc", ".nc4", ".cdf"}:
        with tempfile.NamedTemporaryFile(suffix=ext) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()

            with xr.open_dataset(tmp_file.name) as ds:
                return ds.load()

    raise ValueError(f"Unsupported file type: {ext} in S3 file {key}")


def extract_columns(
    s3_client,
    bucket: str,
    key: str,
) -> list[str]:
    """Extract column names from an S3 sample file."""
    data = load_s3_file(s3_client, bucket, key)

    if isinstance(data, xr.Dataset):
        return [str(name) for name in data.data_vars]

    return [str(column) for column in data.columns]


def get_netcdf_variable_descriptions(
    s3_client,
    bucket: str,
    key: str,
) -> dict[str, str]:
    """Extract NetCDF variable names and descriptions from an S3 file."""
    ds = load_s3_file(s3_client, bucket, key)

    descriptions = {}

    for name, variable in ds.variables.items():
        long_name = variable.attrs.get("long_name", "")
        units = variable.attrs.get("units", "")

        if not units:
            units = variable.encoding.get("units", "")

        if long_name and units:
            description = f"{long_name} ({units})"
        elif long_name:
            description = long_name
        elif units:
            description = f"({units})"
        else:
            description = ""

        descriptions[str(name)] = description

    return descriptions


def write_draft_description(
    output_dir: Path,
    dataset_name: str,
    sample_file_path: str,
    title: str,
    columns: list[str],
    descriptions: dict[str, str] | None = None,
):
    """Write a draft data description CSV file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{dataset_name}.csv"

    descriptions = descriptions or {}

    with output_file.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="|", lineterminator="\n")

        writer.writerow(["sample_file_path", sample_file_path])
        writer.writerow(["title", title])

        for column in columns:
            writer.writerow([column, descriptions.get(column, "")])

    print(f"Wrote draft description file: {output_file}")


def create_draft_data_desc_files(
    s3_client,
    bucket: str,
    prefix: str,
):
    """Create draft input and output data description CSV files from S3."""
    for data_type in ("inputs", "outputs"):
        print(
            f"\n============ Creating draft descriptions for {data_type} ============"
        )

        definitions = DATASET_DEFINITIONS[data_type]

        if not definitions:
            print(f"No {data_type} datasets are configured in DATASET_DEFINITIONS.")
            continue

        output_dir = DIR_DATA_DESC / data_type

        for dataset_name, metadata in definitions.items():
            output_file = output_dir / f"{dataset_name}.csv"
            if output_file.exists():
                print(f"Skipping existing description file: {output_file}")
                continue

            sample_file_path = metadata["sample_file_path"]
            title = metadata["title"]

            s3_key = "/".join(
                part.strip("/") for part in (prefix, sample_file_path) if part
            )

            print(f"Reading S3 sample file: s3://{bucket}/{s3_key}")

            try:
                if Path(s3_key).suffix.lower() in {".nc", ".nc4", ".cdf"}:
                    descriptions = get_netcdf_variable_descriptions(
                        s3_client,
                        bucket,
                        s3_key,
                    )
                    columns = list(descriptions)
                else:
                    columns = extract_columns(
                        s3_client,
                        bucket,
                        s3_key,
                    )
                    descriptions = {}
            except Exception as exc:
                print(f"ERROR reading s3://{bucket}/{s3_key}: {exc}")
                continue

            write_draft_description(
                output_dir,
                dataset_name,
                sample_file_path,
                title,
                columns,
                descriptions,
            )


def schema_to_rst(
    df: pd.DataFrame,
    title: str,
    desc_df: pd.DataFrame | None = None,
    preview_rows: int = 3,
) -> str:
    """Convert a pandas DataFrame schema to an RST list-table."""
    lines = []

    anchor = make_anchor(title)
    lines.append(f".. _{anchor}:")
    lines.append("")

    lines.append(title)
    lines.append("-" * len(title))
    lines.append("")

    description = ""

    if desc_df is not None and "title" in desc_df[0].values:
        description = str(desc_df.loc[desc_df[0] == "title", 1].iloc[0]).strip()

    if desc_df is not None and "sample_file_path" in desc_df[0].values:
        sample_path = str(
            desc_df.loc[desc_df[0] == "sample_file_path", 1].iloc[0]
        ).strip()
        description += f"\n\nSample file path: ``{sample_path}``"

    if description:
        lines.append(description)
        lines.append("")

    if "spatial_distance" in title:
        lines.append(
            ".. warning:: Schema table omitted for spatial_distance files "
            "due to large number of columns."
        )
        lines.append("")
        return "\n".join(lines)

    if not df.empty:
        preview_df = df.head(preview_rows)

        dropped_geom = False
        if "geometry" in preview_df.columns:
            preview_df = preview_df.drop(columns=["geometry"])
            dropped_geom = True

        if dropped_geom:
            lines.append(
                ".. note:: Geometry column omitted from preview table for brevity."
            )
            lines.append("")

        lines.append("**Example rows:**")
        lines.append("")
        lines.append(".. csv-table::")
        lines.append("   :header-rows: 1")
        lines.append("")

        lines.append("   " + ", ".join(f'"{column}"' for column in preview_df.columns))

        for _, row in preview_df.iterrows():
            lines.append("   " + ", ".join(f'"{value}"' for value in row.values))

        lines.append("")

    lines.append("**Schema:**")
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1\n")
    lines.append("   * - Column")
    lines.append("     - Description")
    lines.append("     - Type")

    for column, dtype in df.dtypes.items():
        if desc_df is not None and column in desc_df[0].values:
            col_desc = str(desc_df.loc[desc_df[0] == column, 1].iloc[0]).strip()
        else:
            col_desc = str(column)

        lines.append(f"   * - {column}\n     - {col_desc}\n     - {dtype}\n")

    lines.append("")
    return "\n".join(lines)


def get_netcdf_example_values(
    variable,
    n_values: int = 3,
) -> str:
    """Return the first few values of a NetCDF variable as a string."""
    values = variable.values.reshape(-1)[:n_values]

    formatted_values = []
    for value in values:
        if isinstance(value, bytes):
            value = value.decode(errors="replace")
        elif hasattr(value, "item"):
            value = value.item()

        formatted_values.append(str(value))

    return ", ".join(formatted_values)


def netcdf_to_rst(
    ds: xr.Dataset,
    title: str,
    desc_df: pd.DataFrame | None = None,
) -> str:
    """Convert an xarray Dataset schema to an RST table."""
    lines = []

    anchor = make_anchor(title)
    lines.append(f".. _{anchor}:")
    lines.append("")

    lines.append(title)
    lines.append("-" * len(title))
    lines.append("")

    description = ""

    if desc_df is not None and "title" in desc_df[0].values:
        description = str(desc_df.loc[desc_df[0] == "title", 1].iloc[0]).strip()

    if desc_df is not None and "sample_file_path" in desc_df[0].values:
        sample_path = str(
            desc_df.loc[desc_df[0] == "sample_file_path", 1].iloc[0]
        ).strip()
        description += f"\n\nSample file path: ``{sample_path}``"

    if description:
        lines.append(description)
        lines.append("")

    lines.append("**Schema:**")
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1\n")
    lines.append("   * - Variable")
    lines.append("     - Description")
    lines.append("     - Type")
    lines.append("     - Dimensions")
    lines.append("     - Example values")

    for name, variable in ds.variables.items():
        if desc_df is not None and name in desc_df[0].values:
            description = str(desc_df.loc[desc_df[0] == name, 1].iloc[0]).strip()
        else:
            description = name

        dimensions = ", ".join(variable.dims)
        dtype = variable.encoding.get("dtype", variable.dtype)

        lines.append(
            f"   * - {name}\n"
            f"     - {description}\n"
            f"     - {dtype}\n"
            f"     - {dimensions}\n"
            f"     - {get_netcdf_example_values(variable)}\n"
        )

    lines.append("")
    return "\n".join(lines)


def process_file(
    title: str,
    path: str,
    desc_df: pd.DataFrame | None,
    s3_client=None,
    bucket: str = "ngwpc-dev",
    layer: str = "divides",
) -> str:
    """Load a file and return an RST schema string."""
    df = pd.DataFrame()

    if "spatial_distance" in title:
        return schema_to_rst(df, title, desc_df=desc_df)

    ext = os.path.splitext(path)[1].lower().strip()

    try:
        if s3_client is None:
            if ext == ".csv":
                df = pd.read_csv(path, nrows=1000)
            elif ext == ".parquet":
                df = pd.read_parquet(path, engine="pyarrow")
            elif ext in {".gpkg", ".gdb"}:
                layers = fiona.listlayers(path)

                if layer not in layers:
                    raise ValueError(f"{layer} layer not found in {path}")

                df = gpd.read_file(path, layer=layer, rows=1000)
            elif ext in {".nc", ".nc4", ".cdf"}:
                with xr.open_dataset(path) as ds:
                    return netcdf_to_rst(
                        ds,
                        title,
                        desc_df=desc_df,
                    )
            else:
                print(
                    f"ERROR: Unsupported file type for schema extraction: "
                    f"{ext} in file {path}"
                )
                return ""

        else:
            if ext in {".nc", ".nc4", ".cdf"}:
                ds = load_s3_file(
                    s3_client,
                    bucket,
                    path,
                )
                return netcdf_to_rst(
                    ds,
                    title,
                    desc_df=desc_df,
                )

            df = load_s3_file(s3_client, bucket, path, layer=layer)

    except Exception as exc:
        print(f"ERROR reading {path}: {exc}")
        return ""

    return schema_to_rst(df, title, desc_df=desc_df)


def process_schema(
    file_dict: dict[str, str],
    desc_dir: Path,
    output_rst: Path,
    s3_client=None,
    bucket: str = "ngwpc-dev",
):
    """Generate an RST file containing schemas for the supplied files."""
    all_schemas = ["Schemas", "=======", ""]

    for dataset_name, sample_file_path in file_dict.items():
        desc_file = desc_dir / f"{dataset_name}.csv"

        if not desc_file.exists():
            print(f"Error: description file not found for {dataset_name}: {desc_file}")
            continue
        else:
            desc_df = read_description_file(desc_file)

        schema = process_file(
            dataset_name,
            sample_file_path,
            desc_df=desc_df,
            s3_client=s3_client,
            bucket=bucket,
        )

        if schema:
            all_schemas.append(schema)
            all_schemas.append("")

    all_schemas.append(".. toctree::\n   :maxdepth: 2")

    output_rst.parent.mkdir(parents=True, exist_ok=True)

    with output_rst.open("w") as f:
        f.write("\n".join(all_schemas))


def create_schemas(s3_client, bucket: str, prefix: str):
    """Generate input and output RST schema files."""
    input_files = get_sample_data_files(
        DIR_DATA_DESC / "inputs",
        base_prefix=prefix,
    )
    print("\n============ Creating schemas for input files ============")
    pprint(input_files)

    process_schema(
        dict(sorted(input_files.items())),
        DIR_DATA_DESC / "inputs",
        DIR_TECH_REFERENCE / "input_data.rst",
        s3_client=s3_client,
        bucket=bucket,
    )

    output_files = get_sample_data_files(
        DIR_DATA_DESC / "outputs",
        base_prefix=prefix,
    )
    print("\n============ Creating schemas for output files ============")
    pprint(output_files)

    process_schema(
        dict(sorted(output_files.items())),
        DIR_DATA_DESC / "outputs",
        DIR_TECH_REFERENCE / "output_data.rst",
        s3_client=s3_client,
        bucket=bucket,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create draft data description CSVs or generate RST data schemas "
            "from sample files stored on S3."
        )
    )

    parser.add_argument(
        "--step",
        choices=("draft", "schema"),
        default="schema",
        help=(
            "Workflow step to run: 'draft' creates the draft data description CSVs; "
            "'schema' generates RST schema files (default: schema)."
        ),
    )

    parser.add_argument(
        "--bucket",
        default="ngwpc-dev",
        help="S3 bucket name.",
    )

    parser.add_argument(
        "--prefix",
        default="nwm-tools-data/regionalization/data/",
        help="S3 prefix containing the sample files.",
    )

    args = parser.parse_args()

    s3_client = initialize_s3_client()

    if args.step == "draft":
        create_draft_data_desc_files(
            s3_client,
            bucket=args.bucket,
            prefix=args.prefix,
        )
    elif args.step == "schema":
        create_schemas(
            s3_client,
            bucket=args.bucket,
            prefix=args.prefix,
        )


if __name__ == "__main__":
    main()

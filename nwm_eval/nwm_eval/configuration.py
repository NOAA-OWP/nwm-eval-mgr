"""Data models for configuration sections in the yaml file, defined with Pydantic for validation and documentation."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator

from .utils import check_options

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
)


class LocationFilter(BaseModel):
    """Data model for filtering locations based on column values in the crosswalk file."""

    columns: str | list[str] | None = Field(
        description="Column name(s) in the crosswalk file to filter on. Can be a single string or a list of strings.",
        examples=["vpu_id", "status"],
        default=None,
    )

    values: str | list[str] | None = Field(
        description="Value(s) to filter on for the corresponding columns. Can be a single string or a list of strings.",
        examples=["03S", "USGS-active"],
        default=None,
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_and_validate(cls, data):
        """Normalize columns/values to lists and ensure they have matching lengths.

        This allows configs to specify either a single string or a list for each field,
        while guaranteeing that downstream code always receives lists of equal length.
        """
        if data is None:
            return data

        # If another validator has already constructed a LocationFilter instance, just return it unchanged.
        if isinstance(data, cls):
            return data

        if not isinstance(data, dict):
            return data

        columns = data.get("columns")
        values = data.get("values")

        # If either field is missing, let Pydantic's own validation handle it.
        if columns is None or values is None:
            return data

        # Normalize columns to a list of strings.
        if isinstance(columns, str):
            columns_list = [columns]
        else:
            columns_list = list(columns)

        # Normalize values to a list of strings.
        if isinstance(values, str):
            values_list = [values]
        else:
            values_list = list(values)

        # Ensure columns and values lists have the same length.
        if len(columns_list) != len(values_list):
            raise ValueError(
                "LocationFilter configuration error: 'columns' and 'values' must have the same length."
            )

        data["columns"] = columns_list
        data["values"] = values_list

        return data


class GeneralConfig(BaseModel):
    """Data model for the 'general' section of the config file."""

    steps: dict[str, bool] = Field(
        description=(
            "Dictionary specifying which steps to run. Keys are step names (e.g., 'fetch_fcst_data', 'fetch_obs_data', "
            "'pair_data', 'compute_metrics', 'plot_metrics'), and values are booleans indicating whether to run the step."
            "Note that these steps need to run in order, since some steps depend on the output of previous steps "
            "(e.g., one cannot compute metrics without first fetching data and pairing it)."
        ),
        json_schema_extra={
            "description_short": "Steps to run in the evaluation process."
        },
        examples={
            "fetch_fcst_data": True,
            "fetch_obs_data": True,
            "pair_data": True,
            "compute_metrics": True,
            "plot_metrics": True,
        },
        default_factory=lambda: {
            "fetch_fcst_data": True,
            "fetch_obs_data": True,
            "pair_data": True,
            "compute_metrics": True,
            "plot_metrics": True,
        },
    )

    domain: Literal["conus", "hi", "ak", "prvi"] | None = Field(
        default=None,
        examples=["conus"],
        description="Domain for the evaluation. Valid options are 'conus', 'hi', 'ak', 'prvi' (case insensitive).",
    )

    assemble_domain: bool | None = Field(
        default=None,
        examples=[False, True],
        description=(
            "Whether to assemble results from different VPUs across domains. This is only applicable when domain is 'conus', "
            "since the CONUS domain is currently divided into VPUs while other domains are not. If True, "
            "the script will look for metric files from each VPU, concatenate them, and save the assembled metric file "
            "for the entire CONUS domain."
        ),
        json_schema_extra={
            "description_short": "Whether to assemble results across VPUs for the CONUS domain."
        },
    )

    location_set_name: str = Field(
        description=(
            "User-specified name for the set of locations (e.g., a specific VPU or a cluster from a "
            "regionalization). This will be used in naming output files and directories."
        ),
        json_schema_extra={
            "description_short": "Name for the set of locations to evaluate."
        },
        examples=["vpu_03S", "usgs_01123000"],
        default="usgs_01123000",
    )

    location_list: list[str] | None = Field(
        default=None,
        examples=[["01123000", "01123500"], ["50070900"]],
        description="List of specific locations to include in the evaluation. If None, all locations in the crosswalk file will be used.",
    )

    location_type: Literal["usgs_gage", "nwm30_link", "nwm22_link"] = Field(
        default="usgs_gage",
        examples=["usgs_gage", "nwm30_link", "nwm22_link"],
        description=(
            "Type of locations to evaluate. Valid options are 'usgs_gage', 'nwm30_link', and 'nwm22_link'. This will "
            "determine which columns in the crosswalk file to use for filtering locations and for merging forecast and observation data."
        ),
        json_schema_extra={
            "description_short": "Type of locations to evaluate, which determines how locations are identified and processed."
        },
    )

    location_filter: LocationFilter | None = Field(
        default=None,
        examples={
            "columns": ["vpu_id", "status"],
            "values": ["03S", "USGS-active"],
        },
        description=(
            "Optional configuration for filtering locations based on column values in the crosswalk file. "
            "If provided, only locations that match the specified column-value pairs will be included in the evaluation."
        ),
        json_schema_extra={
            "description_short": "Configuration for filtering locations based on column values."
        },
    )

    location_group_size: int | None = Field(
        default=200,
        examples=[100, 200, 500],
        description=(
            "Number of locations to process in each group when pairing forecast and observation data. "
            "This is used to manage memory usage during the pairing step. If None, all locations will be processed "
            "in a single group."
        ),
        json_schema_extra={
            "description_short": "Number of locations to process in each group when pairing forecast and observation data."
        },
    )

    variable_name: str = Field(
        default="streamflow",
        examples=["streamflow"],
        description=(
            "Name of the variable to evaluate. Currently only 'streamflow' is supported, "
            "but this field is included for future extensibility."
        ),
    )

    nwm_configuration: str = Field(
        description=(
            "Name of the NWM configuration to evaluate. This can be 'ngen' for ngen-based simulations or match one of "
            "the configurations defined in the forecast configuration file specified by 'file_paths.fcst_config_file'."
        ),
        json_schema_extra={"description_short": "NWM configuration to evaluate."},
        examples=[
            "ngen",
            "short_range",
            "medium_range_blend",
            "standard_ana_puertorico",
        ],
    )

    dataset_name: list[str] = Field(
        description=(
            "User-specified name(s) for the dataset(s) to evaluate (e.g., formulation name or regionalization algorithm). "
            "This will be used in naming output files and directories. If evaluating multiple datasets, this should be "
            "a list of names with the same length as 'nwm_version', 'forecast_start_date', and 'forecast_end_date'."
        ),
        json_schema_extra={
            "description_short": "User-specified name(s) for the dataset(s) to evaluate."
        },
        examples=[["noah_cfes", "noah_topmodel"], ["gower"]],
    )

    nwm_version: list[str] = Field(
        description=(
            "List of NWM versions to evaluate. Valid options include 'ngen', 'nwm30', 'nwm22', etc. This should be "
            "a list of the same length as 'dataset_name', where each entry corresponds to the NWM version for the "
            "dataset with the same index in 'dataset_name'."
        ),
        json_schema_extra={"description_short": "NWM version(s) to evaluate."},
        examples=[["ngen", "nwm30"], ["ngen"]],
    )

    forecast_start_date: list[str] = Field(
        description=(
            "List of start dates for the forecast data to evaluate. This should be a list of the same length as 'dataset_name', "
            "where each entry corresponds to the start date for the dataset with the same index in 'dataset_name'"
        ),
        json_schema_extra={
            "description_short": "Start date(s) for the forecast data to evaluate."
        },
        examples=[
            ["2022-12-01 00:00:00", "2022-12-15 00:00:00"],
            ["2022-12-01 00:00:00"],
        ],
    )

    forecast_end_date: list[str] = Field(
        description=(
            "List of end dates for the forecast data to evaluate. This should be a list of the same length as 'dataset_name', "
            "where each entry corresponds to the end date for the dataset with the same index in 'dataset_name'"
        ),
        json_schema_extra={
            "description_short": "End date(s) for the forecast data to evaluate."
        },
        examples=[
            ["2022-12-31 00:00:00", "2023-01-15 00:00:00"],
            ["2022-12-31 00:00:00"],
        ],
    )

    eval_start_date: list[str] | None = Field(
        default=None,
        description=(
            "List of start dates for the evaluation period. This should be a list of the same length as 'dataset_name', "
            "where each entry corresponds to the start date for the evaluation period of the dataset with the same index "
            "in 'dataset_name'. If not provided, the evaluation will start from the earliest available date in the paired "
            "forecast and observation data for each dataset."
        ),
        json_schema_extra={
            "description_short": "Start date(s) for the evaluation period."
        },
        examples=[
            ["2022-12-11 00:00:00", "2022-12-25 00:00:00"],
            ["2022-12-11 00:00:00"],
        ],
    )

    eval_end_date: list[str] | None = Field(
        default=None,
        description=(
            "List of end dates for the evaluation period. This should be a list of the same length as 'dataset_name', "
            "where each entry corresponds to the end date for the evaluation period of the dataset with the same index "
            "in 'dataset_name'. If not provided, the evaluation will end at the latest available date in the paired "
            "forecast and observation data for each dataset."
        ),
        json_schema_extra={
            "description_short": "End date(s) for the evaluation period."
        },
        examples=[
            ["2022-12-31 00:00:00", "2023-01-15 00:00:00"],
            ["2022-12-31 00:00:00"],
        ],
    )

    separate_calibrated: bool | None = Field(
        default=None,
        examples=[False, True],
        description="Whether to distinguish calibrated and regionalized locations in the evaluation",
    )

    log_level: str = Field(
        description="Logging level. Valid options (case insensitive): debug, info, warning, error, critical, severe, fatal",
        examples=["debug", "info", "warning", "error", "critical", "severe", "fatal"],
        default="info",
    )

    @field_validator("domain", mode="before")
    @classmethod
    def normalize_domain(cls, v):
        """Normalize domain string to lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    @model_validator(mode="after")
    def check_log_level(self):
        """Ensure that the log level is valid."""
        # valid log levels for logging module (case insensitive)
        valid_levels = [
            "DEBUG",
            "INFO",
            "WARNING",
            "SEVERE",  # maps to ERROR
            "FATAL",  # maps to CRITICAL
            "CRITICAL",
            "ERROR",
        ]
        check_options(self.log_level.upper(), valid_levels, "log level")
        return self


class FilePathsConfig(BaseModel):
    """Data model for the 'file_paths' section of the config file."""

    base_dir: Path = Field(
        description=(
            "Root directory to store data and outputs for the evaluation. The script will create subdirectories under "
            "this base directory for different datasets and types of outputs (e.g., noah_cfes, usgs, joined, metrics, plots)."
        ),
        json_schema_extra={
            "description_short": "Root directory for storing data and outputs."
        },
        examples=["~/ngen_evaluation/"],
    )

    location_list_file: Path | str | None = Field(
        default=None,
        examples=[Path("~/location_list.csv")],
        description=(
            "Path to a file containing the list of locations to evaluate, only used if 'general.location_list' is not provided. "
            "If neither is provided, locations from the crosswalk file will be used, filtered by 'general.location_filter'."
        ),
        json_schema_extra={
            "description_short": "Path to a file containing the list of locations to evaluate"
        },
    )

    crosswalk_file: Path | str | dict[str, Path] | dict[str, str] = Field(
        examples=[
            Path("~/crosswalk.csv"),
            {
                "ngen": Path("~/crosswalk_ngen.csv"),
                "nwm30": Path("~/crosswalk_nwm30.csv"),
            },
        ],
        description=(
            "Path to a crosswalk file or a dictionary of crosswalk files, corresponding to different nwm versions. "
            "The crosswalk file maps location identifiers to other relevant information."
        ),
        json_schema_extra={
            "description_short": "Path to a crosswalk file or a dictionary of crosswalk files."
        },
    )

    fcst_config_file: str | Path | None = Field(
        default=None,
        examples=["data/inputs/nwm_forecast_configuration.yaml"],
        description=(
            "Path to the forecast configuration file. This file defines the parameters for different NWM configurations. "
            "For each forecast configuration, a list that specify the following parameters (in order): "
            "cycle_start: start time of forecast cycles in Zulu time or UTC (e.g., 0Z);"
            "cycle_end: end time of forecast cycles in Zulu time or UTC (e.g., 23Z);"
            "cycle_freq: frequency of forecast cycles in hours (e.g., 1);"
            "fcst_win: forecast window in hours (e.g., 18);"
            "fcst_timestep: forecast timestep in hours (e.g., 1);"
        ),
        json_schema_extra={
            "description_short": "Path to the forecast configuration file defining parameters for different NWM configurations."
        },
    )

    fcst_data_file: Path | str | dict[str, Path] | dict[str, str] | None = Field(
        default=None,
        examples=["01123000_output.csv"],
        description="Path to the forecast data file or a dictionary of forecast data files.",
    )

    fcst_data_dir: Path | str | dict[str, Path] | dict[str, str] | None = Field(
        default=None,
        examples=["data/inputs/hindcasts/"],
        description="Path to the directory containing forecast data files or a dictionary of directories.",
    )

    obs_data_file: Path | str | None = Field(
        default=None,
        examples=["data/inputs/obs/01123000_hourly_discharge.csv"],
        description=(
            "Path to the observation data file. Both obs_data_file and obs_data_dir can be specified. "
            "The run will read all .csv and .parquet files in obs_data_dir and obs_data_file and remove duplicates."
            "If neither obs_data_file nor obs_data_dir is provided, an observation data source must be specified in "
            "the 'flow_observation.usgs' section."
        ),
    )

    obs_data_dir: Path | str | None = Field(
        default=None,
        examples=["data/inputs/obs/"],
        description=(
            "Path to the observation data directory where one or more observation data files are stored. "
            "The run will look for all .csv and .parquet files in this directory. "
            "Each file can contain observation data for a single location (with the filename starting with the location "
            "identifier), or multiple locations with a 'location_id' column specifying the location identifiers."
        ),
    )

    calib_param_file: Path | str | None = Field(
        default=None,
        examples=["data/inputs/calib_params.csv"],
        description="Path to the calibration parameter file.",
    )

    txdot_gage_file: Path | str | None = Field(
        default=None,
        examples=["data/inputs/gage_files/tx_gauges.csv"],
        description="Path to the TxDOT gage file. This is only needed if evaluating TxDOT locations, for which streamflow "
        "observations are retrieved differently than USGS gages. If not provided, the default TxDOT list defined in settings.py will be used. ",
        json_schema_extra={"description_short": "Path to the TxDOT gage file."},
    )

    output_dir: str | Path = Field(
        description=(
            "Directory to save outputs such as paired data, computed metrics, and plots. "
        ),
        examples=["ngen_evaluation/outputs/usgs_01123000/"],
    )

    log_file: str | Path | None = Field(
        default=None,
        description="Path to log file. Default: verification.log in {output_dir}",
        examples=["outputs/usgs_01123000/verification.log"],
    )


class NWMForecastConfig(BaseModel):
    """Data model for the 'nwm_forecast' section of the config file."""

    data_source: Literal["ngenCERF", "ngenSIM", "hindcast", "GCS"] = Field(
        description=(
            "Data source for the NWM forecast. This specifies the source from which forecast data will be retrieved."
            "Valid options are: "
            "'ngenCERF' for ngen-based single-location forecasts for a single reference time (T0), "
            "'hindcast' for ngen-based single-location hindcast data for multiple reference times (T0), "
            "'ngenSIM' for large-scale ngen-based simulations (e.g., across a VPU from regionalization), "
            "'GCS' for large-scale operational NWM forecasts on Google Cloud Storage."
        ),
        json_schema_extra={
            "description_short": "Data source for the NWM forecast. Valid options include 'ngenCERF', 'ngenSIM', 'hindcast', and 'GCS'."
        },
        examples=["ngenCERF", "ngenSIM", "hindcast", "GCS"],
    )

    fetch_fcst: list[bool] | None = Field(
        default=[True],
        examples=[[True], [True, False]],
        description=(
            "List of booleans indicating whether to fetch forecast data for each dataset. "
            "If False, forecast data will be retrieved regardless of whether it already exists locally. "
            "Otherwise, skip fetching if forecast data file already exists locally. "
        ),
        json_schema_extra={
            "description_short": "Whether to fetch forecast data for each dataset, with local file existence check."
        },
    )

    output_type: str | None = Field(
        default="channel_rt",
        examples=["channel_rt", "land", "terrain_rt"],
        description=(
            "Type of NWM output to retrieve. Currently only 'channel_rt' is supported. Only applicable when data_source='GCS'. "
        ),
    )

    t_minus: list[int] | None = Field(
        default=[0, 1, 2],
        examples=[[0], [0, 1, 2]],
        description=(
            "List of integers indicating the T-minus hours for which to retrieve NWM forecasts. "
            "Only applicable when data_source='GCS' and nwm_configuration is an AnA run (analysis & assimilation)."
        ),
        json_schema_extra={
            "description_short": "T-minus hours for which to retrieve NWM forecasts, only applicable for AnA runs on GCS."
        },
    )

    kerchunk_method: str | None = Field(
        default="local",
        examples=["local", "remote", "auto"],
        description=(
            "Specifies the preference in creating Kerchunk reference json files. Only needed for data_source = 'GCS'. "
            "'local' - always create new json files from netcdf files in GCS and save locally, if they do not already exist; "
            "'remote' - read the CIROH pre-generated jsons from s3, ignoring any that are unavailable; "
            "'auto' - read the CIROH pre-generated jsons from s3, and create any that are unavailable, storing locally"
        ),
        json_schema_extra={
            "description_short": "Preference for creating Kerchunk reference json files, only applicable for GCS data source."
        },
    )
    process_by_z_hour: bool | None = Field(
        default=True,
        examples=[False, True],
        description=(
            "Only applicable when data_source='GCS'. If True, NWM files will be processed by z-hour per day. "
            "If False, files will be processed in chunks (defined by STEPSIZE). This can help if you want to read many reaches "
            "at once (all ~2.7 million for medium range for example)."
        ),
        json_schema_extra={
            "description_short": "Whether to process NWM files by z-hour per day, only applicable for GCS data source."
        },
    )

    stepsize: int | None = Field(
        default=100,
        examples=[50, 100, 200],
        description=(
            "Only applicable when data_source='GCS' and process_by_z_hour=False. Controls how many files are processed "
            "in memory at once. Higher values can increase performance at the expense on memory. "
        ),
        json_schema_extra={
            "description_short": "Number of files to process in memory at once when processing GCS data without z-hour chunking."
        },
    )

    ignore_missing_file: bool | None = Field(
        default=True,
        examples=[False, True],
        description=(
            "Only applicable when data_source='GCS'. If True, the missing file(s) will be skipped and the process will resume. "
            "If False, TEEHR will fail if a missing NWM file is encountered."
        ),
        json_schema_extra={
            "description_short": "Whether to ignore missing NWM files and continue processing, only applicable for GCS data source."
        },
    )

    overwrite_output: bool | None = Field(
        default=False,
        examples=[False, True],
        description=(
            "Whether to overwrite existing forecast data files. If False, the script will check if the forecast "
            "data file already exists locally before attempting to fetch it. If True, the script will fetch "
            "the forecast data and overwrite any existing local file with the same name."
        ),
        json_schema_extra={
            "description_short": "Whether to overwrite existing forecast data files."
        },
    )

    memory_per_worker_gb: int | None = Field(
        default=3,
        examples=[1, 2, 3, 4],
        description="Configurable memory (in GB) assigned to each worker or process.",
    )


class USGSConfig(BaseModel):
    """Configuration for USGS flow observations."""

    chunk_by: Literal["day", "month", "year"] = Field(
        default="month",
        description="How downloaded data are chunked into parquet files.",
    )

    overwrite_output: bool | None = Field(
        default=True,
        description=(
            "If True, existing output files are overwritten. "
            "If False, existing files are retained."
        ),
    )

    memory_per_worker_gb: int | None = Field(
        default=3,
        ge=1,
        description="Memory assigned to each worker in GB.",
    )


class FlowObservationConfig(BaseModel):
    """Data model for the flow_observation section."""

    usgs: USGSConfig | None = Field(
        default=None,
        description=(
            "Configuration for USGS flow observations. "
            "If omitted, obs_data_file and/or obs_data_dir must be provided in file_paths section, "
        ),
    )


class PairDataConfig(BaseModel):
    """Data model for the 'pair_data' section of the config file."""

    overwrite: bool | None = Field(
        default=True,
        examples=[False, True],
        description=(
            "Whether to overwrite existing paired data files. If False, the script will check if the paired data file "
            "already exists locally before attempting to pair data. If True, the script will pair the data and overwrite "
            "any existing local file with the same name."
        ),
        json_schema_extra={
            "description_short": "Whether to overwrite existing paired data files."
        },
    )
    group_size: int | None = Field(
        default=200,
        examples=[100, 200, 500],
        description=(
            "Number of locations to process in each group when pairing forecast and observation data. This is used to "
            "manage memory usage during the pairing step. If None, all locations will be processed in a single group."
        ),
        json_schema_extra={
            "description_short": "Number of locations to process in each group when pairing forecast and observation data."
        },
    )


class LeadTimesMixin(BaseModel):
    """Mixin class to add lead_times field and validation to metric and plot configs."""

    lead_times: list[str] | None = Field(
        default=None,
        examples=[
            ["all", "1-5", "5-10", "10-15", "all_aggregated"],
        ],
        description=(
            "List of lead times to compute metrics or make plots for. Each lead time can be specified as an integer "
            "(e.g., 6), a numeric string (e.g., '6'), or a range string (e.g., '1-6'). "
            "`all` represents all available individual lead times for a given nwm configuration. "
            "Range strings will be expanded to include all individual lead times within the range. "
            "`all_aggregated` represents a range that includes all lead times for a given nwm configuration, "
            "(e.g., 1-18 for short_range)."
            "Note lead times defined in `plots` must be a subset of those defined in `metrics`."
        ),
        json_schema_extra={
            "description_short": "Lead times to include in the evaluation."
        },
    )

    @field_validator("lead_times", mode="before")
    @classmethod
    def normalize_lead_times(cls, v):
        """Normalize lead_times to a list of strings, and validate that each entry is either an integer, a numeric string, or a range string."""
        if v is None:
            return []
        if not isinstance(v, list):
            v = [v]
        return [str(lt) for lt in v]


class ReferenceTimesMixin(BaseModel):
    """Mixin class to add reference_times field and validation to metric and plot configs."""

    reference_times: list[datetime] | None = Field(
        default=None,
        examples=[["2022-12-01 00:00:00", "2022-12-15 00:00:00"]],
        description=(
            "List of reference times (T0s) to compute metrics or make plots for. Each reference time can be specified "
            "as a datetime object or a string in a format recognized by pandas.to_datetime."
        ),
        json_schema_extra={
            "description_short": "Reference times (T0s) to include in the evaluation."
        },
    )

    @field_validator("reference_times", mode="before")
    @classmethod
    def normalize_reference_times(cls, v):
        """Normalize reference_times to a list of datetime objects."""
        if v is None:
            return []
        if not isinstance(v, list):
            v = [v]
        return [pd.to_datetime(rt).to_pydatetime() for rt in v]


class MetricsConfig(LeadTimesMixin):
    """Data model for the 'metrics' section of the config file."""

    overwrite: bool | None = Field(
        default=True,
        examples=[False, True],
        description=("Whether to overwrite existing metric files. "),
    )

    library: str | None = Field(
        default="nwm.eval",
        examples=["nwm.eval", "teehr"],
        description=(
            "Library to use for metric computation. Valid options: nwm.eval, teehr. "
        ),
    )

    metric_subset: str | list[str] = Field(
        examples=["all", ["NSE", "KGE"]],
        description=(
            "Subset of metrics to compute. Can be 'all' or a list of metric names. If 'all', all available metrics in "
            "the specified library will be computed. If a list of metric names is provided, only those metrics will be computed."
        ),
        json_schema_extra={
            "description_short": "Subset of metrics to compute, either 'all' or a list of metric names."
        },
    )

    metric_exclude: list[str] | None = Field(
        default=None,
        examples=[["HSEG_FDC", "MSEG_FDC", "LSEG_FDC"], ["NSE"]],
        description=(
            "List of metric names to exclude from metric_subset for computation. "
        ),
    )

    threshold_categorical: dict[str, float | str] | None = Field(
        default={"value": 0.9, "type": "quantile"},
        examples=[
            {"value": 0.9, "type": "quantile"},
            {"value": 10.0, "type": "absolute"},
        ],
        description=(
            "Threshold for categorical metrics. Valid options for type are 'quantile' and 'absolute'. "
            "If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. "
            "If 'absolute', the threshold will be the specified absolute flow value."
        ),
    )

    threshold_event: dict[str, float | str] | None = Field(
        default={"value": 0.9, "type": "quantile"},
        examples=[
            {"value": 0.9, "type": "quantile"},
            {"value": 10.0, "type": "absolute"},
        ],
        description=(
            "Threshold for event-based metrics. Valid options for type are 'quantile' and 'absolute'. "
            "If 'quantile', the threshold will be determined as the specified quantile of the observed flow values. "
            "If 'absolute', the threshold will be the specified absolute flow value."
        ),
    )

    file_format: str | None = Field(
        default="parquet",
        examples=["parquet", "csv"],
        description="File format for output files. Valid options are 'parquet' and 'csv'.",
    )


Number = int | float


class BasePlotConfig(LeadTimesMixin):
    """Common fields for all plot configs."""

    plot: bool | None = Field(
        default=False,
        examples=[False, True],
        description=(
            "Whether to generate this type of plot. If False, the script will skip generating this type of plot. "
            "If True, the script will generate this type of plot for the specified lead times."
        ),
        json_schema_extra={
            "description_short": "Whether to generate this type of plot."
        },
    )

    metric_subset: str | list[str] | None = Field(
        default=None,
        examples=[["NSE", "KGE"], "all"],
        description=(
            "List of metric names to include in the plots. If not defined, all available metrics will be included in the plots. "
        ),
        json_schema_extra={
            "description_short": "List of metric names to include in the plots."
        },
    )

    tag: str | None = Field(
        default="",
        description=(
            "Optional tag to include in the plot titles and filenames. This can be used to distinguish "
            "different configurations in the plot outputs."
        ),
        json_schema_extra={
            "description_short": "Optional tag to include in plot titles and filenames."
        },
    )


class HistogramConfig(BasePlotConfig):
    """Config for histogram plots."""

    binning: dict[str, list[Number]] | None = Field(
        default={
            "NSE": [-1, -0.5, 0, 0.5, 1],
            "KGE": [-1, -0.5, 0, 0.5, 1],
        },
        examples=[
            {
                "NSE": [-1, -0.5, 0, 0.5, 1],
                "KGE": [-1, -0.5, 0, 0.5, 1],
            }
        ],
        description=(
            "Dictionary specifying the binning for histogram plots. Keys are metric names, and values are lists of "
            "numbers defining the bin edges for the corresponding metric. If a metric is not included in this dictionary, "
            "binning is determined by dividing the range of metric values into 8 equal-width bins. "
        ),
        json_schema_extra={
            "description_short": "Dictionary specifying the binning for histogram plots, with metric names as keys and lists of bin edges as values."
        },
    )


class BoxPlotConfig(BasePlotConfig):
    """Config for box plots."""

    show_outliers: bool | None = Field(
        default=False,
        examples=[False, True],
        description=(
            "Whether to show outliers in box plots. If True, outliers will be shown as individual points. If False, "
            "outliers will be omitted."
        ),
    )


class SpatialMapConfig(BasePlotConfig):
    """Config for spatial maps."""

    scaling: dict[str, list[Number]] | None = Field(
        default={
            "NSE": [-0.5, 1.0],
            "KGE": [-0.5, 1.0],
        },
        examples=[
            {
                "NSE": [-0.5, 1.0],
                "KGE": [-0.5, 1.0],
            }
        ],
        description=(
            "Dictionary specifying the scaling for spatial maps. Keys are metric names, and values are lists of "
            "numbers defining the scaling range for the corresponding metric. If a metric is not included in this dictionary, "
            "metric data will not be scaled and hence the resulting spatial map may be difficult to interpret if there are extreme outliers."
        ),
        json_schema_extra={
            "description_short": "Dictionary specifying the scaling for spatial maps, with metric names as keys and lists of scaling ranges as values."
        },
    )


class TimeSeriesConfig(BasePlotConfig, ReferenceTimesMixin):
    """Config for time series plots."""

    lead_times: list[int] | None = Field(
        default=None,
        examples=[[1, 2, 3], [6, 12, 24]],
        description=(
            "List of lead times for time series plots. "
            "Each lead time should be a number representing "
            "the forecast lead time in hours."
        ),
    )

    @field_validator("lead_times", mode="before")
    @classmethod
    def validate_lead_times(cls, v):
        """Validate that lead_times is a list of numbers or numeric strings, and convert to integers."""
        if v is None:
            return None

        if not isinstance(v, list):
            raise ValueError("lead_times must be a list")

        cleaned = []

        for item in v:
            # Accept int/float directly
            if isinstance(item, (int, float)):
                cleaned.append(int(item))

            # Accept numeric strings like "6" or "6.5"
            elif isinstance(item, str):
                try:
                    cleaned.append(int(float(item)))

                except ValueError:
                    logger.info(
                        f"Invalid lead_time '{item}'. "
                        "Must be numeric (e.g., '6'), "
                        "not ranges like '1-5'. "
                        "Skip this lead time."
                    )

            else:
                logger.info(
                    f"Invalid type {type(item)} in lead_times. "
                    "Must be numeric or numeric string. "
                    "Skip this lead time."
                )

        return cleaned or None


class TablePlotConfig(BasePlotConfig):
    """Config for table plots displaying metric values."""

    pass


class BarChartConfig(BasePlotConfig):
    """Config for bar charts."""

    pass


class PlotsConfig(BaseModel):
    """Data model for the 'plots' section of the config file."""

    histogram: HistogramConfig = Field(
        default_factory=HistogramConfig,
        description="Configuration for histogram plots.",
    )

    boxplot: BoxPlotConfig = Field(
        default_factory=BoxPlotConfig,
        description="Configuration for box plot.",
    )
    spatial_map: SpatialMapConfig = Field(
        default_factory=SpatialMapConfig,
        description="Configuration for spatial map plots.",
    )
    time_series: TimeSeriesConfig = Field(
        default_factory=TimeSeriesConfig,
        description="Configuration for time series plots.",
    )
    metric_table: TablePlotConfig = Field(
        default_factory=TablePlotConfig,
        description="Configuration for metric table plots.",
    )
    barchart: BarChartConfig = Field(
        default_factory=BarChartConfig,
        description="Configuration for bar chart plots.",
    )


class Config(BaseModel):
    """Define a data model for each section in the config file."""

    general: GeneralConfig = Field(
        default_factory=GeneralConfig,
        description="General configuration for the evaluation, including dataset information and evaluation settings.",
    )
    file_paths: FilePathsConfig = Field(
        default_factory=FilePathsConfig,
        description="Configuration for file paths used in the evaluation, including input data and output directories.",
    )
    nwm_forecast: NWMForecastConfig = Field(
        default_factory=NWMForecastConfig,
        description="Configuration for NWM forecast data.",
    )
    flow_observation: FlowObservationConfig = Field(
        default_factory=FlowObservationConfig,
        description="Configuration for flow observation data.",
    )
    pair_data: PairDataConfig = Field(
        default_factory=PairDataConfig,
        description="Configuration for paired data.",
    )
    metrics: MetricsConfig = Field(
        default_factory=MetricsConfig,
        description="Configuration for metrics.",
    )
    plots: PlotsConfig = Field(
        default_factory=PlotsConfig,
        description="Configuration for plots.",
    )

    @field_validator("flow_observation", mode="before")
    @classmethod
    def default_flow_observation(cls, v):
        """Provide a default empty configuration for flow_observation if it is not provided in the config file."""
        if v is None:
            return {}
        return v

    @model_validator(mode="after")
    def check_dataset_configuration(self):
        """Check that the following fields has the same length as dataset_name.

        Fields include: nwm_version, forecast_start_date, forecast_end_date, eval_start_date, eval_end_date.
        """
        dataset_name = self.general.dataset_name
        nwm_version = self.general.nwm_version
        forecast_start_date = self.general.forecast_start_date
        forecast_end_date = self.general.forecast_end_date
        eval_start_date = self.general.eval_start_date
        eval_end_date = self.general.eval_end_date

        fields_to_check = {
            "nwm_version": nwm_version,
            "forecast_start_date": forecast_start_date,
            "forecast_end_date": forecast_end_date,
            "eval_start_date": eval_start_date,
            "eval_end_date": eval_end_date,
        }

        for field_name, field_value in fields_to_check.items():
            if field_value and len(field_value) != len(dataset_name):
                msg = f"Length of '{field_name} ({len(field_value)})' does not match length of 'dataset_name' ({len(dataset_name)})."
                logger.error(msg)
                raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def check_forecast_data_file(self):
        """Make sure forecast data file and/or directory is provided except for GCS."""
        if (
            self.nwm_forecast.data_source.upper() != "GCS"
            and self.file_paths.fcst_data_file is None
            and self.file_paths.fcst_data_dir is None
        ):
            msg = "file_paths.fcst_data_file or file_paths.fcst_data_dir must be provided when "
            msg += "nwm_forecast.data_source is not 'GCS'"
            logger.error(msg)
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_obs_source(self):
        """Check that at least one observation data source is provided (USGS or obs_data_file)."""
        has_usgs = self.flow_observation.usgs is not None
        has_obs_file = self.file_paths.obs_data_file is not None
        has_obs_dir = self.file_paths.obs_data_dir is not None

        if not has_usgs and not has_obs_file and not has_obs_dir:
            msg = "Either 'flow_observation.usgs', 'file_paths.obs_data_file', or 'file_paths.obs_data_dir' must be provided."
            logger.error(msg)
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def check_plot_config(self):
        """Check that plot configurations are compatible with the specified data source.

        Time series, metric_table, and barchart plots are only applicable if nwm_forecast.data_source is ngenCERF or hindcast.
        Spatial maps, histograms, and boxplots are only applicable if nwm_forecast.data_source is GCS or ngenSIM.
        """
        for plot_type in ["time_series", "metric_table", "barchart"]:
            plot_conf = getattr(self.plots, plot_type, None)
            if (
                plot_conf
                and getattr(plot_conf, "plot", False)
                and self.nwm_forecast.data_source.lower()
                not in [
                    "ngencerf",
                    "hindcast",
                ]
            ):
                msg = f"{plot_type} is only applicable if nwm_forecast.data_source is 'ngenCERF' or 'hindcast'"
                logger.error(msg)
                raise ValueError(msg)

        for plot_type in ["spatial_map", "histogram", "boxplot"]:
            plot_conf = getattr(self.plots, plot_type, None)
            if (
                plot_conf
                and getattr(plot_conf, "plot", False)
                and self.nwm_forecast.data_source.lower()
                not in [
                    "gcs",
                    "ngensim",
                ]
            ):
                msg = f"{plot_type} is only applicable if nwm_forecast.data_source is 'GCS' or 'ngenSIM'"
                logger.error(msg)
                raise ValueError(msg)
        return self
